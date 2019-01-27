import json
import nltk
# from nltk.collocations import *
from nltk.util import ngrams
from nltk.tokenize import TweetTokenizer
import collections
import re
import string
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
nltk.download('punkt')
import csv
import pandas as pd
from config import parse_args2
import os
import time
import glob


def ngram_frequency_dist(inputfile, outputfilepath, n=1):
    with open(inputfile, "r") as f:
        json_list = json.load(f)

    text = ''
    for user in json_list:
        text += user['description'].lower() + " "

    # get rid of punctuation (except periods!)
    punctuation_no_period = "[" + re.sub("\.", "", string.punctuation) + "]"
    text = re.sub(punctuation_no_period, "", text)

    # Splits the sentences into words
    tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)
    tokens = tknzr.tokenize(text)
    # tokens = nltk.word_tokenize(text)

    ngrams_list = ngrams(tokens, n)
    # get the frequency of each ngram in our corpus
    ngram_freq = collections.Counter(ngrams_list)
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
        # fieldnames = ['number', 'colour', 'number2', 'count']
        writer = csv.writer(csvfile)
        # writer.writerow(fieldnames)
        for item in ngram_freq:
            writer.writerow(item)


def daily_unigram_collector(inputfilepath, outputfile):
    for file in glob.glob(os.path.join(inputfilepath, 'output_*2019.txt')):
        with open(file, "r") as f:
            json_list = json.load(f)
        text = ''
        for user in json_list:
            text += user['description'].lower() + " "

        # get rid of punctuation (except periods!)
        punctuation_no_period = "[" + re.sub("\.", "", string.punctuation) + "]"
        text = re.sub(punctuation_no_period, "", text)

        # Splits the sentences into words
        tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)
        tokens = tknzr.tokenize(text)
        # tokens = nltk.word_tokenize(text)

        ngrams_list = list(ngrams(tokens, 1))
        # get the frequency of each ngram in our corpus
        ngram_freq = collections.Counter(ngrams_list)
        ngram_freq = ngram_freq.most_common()

        # Creating the new row to add to the daily collector file
        new_row1 = {}
        # Extracting the Date from the filename
        new_row1['Date'] = re.findall(r'[0-9]{2}_[0-9]{2}_[0-9]{4}', file)[0]
        for item, val in ngram_freq:
            new_row1[item[0]] = [val]
        new_row = pd.DataFrame(new_row1)
        # Setting the index key to the Date
        # new_row.set_index('Date', inplace=True)

        # Checking the file exist or not
        # If no then generate a new one or append the line at the end of the file
        if not os.path.exists(outputfile):
            unigram_combined = new_row
        else:
            unigram_original = pd.read_csv(outputfile, index_col=0)
            unigram_combined = pd.concat([unigram_original, new_row], sort=False, ignore_index=True, axis=0)
        unigram_combined.to_csv(outputfile)


def gen_histogram(inputfile, outputfilepath):

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


def gen_histogram1(inputfile, outputfilepath, n=1):

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


def main():

    args = parse_args2()
    # ngram_frequency_dist(args.inputfile, args.outputfile, args.n)

    daily_unigram_collector(args.inputfile, args.outputfile)
    # gen_histogram1(args.inputfile, args.outputfile, n=1)


if __name__ == "__main__":
    main()
