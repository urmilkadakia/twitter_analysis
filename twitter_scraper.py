import tweepy
import json
import api_keys
import csv
import time
from datetime import datetime as dt
import zipfile
import os
import logging
from util import flatten_json, log_tweep_error, reconstruct_data_dictionary, reconstruct_data


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

filename = os.getcwd() + '/Logs/twitter_analysis_' + dt.now().strftime("%m_%Y") + '.log'

if not os.path.exists(filename):
    open(filename, 'w+').close()

file_handler = logging.FileHandler(filename)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

KEY_LIST = ['id', 'id_str', 'name', 'screen_name', 'location', 'description', "followers_count", 'friends_count',
            'statuses_count', 'created_at']


class TwitterScraper:
    """
    Twitter_Scraper class contains the logic to scrape the given userId list and store it in the format of either
    json or csv.
    """
    def __init__(self, input_file_path, output_file_path):
        """
        Method to initialized the class data members
        :param input_file_path: User input for path to the input file
        :param output_file_path: User input for path to the output folder

        api: Data member in the form of tweepy OAuthHandler object
        """

        auth = tweepy.OAuthHandler(api_keys.api_key, api_keys.api_secret_key)
        auth.set_access_token(api_keys.access_token, api_keys.access_token_secret)

        try:
            auth.get_authorization_url()
        except tweepy.TweepError as e:
            log_tweep_error(logger, e)
            del auth
            exit(1)

        # wait_on_rate_limit will put the running code on sleep and will resume it after rate limit time
        self.api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        input_file = open(self.input_file_path, 'r')
        self.length_of_file = len(input_file.readlines())

    def generate_file(self, format=json, size_flag=False, clean_userid_flag=False):
        """
        Method to send the api calls to twitter and get the user data in the json format. The method stores all the
        data in the user specified format(json or csv) in the zip file format to reduce the storage space and also
        prints out the list of failed user ids.
        :param format: format of output file json or csv
        :param size_flag: Specify True if you do not want to store tweets with profile information. This will reduce
        file size. This only works with the json format.
        :param clean_userid_flag: a flag to store the list of user ids for which we get the data without any error.
        Pass True to store the list as csv file.
        """

        time_str = dt.now().strftime("%Y_%m_%d")

        if format == 'csv':
            output_file_name = time_str + '_profiles_' + str(self.length_of_file) + '.csv'
            output_file = open(self.output_file_path + output_file_name, "w+")
            output_file_csv = csv.writer(output_file)
        else:
            output_file_name = time_str + '_profiles_' + str(self.length_of_file) + '.txt'
            output_file = open(self.output_file_path + output_file_name, "w+")

        if clean_userid_flag:
            clean_userid_file_name = time_str + '_userid_list_' + str(self.length_of_file) + '.csv'
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
            status_object_list = []
            # Call the lookup function for a list 100 user IDs
            if count % 100 == 0 or count == self.length_of_file:
                # Retry 3 times if there is a Twitter overfull/internal error
                retry_count = 3
                while True:
                    try:
                        status_object_list = self.api.lookup_users(user_ids=user_id_all)
                    except tweepy.TweepError as e:
                        log_tweep_error(logger, e)
                        if retry_count > 0 and (e.api_code == 130 or e.api_code == 131):
                            time.sleep(60)
                            retry_count -= 1
                            continue
                    break
                statuses = []
                # Convert each element of the status_object_list to JSON format
                for status_object in status_object_list:
                    statuses.append(status_object._json)
                    user_id_success.append(status_object._json["id"])

                # Store the converted user status data in the output file
                if format == "json":
                    if size_flag:
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
                        status_list.append([status[key] for key in KEY_LIST])

                    data_list.extend(status_list)

                # Extending the list fo failed IDs after each call to api
                user_id_failed.extend(list(set(user_id_all) - set(user_id_success)))
                if clean_userid_flag:
                    for user_id in user_id_success:
                        clean_userid_file.writerow([str(user_id)])
                user_id_all.clear()
                user_id_success.clear()
            count += 1

        # Convert the original file to zip file to reduce the storage space
        if format == 'json':
            # retrieve updated records only
            if time_str.split('_')[-1] != '01':
                data_list = self.generate_longitudinal_data(data_list)

            if data_list:
                json_status = json.dumps(data_list)
                output_file.write(json_status)
        else:
            # If we are writing the first line of the output file then following code will
            # write the headers of each column in the output file
            output_file_csv.writerow(KEY_LIST)
            if data_list:
                for row in data_list:
                    output_file_csv.writerow(row)
        output_file.close()
        os.chdir(self.output_file_path)
        zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
        zipf.write(output_file_name)
        zipf.close()
        os.remove(output_file_name)

        logger.info('Number of successful ID:' + str(self.length_of_file - len(user_id_failed)) + ' and '
                    + 'Number of failed ID:' + str(len(user_id_failed)))

        print('Number of successful ID:' + str(self.length_of_file - len(user_id_failed)) + ' and '
              + 'Number of failed ID:' + str(len(user_id_failed)))

    def generate_longitudinal_data(self, data_list):
        """
        This function will take the array of all the profiles and return an array of profiles that have made changes in
        their descriptions.
        :param data_list: An array of all the profiles
        :return: an array of profiles that have made changes in their descriptions
        """
        user_profiles = reconstruct_data_dictionary(self.output_file_path, self.length_of_file)

        # When no base file found
        if not user_profiles:
            return data_list

        updated_user_profiles = []
        for profile in data_list:
            if profile["id_str"] in user_profiles and \
                    profile["description"] == user_profiles[profile["id_str"]]["description"]:
                continue
            updated_user_profiles.append(profile)

        return updated_user_profiles
