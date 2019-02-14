import argparse
import os
import re
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


def generate_state_dictionary(inputfile):
    """
    The function that read the input file which contains the information about the city, county, state id and state
    names and returns a a dictionary object where key is state name and values is a set of cities and counties in
    the state
    :param inputfile: Path to input file which contains the information about the city, county, state id and state names
    :return: Returns a dictionary object where key is state name and values is a set of cities and counties in
             the state
    """
    df = pd.read_csv(inputfile)
    state_locations = {}

    for index, row in df.iterrows():
        state_name = re.sub(r"[^a-zA-Z]+", ' ', row[3]).lower()
        if state_name not in state_locations:
            state_locations[state_name] = set()
            state_locations[state_name].add(state_name)

            # Adding state ID to the dictionary
            state_locations[state_name].add(re.sub(r"[^a-zA-Z]+", ' ', row[2]).lower())

        # Adding city name to the dictionary
        if row[0]:
            state_locations[state_name].add(re.sub(r"[^a-zA-Z]+", ' ', row[0]).lower())

        # Adding county name to the dictionary
        if row[5]:
            state_locations[state_name].add(re.sub(r"[^a-zA-Z]+", ' ', row[5]).lower())

    return state_locations
