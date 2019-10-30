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
# import time
from datetime import datetime as dt
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
from util import date_sort, get_user_description_dict, reconstruct_data_dictionary, reconstruct_user_description_dictionary

mpl.use('Agg')
nltk.download('punkt')
nltk.download('stopwords')


def get_ngram_list(text, n=1):
    """
    Returns the a list of ngram for the input text for the specified ngram type
    :param text: input text
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    :return: Return a list of ngrams
    """

    # Get rid of punctuation (except periods!)
    punctuation_no_period = "[" + re.sub(r"\.", "", string.punctuation) + "]"
    text = re.sub(punctuation_no_period, "", text.lower())

    # Splits the sentences into words
    tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)
    tokens = tknzr.tokenize(text)

    # remove remaining tokens that are not alphabetic
    # Problem !!! also removes emoji joiners and similar tokens
    # tokens = [token for token in tokens if token.isalpha()]

    # filter out stop words
    # stop_words = set(stopwords.words('english'))
    # words = [w for w in words if w not in stop_words]

    ngram_list = list(ngrams(tokens, n))
    return ngram_list


def count_ngrams_frequency(input_file, n=1):
    """
    The function will count the frequencies for the given ngram
    :param input_file: Path to the input file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    :return: Returns the dictionary of ngram and frequency as the key value pairs sorted in the decreasing order.
    """
    with zipfile.ZipFile(input_file, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    text = ''
    for user in json_list:
        text += user['description'] + " "

    ngrams_list = get_ngram_list(text, n)
    # Get the frequency of each ngram in our corpus
    ngram_freq = collections.Counter(ngrams_list)
    return ngram_freq


def ngram_frequency_dist(input_file, output_file, n=1):
    """
    The function counts the frequency of each ngram specified by the input parameter n and store the output as the csv
    at the output file location.
    :param input_file: Path to the input file
    :param output_file: Path to the output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigrams.
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
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
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
              represents unigram.
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
              represents unigram.
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


def ngram_adjacency_matrix(input_file, output_file, n, cut_off):
    """
    The function writes the adjacency matrix to the output file, where the rows and columns are ngram and each cell is
    the number of users that has both the ngram in their description.
    :param input_file: Path to input file
    :param output_file: Path to output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    :param cut_off: The ngrams that has less frequency than the cut off frequency will not be included in the
                    output file. The default value is 5.
    """
    ngram_freq = count_ngrams_frequency(input_file, n)

    for ngram in list(ngram_freq):
        if ngram_freq[ngram] < cut_off:
            del ngram_freq[ngram]

    matrix = pd.DataFrame(np.zeros((len(ngram_freq), len(ngram_freq))), columns=ngram_freq, index=ngram_freq)

    with zipfile.ZipFile(input_file, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    for user in json_list:
        text = user['description']

        ngram_list = get_ngram_list(text, n)
        for i in ngram_list:
            for j in ngram_list:
                try:
                    matrix[i][j] += 1
                except KeyError:
                    continue
    drop_row = []
    for i, row in matrix.iterrows():
        if any(j > cut_off for j in row):
            continue
        else:
            drop_row.append(i)
    matrix.drop(drop_row, inplace=True)

    drop_col = []
    for col in matrix:
        if any(j > cut_off for j in matrix[col]):
            continue
        else:
            drop_col.append(col)
    matrix.drop(columns=drop_col, inplace=True)

    matrix.to_csv(output_file)


def ngram_alloy_matrix(input_file1, input_file2, output_file, n):
    """
    Alloy matrix count the number of new ngram pairings. If a ngram A is present at time 1 and at time 2. If a ngram B
    is not present at time 1 but present at time 2, then AB is an alloy and its count will incremented by 1 for each
    new occurrence.
    :param input_file1: Path to input file
    :param input_file2: Path to input file
    :param output_file: Path to output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    """

    with zipfile.ZipFile(input_file1, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    text = ''
    for user in json_list:
        text += user['description'] + ' '

    ngram_set1 = set(get_ngram_list(text, n))

    with zipfile.ZipFile(input_file2, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    text = ''
    for user in json_list:
        text += user['description'] + ' '

    ngram_set2 = set(get_ngram_list(text, n))
    ngram_set_combine = ngram_set1.copy()
    ngram_set_combine.update(ngram_set2)

    alloy_matrix = pd.DataFrame(np.zeros((len(ngram_set_combine), len(ngram_set_combine))), columns=ngram_set_combine,
                                index=ngram_set_combine)

    user_description1 = get_user_description_dict(input_file1)
    user_description2 = get_user_description_dict(input_file2)

    for user in user_description1:
        if user in user_description2:
            user_ngram_list1 = get_ngram_list(user_description1[user], n)   # convert to set
            user_ngram_list2 = get_ngram_list(user_description2[user], n)
            for ngram2 in user_ngram_list2:
                if ngram2 not in user_ngram_list1:
                    for ngram1 in user_ngram_list1:
                        alloy_matrix[ngram1][ngram2] += 1

    drop_row = []
    for i, row in alloy_matrix.iterrows():
        if any(j > 0 for j in row):
            continue
        else:
            drop_row.append(i)
    alloy_matrix.drop(drop_row, inplace=True)

    drop_col = []
    for col in alloy_matrix:
        if any(j > 0 for j in alloy_matrix[col]):
            continue
        else:
            drop_col.append(col)
    alloy_matrix.drop(columns=drop_col, inplace=True)

    alloy_matrix.to_csv(output_file)


def ngram_transmutation_matrix(input_file1, input_file2, output_file, n):
    """
    Alloy matrix count the number of new ngram pairings. If a ngram A is present at time 1 but not at time 2.
    If a ngram B is not present at time 1 but present at time 2, then AB is an alloy and its count will incremented by
    1 for each new occurrence.
    :param input_file1: Path to input file
    :param input_file2: Path to input file
    :param output_file: Path to output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    """

    with zipfile.ZipFile(input_file1, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    text = ''
    for user in json_list:
        text += user['description'] + ' '

    ngram_set1 = set(get_ngram_list(text, n))

    with zipfile.ZipFile(input_file2, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    text = ''
    for user in json_list:
        text += user['description'] + ' '

    ngram_set2 = set(get_ngram_list(text, n))
    ngram_set_combine = ngram_set1.copy()
    ngram_set_combine.update(ngram_set2)

    transmutation_matrix = pd.DataFrame(np.zeros((len(ngram_set_combine), len(ngram_set_combine))), columns=ngram_set_combine,
                                index=ngram_set_combine)

    user_description1 = get_user_description_dict(input_file1)
    user_description2 = get_user_description_dict(input_file2)

    for user in user_description1:
        if user in user_description2:
            user_ngram_list1 = get_ngram_list(user_description1[user], n)
            user_ngram_list2 = get_ngram_list(user_description2[user], n)
            ngram_difference = [ngram for ngram in user_ngram_list1 + user_ngram_list2
                                if ngram not in user_ngram_list1 or ngram not in user_ngram_list2]
            for i in range(len(ngram_difference)):
                for j in range(i+1, len(ngram_difference)):
                        transmutation_matrix[ngram_difference[i]][ngram_difference[j]] += 1

    drop_row = []
    for i, row in transmutation_matrix.iterrows():
        if any(j > 0 for j in row):
            continue
        else:
            drop_row.append(i)
    transmutation_matrix.drop(drop_row, inplace=True)

    drop_col = []
    for col in transmutation_matrix:
        if any(j > 0 for j in transmutation_matrix[col]):
            continue
        else:
            drop_col.append(col)
    transmutation_matrix.drop(columns=drop_col, inplace=True)

    transmutation_matrix.to_csv(output_file)


def ngram_document_term_matrix(input_file, word_list_file, output_file, n):
    """
    The function writes the adjacency matrix to the output file, where the rows and columns are ngram and each cell is
    the number of users that has both the ngram in their description.
    :param input_file: Path to input file
    :param word_list_file: Path to the word list. This list contains the word for which you want to count the frequency
    :param output_file: Path to output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    """
    word_list = []
    with open(word_list_file) as file:
        for line in file:
            line = line.strip()
            word_list.append(line.lower())

    columns = ['id', 'description'] + word_list
    matrix = pd.DataFrame(np.zeros(shape=(1, len(columns))), columns=columns)
    temp = {word: 0 for word in word_list}
    with zipfile.ZipFile(input_file, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    for user in json_list:
        text = user['description']

        ngram_list = get_ngram_list(text, n)
        for word in ngram_list:
            if n == 1:
                if word[0] in word_list:
                    temp[word[0]] = 1
            else:
                if word in word_list:
                    temp[word] = 1
        matrix.loc[user['id_str']] = [user['id_str']] + [text] + list(temp.values())
    matrix.set_index('id', inplace=True)
    matrix.to_csv(output_file)


def string_present_or_absent(text, pattern):
    """

    :param text:
    :param pattern:
    :return:
    """
    pattern = re.compile(pattern)
    if re.search(pattern, text):
        return 1
    else:
        return 0


def cal_present_absent(input_file_folder_path, output_file_path, start_date, end_date, pattern):
    """

    :param input_file_folder_path:
    :param output_file_path:
    :param start_date:
    :param end_date:
    :param pattern:
    """

    user_present_absent_dict = {}
    curr_date = start_date
    length_of_file = 1000000

    pattern = re.compile(pattern)

    columns = ['date', 'p2p', 'p2a', 'a2p', 'a2a', 'total']
    matrix = pd.DataFrame(columns=columns)

    user_descriptions = reconstruct_user_description_dictionary(input_file_folder_path, length_of_file, curr_date)

    p2p = 0
    a2p = 0
    p2a = 0
    a2a = 0
    for user in user_descriptions:
        user_present_absent_dict[user] = 0
        if re.search(pattern, user_descriptions[user]):
            user_present_absent_dict[user] = 1
            p2p += 1
        else:
            a2a += 1

    total = p2p + a2a
    matrix = matrix.append(pd.Series([curr_date, p2p, p2a, a2p, a2a, total], index=columns), ignore_index=True)

    curr_date = dt.strptime(curr_date, '%Y_%m_%d')
    curr_date += datetime.timedelta(days=1)
    curr_date = dt.strftime(curr_date, '%Y_%m_%d')

    end_date = dt.strptime(end_date, '%Y_%m_%d')
    end_date += datetime.timedelta(days=1)
    end_date = dt.strftime(end_date, '%Y_%m_%d')

    while curr_date != end_date:
        input_f = input_file_folder_path + curr_date + '_profiles_' \
                  + str(length_of_file) + '.zip'

        print(input_f)

        if os.path.exists(input_f):
            user_descriptions = get_user_description_dict(input_f)
            for user in user_descriptions:

                if re.search(pattern, user_descriptions[user]):
                    if user not in user_present_absent_dict:
                        user_present_absent_dict[user] = 1
                        p2p += 1
                    if user_present_absent_dict[user] == 0:
                        user_present_absent_dict[user] = 1
                        a2p += 1
                        a2a -= 1
                else:
                    if user not in user_present_absent_dict:
                        user_present_absent_dict[user] = 0
                        a2a += 1
                    if user_present_absent_dict[user] == 1:
                        user_present_absent_dict[user] = 0
                        p2a += 1
                        p2p -= 1

            total = p2p + p2a + a2p + a2a
            matrix = matrix.append(pd.Series([curr_date, p2p, p2a, a2p, a2a, total], index=columns), ignore_index=True)

            p2p += a2p
            a2a += p2a
            a2p = 0
            p2a = 0

        curr_date = dt.strptime(curr_date, '%Y_%m_%d')
        curr_date += datetime.timedelta(days=1)
        curr_date = dt.strftime(curr_date, '%Y_%m_%d')

    matrix.set_index(columns[0], inplace=True)
    matrix.to_csv(output_file_path)
