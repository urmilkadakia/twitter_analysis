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


def changing_ngram(inputfile1, inputfile2,  outputfilepath, n=1):
    """
    The function will count the difference between the frequencies of the two given files for the specified ngram and
    store it in the output file path folder.
    :param inputfile1: Path to the input file 1
    :param inputfile2: Path to the input file 2
    :param outputfilepath: Path to the output folder
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

    if n == 1:
        ngram_type = 'uni'
    elif n == 2:
        ngram_type = 'bi'
    elif n == 3:
        ngram_type = 'tri'
    else:
        ngram_type = str(n)
    with open(outputfilepath + ngram_type + "gram_change_freq.csv", "w+") as csvfile:
        writer = csv.writer(csvfile)
        for item in ngram_freq:
            writer.writerow(item)


def ngram_frequency_dist(inputfile, outputfilepath, n=1):
    """

    :param inputfile:
    :param outputfilepath:
    :param n:
    :return:
    """
    ngram_freq = count_ngrams_frequency(inputfile, n)
    ngram_freq = ngram_freq.most_common()

    if n == 1:
        ngram_type = 'uni'
    elif n == 2:
        ngram_type = 'bi'
    elif n == 3:
        ngram_type = 'tri'
    else:
        ngram_type = str(n)
    with open(outputfilepath + ngram_type + "gram.csv", "w+") as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow(fieldnames)
        for item in ngram_freq:
            writer.writerow(item)


def dateSort(file):
    date = re.findall(r'[0-9]{2}_[0-9]{2}_[0-9]{4}', file)[0]
    date = int(''.join(date.split('_')))
    return date


def daily_unigram_collector(inputfilepath, outputfile, freq):
    """
    The function reads all the files that are in the input file folder and counts the ngram frequencies for all
    the ngrams in the file and finally combine them all in a date vise sorted csv file.
    :param inputfilepath: Path to the folder in which input files are stored
    :param outputfile: Path to the output file
    :param freq: The ngrams that has less frequency than the cut off frequency will not be included in the output file
    """
    for file in sorted(glob.glob(os.path.join(inputfilepath, '*2019.zip')), key=dateSort):
        ngram_freq = count_ngrams_frequency(file, n=1)
        ngram_freq = ngram_freq.most_common()

        # Creating the new row to add to the daily collector file
        new_row1 = {}
        # Extracting the Date from the filename
        new_row1['Date'] = re.findall(r'[0-9]{2}_[0-9]{2}_[0-9]{4}', file)[0]
        for item, val in ngram_freq:
            new_row1[item[0]] = [val]
        new_row = pd.DataFrame(new_row1)

        new_row1 = pd.DataFrame()
        for col in list(new_row.columns):
            if col == 'Date':
                new_row1[col] = new_row[col]
                continue
            if new_row[col][0] > freq:
                new_row1[col] = new_row[col]

        # Checking the file exist or not
        # If not then generate a new one or append the line at the end of the file
        if not os.path.exists(outputfile):
            unigram_combined = new_row1
        else:
            unigram_original = pd.read_csv(outputfile, index_col=0)
            unigram_combined = pd.concat([unigram_original, new_row1], sort=False, ignore_index=True, axis=0)
        unigram_combined.replace(np.nan, 0, inplace=True)
        unigram_combined.to_csv(outputfile)


def char_length_histogram(inputfile, outputfilepath):
    """

    :param inputfile:
    :param outputfilepath:
    :return:
    """

    with open(inputfile, "r") as f:
        json_list = json.load(f)

    text_len = []
    for user in json_list:
        text_len.append(len(user['description']))

    # An "interface" to matplotlib.axes.Axes.hist() method
    n, bins, patches = plt.hist(x=text_len, bins=25, rwidth=0.9)
    plt.xlabel('character length')
    plt.ylabel('Frequency')
    plt.title('Description character length distribution')
    plt.savefig(outputfilepath + "histogram.png")


def ngram_histogram(inputfile, outputfilepath, n=1):
    """

    :param inputfile:
    :param outputfilepath:
    :param n:
    :return:
    """

    ngram_frequency_dist(inputfile, outputfilepath, n=1)
    data = pd.read_csv(outputfilepath + "uni" + "gram.csv")

    plt.figure(num=None, figsize=(16, 10), dpi=300, facecolor='w', edgecolor='k')

    # Checking the ngram is unigram or not
    if n == 1:
        xdata = []
        for item in data.ix[:, 0]:
            xdata.append(item[2:-3])
    else:
        xdata = data.ix[:, 0]
    ydata = data.ix[:, -1]

    # Plotting the top 50 ngrams of the given file
    plt.bar(xdata[:200], ydata[:200])
    plt.xlabel('character length')
    plt.xticks(xdata[:200], xdata[:200], rotation='vertical')
    plt.ylabel('Frequency')
    plt.title('Description character length distribution')
    plt.savefig(outputfilepath + "ngram_frequency.png")


def get_locations(inputfile, outputfile):
    with open(inputfile, "r") as f:
        json_list = json.load(f)
    df = pd.read_csv('/home/urmilkadakia/Desktop/Masters/Social_behavioral/twitter_analysis/OUTPUT/uscitiesv1.4.csv')
    us_locations = set()

    for index, row in df.iterrows():
        if row[0]:
            us_locations.add(re.sub(r"[^a-zA-Z]+", ' ', row[0]).lower())
        if row[2]:
            us_locations.add(re.sub(r"[^a-zA-Z]+", ' ', row[2]).lower())
        if row[3]:
            us_locations.add(re.sub(r"[^a-zA-Z]+", ' ', row[3]).lower())
        if row[5]:
            us_locations.add(re.sub(r"[^a-zA-Z]+", ' ', row[5]).lower())
    us_locations.add('us')
    us_locations.add('usa')
    location_dict = {}
    for item in json_list:
        location_dict[item['id']] = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?]', item['location'].lower())
    flag = 0
    for id in location_dict:
        for item in location_dict[id]:
            if item.strip() in us_locations:
                location_dict[id] = 'USA'
                flag = 1
                break
        if flag == 0:
            location_dict[id] = 'Not in USA'
        else:
            flag = 0
    print(location_dict)
    location_dict.to_csv(outputfile)


def main():

    args = parse_args2()
    # changing_ngram(args.inputfile, args.inputfile, args.outputfile, args.n)
    # ngram_frequency_dist(args.inputfile, args.outputfile, args.n)

    daily_unigram_collector(args.inputfile, args.outputfile, args.n)
    # get_locations(args.inputfile, args.outputfile)
    # gen_histogram1(args.inputfile, args.outputfile, n=1)


if __name__ == "__main__":
    main()
