import json
import csv
import nltk
from nltk.util import ngrams
from nltk.tokenize import TweetTokenizer
import collections
import re
import string
import pandas as pd
import os
import glob
import numpy as np
import zipfile
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
nltk.download('punkt')
from config import parse_args2, parse_args4


def count_ngrams_frequency(inputfile, n):
    """
    The function will count the frequencies for the given ngram
    :param inputfile: Path to the input file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items
    :return: Returns the dictionary of ngram and frequency as the key value pairs sorted in the decreasing order.
    """
    with zipfile.ZipFile(inputfile, 'r') as z:
        for filename in z.namelist():
            # print(filename)
            with z.open(filename) as f:
                json_list = json.load(f)

    text = ''
    for user in json_list:
        text += user['description'].lower() + " "

    # Get rid of punctuation (except periods!)
    punctuation_no_period = "[" + re.sub("\.", "", string.punctuation) + "]"
    text = re.sub(punctuation_no_period, "", text)

    # Splits the sentences into words
    tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)
    tokens = tknzr.tokenize(text)

    ngrams_list = ngrams(tokens, n)
    # Get the frequency of each ngram in our corpus
    ngram_freq = collections.Counter(ngrams_list)
    return ngram_freq


def ngram_frequency_dist(inputfile, outputfile, n=1):
    """
    The function counts the frequency of each ngram specified by the input parameter n and store the output as the csv
    at the output file location.
    :param inputfile: Path to the input file
    :param outputfile: Path to the output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items
    """
    ngram_freq = count_ngrams_frequency(inputfile, n)
    ngram_freq = ngram_freq.most_common()

    with open(outputfile, "w+") as csvfile:
        writer = csv.writer(csvfile)
        for item in ngram_freq:
            writer.writerow(item)


def changing_ngram(inputfile1, inputfile2,  outputfile, n=1):
    """
    The function counts the difference between the frequencies of the two given files for the specified ngram and
    store it in the output file path folder.
    :param inputfile1: Path to the input file 1
    :param inputfile2: Path to the input file 2
    :param outputfile: Path to the output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items
    """

    ngram_freq1 = count_ngrams_frequency(inputfile1, n)
    ngram_freq1 = collections.OrderedDict(sorted(ngram_freq1.items()))
    ngram_freq2 = count_ngrams_frequency(inputfile2, n)
    ngram_freq2 = collections.OrderedDict(sorted(ngram_freq2.items()))

    ngram_freq = {}

    for key in ngram_freq1.keys():
        if key in ngram_freq2:
            ngram_freq[key] = ngram_freq2[key] - ngram_freq1[key]
        else:
            ngram_freq[key] = -1*ngram_freq1[key]

    for key in ngram_freq2:
        if key not in ngram_freq:
            ngram_freq[key] = ngram_freq2[key]

    ngram_freq = sorted(ngram_freq.items(), key=lambda kv: kv[1], reverse=True)

    with open(outputfile, "w+") as csvfile:
        writer = csv.writer(csvfile)
        for item in ngram_freq:
            writer.writerow(item)


def date_sort(file):
    """
    The function extracts the date from the filename and return it
    :param file: the name of the file in the string format
    :return: the extracted date from the filename as an integer of form yyyymmdd
    """
    date = re.findall(r'[0-9]{2}_[0-9]{2}_[0-9]{4}', file)[0]
    date = int(''.join(date.split('_')))
    return date


def daily_ngram_collector(inputfilepath, outputfile, n=1, cutoff_freq=2):
    """
    The function reads all the files that are in the input file folder and counts the ngram frequencies for all
    the ngrams in the file and finally combine them all in a date vise sorted csv file.
    :param inputfilepath: Path to the folder in which input files are stored
    :param outputfile: Path to the output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigrams.
    :param cutoff_freq: The ngrams that has less frequency than the cut off frequency will not be included in the
                        output file. The default value is 10.
    """
    for file in sorted(glob.glob(os.path.join(inputfilepath, '*2019.zip')), key=date_sort):
        ngram_freq = count_ngrams_frequency(file, n=n)
        ngram_freq = ngram_freq.most_common()

        # Creating the new row to add to the daily collector file
        new_row1 = {}
        # Extracting the Date from the filename
        new_row1['Date'] = re.findall(r'[0-9]{2}_[0-9]{2}_[0-9]{4}', file)[0]
        for item, val in ngram_freq:
            if n == 1:
                new_row1[item[0]] = [val]
            else:
                new_row1[item] = [val]
        new_row = pd.DataFrame(new_row1)

        new_row1 = pd.DataFrame()
        for col in list(new_row.columns):
            if col == 'Date':
                new_row1[str(col)] = new_row[col]
                continue
            if new_row[col][0] > cutoff_freq:
                new_row1[str(col)] = new_row[col]
        # Checking the file exist or not
        # If not then generate a new one or append the line at the end of the file
        if not os.path.exists(outputfile):
            ngram_combined = new_row1
        else:
            ngram_original = pd.read_csv(outputfile, index_col=0)
            print(ngram_original.head())
            print(new_row1.head())
            print(ngram_original.columns, new_row1.columns)
            ngram_combined = pd.concat([ngram_original, new_row1], sort=False, ignore_index=True, axis=0)
        ngram_combined.replace(np.nan, 0, inplace=True)
        ngram_combined.to_csv(outputfile)


