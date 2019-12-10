import os
import zipfile
import json
from datetime import datetime as dt
import datetime


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
    :return: A dictionary, where keys are user ids and values are corresponding descriptions.
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


def reconstruct_longitudinal_data(input_file_folder_path, output_file_path, number_of_users, end_date=dt.strftime(dt.now(), '%Y_%m_%d')):
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
