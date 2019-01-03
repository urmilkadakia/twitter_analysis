import json
import nltk
# from nltk.collocations import *
from nltk.util import ngrams
import collections
import re
import string
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
nltk.download('punkt')
import csv
from config import parse_args2


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
    tokens = nltk.word_tokenize(text)

    ngrams_list = ngrams(tokens, n)
    # get the frequency of each bigram in our corpus
    ngram_freq = collections.Counter(ngrams_list)
    ngram_freq = ngram_freq.most_common()

    if n == 1:
        ngram_type = 'uni'
    elif n== 2:
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


def main():

    args = parse_args2()
    ngram_frequency_dist(args.inputfile, args.outputfile, args.n)

    gen_histogram(args.inputfile, args.outputfile)

if __name__ == "__main__":
    main()
