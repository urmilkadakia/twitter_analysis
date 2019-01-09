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
from config import parse_args4
from ngrams_frequency import ngram_frequency_dist


def count_ngrams_frequency(inputfile, n):
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
    # get the frequency of each bigram in our corpus
    ngram_freq = collections.Counter(ngrams_list)
    # ngram_freq = ngram_freq.most_common()
    ngram_freq = collections.OrderedDict(sorted(ngram_freq.items()))
    return ngram_freq


def changing_ngram(inputfile1, inputfile2,  outputfilepath, n=1):

    ngram_freq1 = count_ngrams_frequency(inputfile1, n)
    ngram_freq2 = count_ngrams_frequency(inputfile2, n)

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
        # fieldnames = ['number', 'colour', 'number2', 'count']
        writer = csv.writer(csvfile)
        # writer.writerow(fieldnames)
        for item in ngram_freq:
            writer.writerow(item)


def main():

    args = parse_args4()
    changing_ngram(args.inputfile1, args.inputfile2, args.outputfile, args.n)


if __name__ == "__main__":
    main()