def char_length_histogram(inputfile, outputfile):
    """
    The function to plot and store the histogram of the character length description of each user in the file
    :param inputfile: Path to the input file
    :param outputfile: Path to the output file
    """

    with zipfile.ZipFile(inputfile, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    text_len = []
    for user in json_list:
        text_len.append(len(user['description']))

    # An "interface" to matplotlib.axes.Axes.hist() method
    n, bins, patches = plt.hist(x=text_len, bins=25, rwidth=0.9)
    plt.xlabel('Character length')
    plt.ylabel('Frequency')
    plt.title('Character length distribution of user descriptions')
    plt.savefig(outputfile)


def ngram_histogram(inputfile, outputfile, cutoff_freq, n=1):
    """
    The function to plot and store the histogram of the specified ngram and their frequencies for the ngrams which has
    frequency greater than cutoff_freq
    :param inputfile: Path to input file
    :param outputfile: Path to output file
    :param cutoff_freq: The ngrams that has less frequency than the cut off frequency will not be included in the
                        output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigrams.
    """
    ngram_freq = count_ngrams_frequency(inputfile, n)
    ngram_freq = ngram_freq.most_common()
    plt.figure(num=None, figsize=(16, 10), dpi=300, facecolor='w', edgecolor='k')

    xdata = []
    ydata = []

    for x, y in ngram_freq:
        if y < cutoff_freq:
            break
        # Checking the ngram is unigram or not
        if n == 1:
            xdata.append(x[0])
        else:
            xdata.append(x)
        ydata.append(y)

    # Plotting the ngrams of the given file
    plt.bar(xdata, ydata)
    plt.xlabel('Ngrams')
    plt.xticks(xdata, xdata, rotation='vertical')
    plt.ylabel('Frequency')
    plt.title('Ngram frequency distribution ')
    plt.savefig(outputfile)


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


def get_locations(inputfile, outputfile):
    """
    The function writes the user id and his/her us state name in the output file based on the the value of location key in the user
    information and state_location dictionary. If function does not find the location in the state_locations dictionary
    then not in usa will be written against the user id.
    :param inputfile: Path to input file
    :param outputfile: Path to input file
    """
    with zipfile.ZipFile(inputfile, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    state_locations = \
        generate_state_dictionary('/home/urmilkadakia/Desktop/Masters/Social_behavioral/twitter_analysis/OUTPUT/uscitiesv1.4.csv')
    location_dict = {}
    for item in json_list:
        location_dict[item['id']] = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?]', item['location'].lower())
    state_flag = 0
    us_flag = 0
    cnt = 0
    for id in location_dict:
        for item in location_dict[id]:
            for state in state_locations:
                if item.strip() in state_locations[state]:
                    location_dict[id] = state
                    state_flag = 1
                    break
            if state_flag == 1:
                break
        if state_flag == 1:
            state_flag = 0
        else:
            for item in location_dict[id]:
                if item.strip() == 'us' or item.strip() == 'usa' or item.strip() == 'united states':
                    location_dict[id] = 'usa'
                    us_flag = 1
                    break
            if us_flag == 1:
                us_flag = 0
            else:
                location_dict[id] = 'not in usa'
                cnt += 1
    header_flag = 0
    with open(outputfile, 'w') as csvfile:
        writer = csv.writer(csvfile)
        if header_flag == 0:
            writer.writerow(['Id', 'Location'])
        for data in location_dict:
            writer.writerow([data, location_dict[data]])


def main():

    args = parse_args2()
    # changing_ngram(args.inputfile, args.inputfile, args.outputfile, args.n)
    # ngram_frequency_dist(args.inputfile, args.outputfile, args.n)

    daily_ngram_collector(args.inputfile, args.outputfile, args.n)
    # get_locations(args.inputfile, args.outputfile)
    # ngram_histogram(args.inputfile, args.outputfile, 10, 1)
    # char_length_histogram(args.inputfile, args.outputfile)


if __name__ == "__main__":
    main()
