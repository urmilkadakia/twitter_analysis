import os
import re
import zipfile
import json
from datetime import datetime as dt
import datetime
import pandas as pd


def log_tweep_error(logger, tweep_error, message=""):
    """Log a TweepError exception."""
    if tweep_error.api_code:
        api_code = tweep_error.api_code
    else:
        api_code = int(re.findall(r'"code":[0-9]+', tweep_error.reason)[0].split(':')[1])
    if api_code == 32:
        logger.error("invalid Twitter API authentication tokens")
    elif api_code == 34:
        logger.error("requested object (user, Tweet, etc) not found")
    elif api_code == 64:
        logger.error("your Twitter developer account is suspended and is not permitted")
    elif api_code == 130:
        logger.error("Twitter is currently in over capacity")
    elif api_code == 131:
        logger.error("internal Twitter error occurred")
    elif api_code == 135:
        logger.error("could not authenticate your Twitter API tokens")
    elif api_code == 136:
        logger.error("you have been blocked to perform this action")
    elif api_code == 179:
        logger.error("you are not authorized to see this Tweet")
    else:
        if message:
            logger.error("error while using the Twitter REST API: %s. Message = %s", tweep_error, message)
        else:
            logger.error("error while using the Twitter REST API: %s", tweep_error)


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


def generate_state_dictionary():
    """
    The function that reads uscities.csv file which contains the information about the city, county, state id and state
    names and returns a hash map object where key is state name and values is a set of cities and counties in
    the state
    :return: Returns a hash map object where key is state name and values is a set of cities and counties in
             the state
    """
    path_to_location_file = os.getcwd() + "/Data/uscities.csv"
    df = pd.read_csv(path_to_location_file)
    state_locations = {}

    for index, row in df.iterrows():
        state_name = re.sub(r"[^a-zA-Z]+", ' ', row[3]).lower()
        if state_name not in state_locations:
            state_locations[state_name] = set()

            # Adding state ID to the dictionary
            state_locations[state_name].add(re.sub(r"[^a-zA-Z]+", ' ', row[2]).lower())

        # Adding city name to the dictionary
        if row[0]:
            state_locations[state_name].add(re.sub(r"[^a-zA-Z]+", ' ', row[0]).lower())

        # Adding county name to the dictionary
        if row[5]:
            state_locations[state_name].add(re.sub(r"[^a-zA-Z]+", ' ', row[5]).lower())

    return state_locations


def get_user_description_dict(input_file):
    """
    The method read the json file and generates dictionary where each key is user id and corresponding value is his/her
    profile description.
    :param input_file: path to input file
    :return: Return a dictionary where user id is key and his/her description is its value.
    """
    user_descriptions = {}

    with zipfile.ZipFile(input_file, 'r') as z:
        for filename in z.namelist():
            if z.getinfo(filename).file_size == 0:
                return user_descriptions
            with z.open(filename) as f:
                json_list = json.load(f)

    for user in json_list:
        user_descriptions[user['id_str']] = user['description']

    return user_descriptions


def reconstruct_user_description_dictionary(input_file_folder_path, number_of_users, end_date=dt.strftime(dt.now(), '%Y_%m_%d')):
    """
    This function will reconstruct the a dictionary, where keys are user ids and values are corresponding
    profile descriptions. It uses the 1st day of the month as the base file and updates/adds the user descriptions that
    have made changes in their descriptions.
    :param input_file_folder_path: Path to the folder in which input files are stored
    :param number_of_users: To identify the input file as they are named based on the number of users
    :param end_date: date up to which the function will reconstruct the description dictionary
    :return: A dictionary, , where keys are user ids and values are corresponding descriptions.
    """
    first_flag = 1
    user_descriptions = {}
    end_date = dt.strptime(end_date, '%Y_%m_%d')
    curr_date = str(end_date.year) + '_' + str(end_date.month) + '_01'
    end_date = dt.strftime(end_date, '%Y_%m_%d')

    while curr_date != end_date:
        input_f = os.path.join(input_file_folder_path, curr_date + '_profiles_' + str(number_of_users) + '.zip')
        if os.path.exists(input_f):
            if first_flag:
                user_descriptions = get_user_description_dict(input_f)
                first_flag = 0
                continue
            temp_user_descriptions = get_user_description_dict(input_f)

            for user in temp_user_descriptions:
                user_descriptions[user] = temp_user_descriptions[user]
        curr_date = dt.strptime(curr_date, '%Y_%m_%d')
        curr_date += datetime.timedelta(days=1)
        curr_date = dt.strftime(curr_date, '%Y_%m_%d')

    return user_descriptions


