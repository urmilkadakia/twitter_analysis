import tweepy
import json
import api_keys
import csv
import time
import zipfile
import os
from util import flatten_json, get_user_profile_dict

KEY_LIST = ['id', 'id_str', 'name', 'screen_name', 'location', 'description', "followers_count", 'friends_count',
            'statuses_count', 'created_at']


class TwitterScraper:
    """
    Twitter_Scraper class contains the logic to scrape the given userId list and store it in the format of either
    json or csv.
    """
    def __init__(self, input_file, output_file):
        """
        Method to initialized the class data members
        :param input_file: User input for path to the input file
        :param output_file: User input for path to the output folder

        api: Data member in the form of tweepy OAuthHandler object

        """

        auth = tweepy.OAuthHandler(api_keys.api_key, api_keys.api_secret_key)
        auth.set_access_token(api_keys.access_token, api_keys.access_token_secret)

        # wait_on_rate_limit will put the running code on sleep and will resume it after rate limit time
        self.api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.input_file_path = input_file
        self.output_file_path = output_file
        self.length_of_file = 0

    def generate_file(self, format=json, size=0, clean_userid=0):
        """
        Method to send the api calls to twitter and get the user data in the json format. The method stores all the
        data in the user specified format(json or csv) in the zip file format to reduce the storage space and also
        prints out the list of failed user ids.
        :param format: format of output file json or csv
        :param size: Specify 1 if you do not want to store tweets with profile information. This will reduce file size.
        :param clean_userid: a flag to store the list of user ids for which we get the data without any error. Pass 1
                             to store the list as csv file.
        """

        time_str = time.strftime("%Y_%m_%d")
        input_file = open(self.input_file_path, 'r')
        self.length_of_file = len(input_file.readlines())

        if format == 'csv':
            output_file_name = time_str + '_profiles_' + str(self.length_of_file) + '.csv'
            output_file = csv.writer(open(self.output_file_path + output_file_name, "w+"))
        else:
            output_file_name = time_str + '_profiles_' + str(self.length_of_file) + '.txt'
            output_file = open(self.output_file_path + output_file_name, "w+")
        clean_userid_file = ''
        if clean_userid:
            clean_userid_file_name = 'new_userid_list_' + time_str + '.csv'
            clean_userid_file = csv.writer(open(self.output_file_path + clean_userid_file_name, "w+"))

        zip_file_name = time_str + '_profiles_' + str(self.length_of_file) + '.zip'

        count = 1
        # user_if_all contains all the user IDs
        user_id_all = []
        # user_if_failed contains a list of user IDs that fail to extracted
        user_id_failed = []
        # user_if_success contains a list of user IDs that api extracted
        user_id_success = []
        data_list = []

        inputfile = open(self.input_file_path, 'r')
        for line in inputfile:
            user_id_all.append(int(float(line.strip())))

            # Call the lookup function for a list 100 user IDs
            if count % 100 == 0 or count == self.length_of_file:
                try:
                    status_object_list = self.api.lookup_users(user_ids=user_id_all)
                except tweepy.TweepError:
                    print("except")

                statuses = []
                # Convert each element of the status_object_list to JSON format
                for status_object in status_object_list:
                    # print(status_object)
                    statuses.append(status_object._json)
                    user_id_success.append(status_object._json["id"])

                # Store the converted user status data in the output file
                if format == "json":
                    if size == 1:
                        status_list = []
                        for status in statuses:
                            user_dict = {}
                            for key in KEY_LIST:
                                user_dict[key] = status[key]
                            status_list.append(user_dict)
                    else:
                        status_list = statuses
                    data_list.extend(status_list)
                # If defined format is csv then the following code snippet will store the user status
                # data into csv format in the output file
                else:
                    status_list = []
                    for status in statuses:
                        # Function will return the 1 dimensional row vector for the given status
                        status = flatten_json(status)
                        if size == 1:
                            status_list.extend([status[key] for key in KEY_LIST])
                        else:
                            status_list.extend(status)
                    data_list.extend(status_list)

                # Extending the list fo failed IDs after each call to api
                user_id_failed.extend(list(set(user_id_all) - set(user_id_success)))
                if clean_userid == 1:
                    for user_id in user_id_success:
                        clean_userid_file.writerow([str(user_id)])
                user_id_all.clear()
                user_id_success.clear()
            count += 1

        # retrieve updated records only
        if time_str.split('_')[-1] != '01':
            data_list = self.generate_longitudinal_data(data_list)
        # Convert the original file to zip file to reduce the storage space
        if format == 'json':
            if data_list:
                json_status = json.dumps(data_list)
                output_file.write(json_status)
        else:
            # If we are writing the first line of the output file then following code will
            # write the headers of each column in the output file
            output_file.writerow(KEY_LIST)
            if data_list:
                for row in data_list:
                    output_file.writerow(row)
        output_file.close()
        os.chdir(self.output_file_path)
        zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
        zipf.write(output_file_name)
        zipf.close()
        os.remove(output_file_name)

        print("failed_IDs:", user_id_failed)
        print("Number of failed ID:", len(user_id_failed))

    def generate_longitudinal_data(self, data_list):
        """
        This function will take the array of all the profiles and return an array of profiles that have made changes in
        their descriptions.
        :param data_list: An array of all the profiles
        :return: an array of profiles that have made changes in their descriptions
        """
        user_profiles = self.reconstruct_data_dictionary()
        updated_user_profiles = []
        for profile in data_list:
            if profile["id_str"] in user_profiles and \
                    profile["description"] == user_profiles[profile["id_str"]]["description"]:
                continue
            updated_user_profiles.append(profile)

        return updated_user_profiles

    def reconstruct_data_dictionary(self):
        """
        This function will reconstruct the a dictionary, where keys are user ids and values are corresponding
        profile data. It uses the 1st day of the month as the base file and updates/adds the user profiles that have
        made changes in their descriptions.
        :return: A dictionary, , where keys are user ids and values are corresponding profile data.
        """
        time_str = time.strftime("%Y_%m_%d")
        curr_year, curr_month, curr_date = time_str.split('_')
        first_flag = 1
        users_profiles = {}
        for date in range(1, int(curr_date)):
            if date > 9:
                date = str(date)
            else:
                date = '0' + str(date)
            input_f = self.output_file_path + curr_year + "_" + curr_month + "_" + str(date) + '_profiles_' + \
                      str(self.length_of_file) + '.zip'
            if not os.path.exists(input_f):
                continue
            if first_flag:
                users_profiles = get_user_profile_dict(input_f)
                first_flag = 0
                continue
            temp_user_profiles = get_user_profile_dict(input_f)

            for user in temp_user_profiles:
                users_profiles[user] = temp_user_profiles[user]

        return users_profiles

    def reconstruct_data(self):
        """
        This function calls the reconstruct_data_dictionary function to get the updated user profiles dictionary and
        store it as a zip file in the user specified location.
        """

        time_str = time.strftime("%Y_%m_%d")
        user_profiles = self.reconstruct_data_dictionary()
        json_status = json.dumps(list(user_profiles.values()))

        output_file_name = self.output_file_path + time_str + '_pprofiles_' + str(self.length_of_file) + '.txt'
        output_file = open(output_file_name, "w+")
        output_file.write(json_status)

        zip_file_name = time_str + '_pprofiles_' + str(self.length_of_file) + '.zip'
        os.chdir(self.output_file_path)
        zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
        zipf.write(output_file_name)
        zipf.close()
        os.remove(output_file_name)






