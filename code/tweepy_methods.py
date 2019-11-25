import tweepy
import json
import csv
import time
import zipfile
import os
import logging
from datetime import datetime as dt

from api_keys import access_token, access_token_secret, api_key, api_secret_key, mashape_key
from reconstruction_methods import reconstruct_data_dictionary
from logger import log_twitter_error

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

filename = os.path.join(os.getcwd(), 'logs/tweepy_methods_' + dt.now().strftime("%m_%Y") + '.log')
if not os.path.exists(filename):
    open(filename, 'w+').close()

file_handler = logging.FileHandler(filename)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def _flatten_json(y):
    """
    Method to convert the multilayer JSON to 1 dimension row vector
    :return: flatten json dictionary
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


def twitter_scarper(input_file_path, output_file_path, format=json, size_flag=False, clean_userid_flag=False):
    """
    Method to send the api calls to twitter and get the user data in the json format. The method stores all the
    data in the user specified format(json or csv) in the zip file format to reduce the storage space and also
    prints out the list of failed user ids.
    :param input_file_path: User input for path to the input file
    :param output_file_path: User input for path to the output folder
    :param format: format of output file json or csv
    :param size_flag: Specify True if you do not want to store tweets with profile information. This will reduce
    file size. This only works with the json format.
    :param clean_userid_flag: a flag to store the list of user ids for which we get the data without any error.
    Pass True to store the list as csv file.
    """

    # tweepy OAuthHandler object
    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)

    try:
        auth.get_authorization_url()
    except tweepy.TweepError as e:
        log_twitter_error(logger, e)
        del auth
        exit(1)

    key_list = ['id', 'id_str', 'name', 'screen_name', 'location', 'description', "followers_count", 'friends_count',
                'statuses_count', 'created_at']

    # wait_on_rate_limit will put the running code on sleep and will resume it after rate limit time
    api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    input_file = open(input_file_path, 'r')
    number_of_users = len(input_file.readlines())

    time_str = dt.now().strftime("%Y_%m_%d")

    if format == 'csv':
        output_file_name = time_str + '_profiles_' + str(number_of_users) + '.csv'
        output_file = open(output_file_path + output_file_name, "w+")
        output_file_csv = csv.writer(output_file)
    else:
        output_file_name = time_str + '_profiles_' + str(number_of_users) + '.txt'
        output_file = open(output_file_path + output_file_name, "w+")

    if clean_userid_flag:
        clean_userid_file_name = time_str + '_userid_list_' + str(number_of_users) + '.csv'
        clean_userid_file = csv.writer(open(output_file_path + clean_userid_file_name, "w+"))

    zip_file_name = time_str + '_profiles_' + str(number_of_users) + '.zip'

    count = 1
    # user_id_all contains all the user IDs
    user_id_all = []
    # user_id_failed contains a list of user IDs that fail to extracted
    user_id_failed = []
    # user_id_success contains a list of user IDs that api extracted
    user_id_success = []
    data_list = []

    inputfile = open(input_file_path, 'r')
    for line in inputfile:
        user_id_all.append(int(float(line.strip())))
        status_object_list = []
        # Call the lookup function for a list 100 user IDs
        if count % 100 == 0 or count == number_of_users:
            # Retry 3 times if there is a Twitter overfull/internal error
            retry_count = 3
            while True:
                try:
                    status_object_list = api.lookup_users(user_ids=user_id_all)
                except tweepy.TweepError as e:
                    log_twitter_error(logger, e)
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
                        for key in key_list:
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
                    status = _flatten_json(status)
                    status_list.append([status[key] for key in key_list])

                data_list.extend(status_list)

            # Extending the list of failed IDs after each call to api
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
            data_list = _generate_longitudinal_data(output_file_path, number_of_users, data_list)

        if data_list:
            json_status = json.dumps(data_list)
            output_file.write(json_status)
    else:
        # If we are writing the first line of the output file then following code will
        # write the headers of each column in the output file
        output_file_csv.writerow(key_list)
        if data_list:
            for row in data_list:
                output_file_csv.writerow(row)
    output_file.close()
    os.chdir(output_file_path)
    zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
    zipf.write(output_file_name)
    zipf.close()
    os.remove(output_file_name)

    logger.info('Number of successful ID:' + str(number_of_users - len(user_id_failed)) + ' and '
                + 'Number of failed ID:' + str(len(user_id_failed)))


def _generate_longitudinal_data(output_file_path, number_of_users, data_list):
    """
    This function will take the array of all the profiles and return an array of profiles that have made changes in
    their descriptions.
    :param output_file_path: User input for path to the output folder
    :param number_of_users: To identify the input file as they are named based on the number of users
    :param data_list: An array of all the profiles
    :return: an array of profiles that have made changes in their descriptions
    """
    user_profiles = reconstruct_data_dictionary(output_file_path, number_of_users)

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


def get_twitter_user_id_from_screen_name(input_file_path, output_file_path):
    """
    Method to get the twitter user_id from the screen name
    :param input_file_path: path to input file that contains the list of screen name
    :param output_file_path: path to the output file where the corresponding the user_ids are saved
    """

    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)

    try:
        auth.get_authorization_url()
    except tweepy.TweepError as e:
        log_twitter_error(logger, e)
        del auth
        exit(1)

    # wait_on_rate_limit will put the running code on sleep and will resume it after rate limit time
    api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    output_file = open(output_file_path, "w+")
    output_file_csv = csv.writer(output_file)

    with open(input_file_path, 'r')as file:
        input_file = csv.reader(file, delimiter=',')
        next(input_file)  # skip header
        for row in input_file:
            try:
                output_file_csv.writerow([api.get_user(screen_name=row[1])._json["id"]])
            except tweepy.TweepError as e:
                print(e, row)
                log_twitter_error(logger, e, "Error while accessing user " + row[0].strip() + " : " + row[1])
    output_file.close()