def get_user_profile_dict(input_file):
    """
    The method read the json file and generates dictionary where each key is user id and corresponding value is his/her
    profile data.
    :param input_file: Path to input file
    :return: Return a dictionary where user id is key and his/her twitter profile data is its value.
    """
    user_profiles = {}

    with zipfile.ZipFile(input_file, 'r') as z:
        for filename in z.namelist():
            if z.getinfo(filename).file_size == 0:
                return user_profiles
            with z.open(filename) as f:
                json_list = json.load(f)

    for user in json_list:
        user_profiles[user['id_str']] = user

    return user_profiles


def reconstruct_data_dictionary(input_file_folder_path, number_of_users, end_date=dt.strftime(dt.now(), '%Y_%m_%d')):
    """
    This function will reconstruct the a dictionary, where keys are user ids and values are corresponding
    profile data. It uses the 1st day of the month as the base file and updates/adds the user profiles that have
    made changes in their descriptions.
    :param input_file_folder_path: Path to the folder in which input files are stored
    :param number_of_users: To identify the input file as they are named based on the number of users
    :param end_date: date up to which the function will reconstruct the description dictionary
    :return: A dictionary, , where keys are user ids and values are corresponding profile data.
    """

    first_flag = 1
    users_profiles = {}
    end_date = dt.strptime(end_date, '%Y_%m_%d')
    curr_date = str(end_date.year) + '_' + str(end_date.month) + '_01'
    end_date = dt.strftime(end_date, '%Y_%m_%d')

    while curr_date != end_date:
        input_f = os.path.join(input_file_folder_path, curr_date + '_profiles_' + str(number_of_users) + '.zip')
        if os.path.exists(input_f):
            if first_flag:
                users_profiles = get_user_profile_dict(input_f)
                first_flag = 0
                continue
            temp_user_profiles = get_user_profile_dict(input_f)

            for user in temp_user_profiles:
                users_profiles[user] = temp_user_profiles[user]

        curr_date = dt.strptime(curr_date, '%Y_%m_%d')
        curr_date += datetime.timedelta(days=1)
        curr_date = dt.strftime(curr_date, '%Y_%m_%d')

    return users_profiles


def reconstruct_data(input_file_folder_path, output_file_path, number_of_users, end_date=dt.strftime(dt.now(), '%Y_%m_%d')):
    """
    This function calls the reconstruct_data_dictionary function to get the updated user profiles dictionary and
    store it as a zip file in the user specified location.
    :param output_file_path: Path to the output file
    :param input_file_folder_path: Path to the folder in which input files are stored
    :param number_of_users: To identify the input file as they are named based on the number of users
    :param end_date: date up to which the function will reconstruct the description dictionary
    """

    user_profiles = reconstruct_data_dictionary(input_file_folder_path, number_of_users, end_date)
    json_status = json.dumps(list(user_profiles.values()))

    output_file_base_name = end_date + '_full_profiles_' + str(number_of_users) + '.txt'
    output_file_name = os.path.join(output_file_path, output_file_base_name)
    output_file = open(output_file_name, "w+")
    output_file.write(json_status)

    zip_file_name = end_date + '_full_profiles_' + str(number_of_users) + '.zip'
    os.chdir(output_file_path)
    zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
    zipf.write(output_file_name, output_file_base_name)
    zipf.close()
    os.remove(output_file_name)
