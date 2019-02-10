import sys
import tweepy
import json
import api_keys
import csv
import time
import zipfile
import os


class Twitter_Scraper:
    """
    Twitter_Scraper class contains the logic to scrape the given userId list and store it in the format of either
    json or csv.
    """
    def __init__(self, inputfilepath, outputfilepath):
        """
        Method to initialized the class data members

        :param inputfilepath: User input for path to the input file
        :param outputfilepath: User input for path to the output file

        key_list: data member that contains the list of columns names for the csv output file
        """
        self.key_list = ['id', 'id', 'id_str', 'name', 'screen_name', 'location', 'description', "followers_count",
                         'friends_count', 'created_at']

        auth = tweepy.OAuthHandler(api_keys.api_key, api_keys.api_secret_key)
        auth.set_access_token(api_keys.access_token, api_keys.access_token_secret)

        # wait_on_rate_limit will put the running code on sleep and will resume it after rate limit time
        self.api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.inputfilepath = inputfilepath
        self.outputfilepath = outputfilepath

    def flatten_json(y):
        """
        Method to convert the multilayer JSON to 1 dimention row vector

        :return: flattern json dictionary
        """
        out = {}

        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + '_')
            else:
                out[name[:-1]] = x

        # Recursively call itself with the child dictionary
        flatten(y)
        return out

    def genFile(self, format, clean_userid=0):
        """
        Method to send the api calls to twitter and get the user data in the json format. The method stores all the
        data in the user specified format(json or csv) in the zip file format to reduce the storage space and also
        prints out the list of failed user ids.

        :param format: format of output file json or csv
        :param clean_userid: a flag to store the list of user ids for which we get the data without any error. Pass 1
                             to store the list as csv file.
        """

        timestr = time.strftime("%Y_%m_%d")
        inputfile = open(self.inputfilepath, 'r')
        if format == 'csv':
            outputfile = csv.writer(open(self.outputfilepath + timestr + '_profiles_2017_250k' + '.csv', "w+"))
        else:
            outputfile = open(self.outputfilepath + timestr + '_profiles_2017_250k' + '.txt', "w+")
        clean_userid_file = ''
        if clean_userid:
            clean_userid_file = csv.writer(open(self.outputfilepath + 'new_userid_list_' + timestr + '.csv', "w+"))

        count = 1
        # user_if_all contains all the user IDs
        user_id_all = []
        # user_if_failed contains a list of user IDs that fail to extracted
        user_id_failed = []
        # user_if_success contains a list of user IDs that api extracted
        user_id_success = []
        json_list = []
        header_flag = 0

        length_of_file = len(inputfile.readlines())

        inputfile = open(self.inputfilepath, 'r')
        for line in inputfile:
            user_id_all.append(int(float(line.strip())))

            # Call the lookup function for a list 100 user IDs
            if count % 100 == 0 or count == length_of_file:
                try:
                    status_object_list = self.api.lookup_users(user_ids=user_id_all)
                except:
                    print("except")

                statuses = []
                # Convert each element of the status_object_list to JSON format
                for status_object in status_object_list:
                    # print(status_object)
                    statuses.append(status_object._json)
                    user_id_success.append(status_object._json["id"])

                # Store the converted user status data in the output file
                if format == "json":
                    json_list.extend(statuses)
                # If defined format is csv then the following code snippet will store the user status
                # data into csv format in the output file
                else:
                    for status in statuses:
                        # Function will return the 1 dimensional row vector for the given status
                        status = self.flatten_json(status)
                        status_list = [status[key] for key in self.key_list]

                        # If we are writing the first line of the output file then following code will
                        # write the headers of each column in the output file
                        if header_flag == 0:
                            header = self.key_list
                            outputfile.writerow(header)
                            header_flag = 1
                        outputfile.writerow(status_list)
                # Extending the list fo failed IDs after each call to api
                user_id_failed.extend(list(set(user_id_all) - set(user_id_success)))
                if clean_userid == 1:
                    for user_id in user_id_success:
                        clean_userid_file.writerow([str(user_id)])
                user_id_all.clear()
                user_id_success.clear()
            count += 1

        # Convert the original file to zip file to reduce the storage space
        if format == 'json':
            json_status = json.dumps(json_list)
            outputfile.write(json_status)
            os.chdir(self.outputfilepath)
            zipf = zipfile.ZipFile(timestr + '_profiles_2017_250k' + '.txt.zip', 'w', zipfile.ZIP_DEFLATED)
            zipf.write(timestr + '_profiles_2017_250k' + '.txt')
            zipf.close()
            os.remove(timestr + '_profiles_2017_250k' + '.txt')
        else:
            os.chdir(self.outputfilepath)
            zipf = zipfile.ZipFile(timestr + '_profiles_2017_250k' + '.csv.zip', 'w', zipfile.ZIP_DEFLATED)
            zipf.write(timestr + '_profiles_2017_250k' + '.csv')
            zipf.close()
            os.remove(timestr + '_profiles_2017_250k' + '.csv')

        print("failed_IDs:", user_id_failed)
        print("Number of failed ID:", len(user_id_failed))
