import json
import csv
import nltk
from nltk.util import ngrams
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
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
nltk.download('stopwords')
from util import date_sort, generate_state_dictionary


def count_ngrams_frequency(input_file, n):
    """
    The function will count the frequencies for the given ngram
    :param input_file: Path to the input file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigrams.
    :return: Returns the dictionary of ngram and frequency as the key value pairs sorted in the decreasing order.
    """
    with zipfile.ZipFile(input_file, 'r') as z:
        for filename in z.namelist():
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


def ngram_frequency_dist(input_file, output_file, n=1):
    """
    The function counts the frequency of each ngram specified by the input parameter n and store the output as the csv
    at the output file location.
    :param input_file: Path to the input file
    :param output_file: Path to the output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items
    """
    ngram_freq = count_ngrams_frequency(input_file, n)
    ngram_freq = ngram_freq.most_common()

    with open(output_file, "w+") as csvfile:
        writer = csv.writer(csvfile)
        for item in ngram_freq:
            writer.writerow(item)


def changing_ngram(input_file1, input_file2,  output_file, n=1):
    """
    The function counts the difference between the frequencies of the two given files for the specified ngram and
    store it in the output file path folder.
    :param input_file1: Path to the input file 1
    :param input_file2: Path to the input file 2
    :param output_file: Path to the output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items.
    """

    ngram_freq1 = count_ngrams_frequency(input_file1, n)
    ngram_freq1 = collections.OrderedDict(sorted(ngram_freq1.items()))
    ngram_freq2 = count_ngrams_frequency(input_file2, n)
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

    with open(output_file, "w+") as csvfile:
        writer = csv.writer(csvfile)
        for item in ngram_freq:
            writer.writerow(item)


def daily_ngram_collector(input_file_path, output_file, n=1, cutoff_freq=5):
    """
    The function reads all the files that are in the input file folder and counts the ngram frequencies for all
    the ngrams in the file and finally combine them all in a date vise sorted csv file.
    :param input_file_path: Path to the folder in which input files are stored
    :param output_file: Path to the output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigrams.
    :param cutoff_freq: The ngrams that has less frequency than the cut off frequency will not be included in the
                        output file. The default value is 5.
    """
    for file in sorted(glob.glob(os.path.join(input_file_path, '*10000.zip')), key=date_sort):
        ngram_freq = count_ngrams_frequency(file, n=n)
        ngram_freq = ngram_freq.most_common()

        # Creating the new row to add to the daily collector file
        new_row1 = {}
        # Extracting the Date from the filename
        new_row1['Date'] = re.findall(r'[0-9]{4}_[0-9]{2}_[0-9]{2}', file)[0]
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
        if not os.path.exists(output_file):
            ngram_combined = new_row1
        else:
            ngram_original = pd.read_csv(output_file, index_col=0)
            ngram_combined = pd.concat([ngram_original, new_row1], sort=False, ignore_index=True, axis=0)
        ngram_combined.replace(np.nan, 0, inplace=True)
        ngram_combined.to_csv(output_file)


def char_length_histogram(input_file, output_file):
    """
    The function to plot and store the histogram of the character length description of each user in the file
    :param input_file: Path to the input file
    :param output_file: Path to the output file
    """

    with zipfile.ZipFile(input_file, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    text_len = []
    for user in json_list:
        text_len.append(len(user['description']))

    # An "interface" to matplotlib.axes.Axes.hist() method
    n, bins, patches = plt.hist(x=text_len, bins=25, rwidth=0.9)
    plt.xlabel('Character length', fontsize=12)
    plt.ylabel('Frequency',  fontsize=12)
    plt.title('Character length distribution of user descriptions',  fontsize=14)
    plt.savefig(output_file)


def ngram_histogram(input_file, output_file, n=1, cutoff_freq=5):
    """
    The function to plot and store the histogram of the specified ngram and their frequencies for the ngrams which has
    frequency greater than cutoff_freq
    :param input_file: Path to input file
    :param output_file: Path to output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigrams.
    :param cutoff_freq: The ngrams that has less frequency than the cut off frequency will not be included in the
                        output file.  The default value is 5.
    """
    ngram_freq = count_ngrams_frequency(input_file, n)
    ngram_freq = ngram_freq.most_common()
    # stop_words = set(stopwords.words('english'))

    xdata = []
    ydata = []

    for x, y in ngram_freq:
        if y < cutoff_freq:
            break

        # if not any(elem in x for elem in stop_words):
        # Checking the ngram is unigram or not
        if n == 1:
            xdata.append(x[0])
        else:
            xdata.append(str(x))
        ydata.append(y)

    # Plotting the ngrams of the given file
    plt.bar(xdata, ydata)
    plt.xlabel('Ngrams', fontsize=12)
    plt.xticks(xdata, xdata, rotation=80)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Ngram frequency distribution ', fontsize=14)
    plt.gcf().subplots_adjust(bottom=0.45)
    plt.savefig(output_file)


def get_locations(input_file1, input_file2, output_file):
    """
    The function writes the user id and his/her us state name in the output file based on the the value of location key in the user
    information and state_location dictionary. If function does not find the location in the state_locations dictionary
    then not in usa will be written against the user id.
    :param input_file1: Path to input file
    :param input_file2: Path to the usa location file
    :param output_file: Path to output file
    """
    with zipfile.ZipFile(input_file1, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    state_locations = generate_state_dictionary(input_file2)
    location_dict = {}
    for item in json_list:
        location_dict[item['id']] = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?]', item['location'].lower())
    state_flag = 0
    us_flag = 0
    cnt = 0
    for user_id in location_dict:
        for item in location_dict[user_id]:
            for state in state_locations:
                if item.strip() in state_locations[state]:
                    location_dict[user_id] = state
                    state_flag = 1
                    break
            if state_flag == 1:
                break
        if state_flag == 1:
            state_flag = 0
        else:
            for item in location_dict[user_id]:
                if item.strip() == 'us' or item.strip() == 'usa' or item.strip() == 'united states':
                    location_dict[user_id] = 'usa'
                    us_flag = 1
                    break
            if us_flag == 1:
                us_flag = 0
            else:
                # print(location_dict[user_id])
                location_dict[user_id] = 'not in usa'
                cnt += 1
    header_flag = 0
    with open(output_file, 'w') as csvfile:
        writer = csv.writer(csvfile)
        if header_flag == 0:
            writer.writerow(['Id', 'Location'])
        for data in location_dict:
            writer.writerow([data, location_dict[data]])

