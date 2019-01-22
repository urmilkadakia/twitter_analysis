import sys
import tweepy
import json
import api_keys
import csv
import time
import zipfile
import os


key_list = ['id', 'id', 'id_str', 'name', 'screen_name', 'location', 'description', "followers_count",
            'friends_count', 'created_at']


# Converting the multilayer JSON to 1 dimention row vector
def flatten_json(y):
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


# Function will return the tweepys' authenticated api object.
def getAuthentication():

    auth = tweepy.OAuthHandler(api_keys.api_key, api_keys.api_secret_key)
    auth.set_access_token(api_keys.access_token, api_keys.access_token_secret)
    # wait_on_rate_limit will put the running code on sleep and will resume it after rate limit time
    api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    return api


def genFile(inputfilepath, outputfilepath, format, clean_userid):

    timestr = time.strftime("%Y_%m_%d")
    inputfile = open(inputfilepath, 'r')
    if format == 'csv':
        outputfile = csv.writer(open(outputfilepath + timestr + '_profiles_2017_250k' + '.csv', "w+"))
    else:
        outputfile = open(outputfilepath + timestr + '_profiles_2017_250k' + '.txt', "w+")
    clean_userid_file = ''
    if clean_userid:
        clean_userid_file = csv.writer(open(outputfilepath + 'new_userid_list_' + timestr + '.csv', "w+"))

    # Authenticated tweepy api object
    api = getAuthentication()

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

    inputfile = open(inputfilepath, 'r')
    for line in inputfile:
        user_id_all.append(int(float(line.strip())))

        # Call the lookup function for a list 100 user IDs
        if count % 100 == 0 or count == length_of_file:
            try:
                status_object_list = api.lookup_users(user_ids=user_id_all)
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
                    status = flatten_json(status)
                    status_list = [status[key] for key in key_list]

                    # If we are writing the first line of the output file then following code will
                    # write the headers of each column in the output file
                    if header_flag == 0:
                        header = key_list
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

    if format == 'json':
        json_status = json.dumps(json_list)
        outputfile.write(json_status)
        os.chdir(outputfilepath)
        zipfile.ZipFile(timestr + '_profiles_2017_250k' + '.txt.zip', mode='w').write(timestr + '_profiles_2017_250k' + '.txt')
        os.remove(timestr + '_profiles_2017_250k' + '.txt')
    else:
        os.chdir(outputfilepath)
        zipfile.ZipFile(timestr + '_profiles_2017_250k' + '.csv.zip', mode='w').write(timestr + '_profiles_2017_250k' + '.csv')
        os.remove(timestr + '_profiles_2017_250k' + '.csv')

    print("failed_IDs:", user_id_failed)
    print("Number of failed ID:", len(user_id_failed))
