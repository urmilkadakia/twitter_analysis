import argparse
import os
import re
import zipfile
import json
import pandas as pd


def is_valid_file(parser, arg):
    """
    Throws an error if the file does not exists at the given location
    :param parser: Object of argparse class
    :param arg: file path for which the function is going to check whether it exist or not
    :return: Return file path if file exist or throw an error of file not exist
    """
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg  # return file path


def parse_args():
    """
    The function to get the inputs from the command line.
    :return: Returns a parser object with the user inputs from the command line
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i1", dest="input_file1", required=True,
                        help="Path to input file 1", type=lambda x: is_valid_file(parser, x))
    parser.add_argument("-i2", dest="input_file2", required=False,
                        help="Path to input file 2", type=lambda x: is_valid_file(parser, x))
    parser.add_argument("-o", dest="output_file", required=False,
                        help="Path to output file")
    parser.add_argument("-f", dest="format", required=False, choices=["json", "csv"],
                        help="Specify the format of the output file", default="json", type=str)
    parser.add_argument("-s", dest="size", required=False,
                        help="Specify 1 if you do not want to store tweets with profile information. "
                             "This will reduce file size.", default=0, type=int)
    parser.add_argument("-u", dest="clean_userid", required=False,
                        help="Specify 1 if want to store a cleaned list of user ids", default=0, type=int)
    parser.add_argument("-n", dest="n", required=False,
                        help="Specify the ngram", default=1, type=int)
    parser.add_argument("-c", dest="cutoff_freq", required=False,
                        help="The ngrams that has less frequency than the cut off frequency will not be included in "
                             "the output file", default=5, type=int)

    args = parser.parse_args()

    return args


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


def date_sort(file):
    """
    The function extracts the date from the filename and return it
    :param file: the name of the file in the string format
    :return: the extracted date from the filename as an integer of form yyyymmdd
    """
    date = re.findall(r'[0-9]{4}_[0-9]{2}_[0-9]{2}', file)[0]
    date = int(''.join(date.split('_')))
    return date


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


def get_user_profile_dict(input_file):
    """
    The method read the json file and generates dictionary where each key is user id and corresponding value is his/her
    profile data.
    :param input_file: Path to input file
    :return: Return a dictionary where user id is key and his/her twitter profile data is its value.
    """
    with zipfile.ZipFile(input_file, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    user_profiles = {}
    for user in json_list:
        user_profiles[user['id_str']] = user

    return user_profiles


def get_user_description_dict(input_file):
    """
    The method read the json file and generates dictionary where each key is user id and corresponding value is his/her
    profile description.
    :param input_file: path to input file
    :return: Return a dictionary where user id is key and his/her description is its value.
    """
    with zipfile.ZipFile(input_file, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    user_descriptions = {}
    for user in json_list:
        user_descriptions[user['id_str']] = user['description']

    return user_descriptions


def log_tweep_error(logger, tweep_error):
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
        logger.error("error while using the Twitter REST API: %s", tweep_error)
