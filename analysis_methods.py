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
import numpy as np
import zipfile
from datetime import datetime as dt
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
from reconstruction_methods import get_user_description_dict, reconstruct_user_description_dictionary, get_user_profile_dict

mpl.use('Agg')
nltk.download('punkt')
nltk.download('stopwords')
STOP_WORDS = set(stopwords.words('english'))


def _get_ngram_list(text, n=1, alpha_numeric_flag=False, stop_words_flag=False):
    """
    Returns the a list of ngram for the input text for the specified ngram type
    :param text: input text
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    :param alpha_numeric_flag: filter all non alpha numeric words. Default is false.
    :param stop_words_flag: filter all stop words. Default is false.
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
    if alpha_numeric_flag:
        tokens = [token for token in tokens if token.isalnum()]

    # filter out stop words
    if stop_words_flag:
        tokens = [w for w in tokens if w not in STOP_WORDS]

    ngram_list = list(ngrams(tokens, n))
    return ngram_list


def count_ngram_frequency(input_file, n=1, alpha_numeric_flag=False, stop_words_flag=False):
    """
    The function will count the frequencies for the given ngram
    :param input_file: Path to the input file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    :param alpha_numeric_flag: filter all non alpha numeric words. Default is false.
    :param stop_words_flag: filter all stop words. Default is false.
    :return: Returns the dictionary of ngram and frequency as the key value pairs sorted in the decreasing order.
    """
    with zipfile.ZipFile(input_file, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    text = ''
    for user in json_list:
        text += user['description'] + " "

    ngrams_list = _get_ngram_list(text, n, alpha_numeric_flag, stop_words_flag)
    # Get the frequency of each ngram in our corpus
    ngram_freq = collections.Counter(ngrams_list)
    return ngram_freq


def ngram_frequency_dist(input_file, output_file, n=1, alpha_numeric_flag=False, stop_words_flag=False):
    """
    The function counts the frequency of each ngram specified by the input parameter n and store the output as the csv
    at the output file location.
    :param input_file: Path to the input file
    :param output_file: Path to the output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigrams.
    :param alpha_numeric_flag: filter all non alpha numeric words. Default is false.
    :param stop_words_flag: filter all stop words. Default is false.
    """
    ngram_freq = count_ngram_frequency(input_file, n, alpha_numeric_flag, stop_words_flag)
    ngram_freq = ngram_freq.most_common()

    with open(output_file, "w+") as csvfile:
        writer = csv.writer(csvfile)
        for item in ngram_freq:
            writer.writerow(item)


def changing_ngram(input_file1, input_file2,  output_file, n=1, alpha_numeric_flag=0, stop_words_flag=0):
    """
    The function counts the difference between the frequencies of the two given files for the specified ngram and
    store it in the output file path folder.
    :param input_file1: Path to the input file 1
    :param input_file2: Path to the input file 2
    :param output_file: Path to the output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    :param alpha_numeric_flag: filter all non alpha numeric words. Default is false.
    :param stop_words_flag: filter all stop words. Default is false.
    """

    ngram_freq1 = count_ngram_frequency(input_file1, n, alpha_numeric_flag, stop_words_flag)
    ngram_freq1 = collections.OrderedDict(sorted(ngram_freq1.items()))
    ngram_freq2 = count_ngram_frequency(input_file2, n, alpha_numeric_flag, stop_words_flag)
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


def daily_ngram_collector(input_file_folder_path, output_file, number_of_users, start_date, end_date, n=1, cutoff_freq=5,
                          alpha_numeric_flag=0, stop_words_flag=0):
    """
    The function reads all the files generated between start date and end date and counts the ngram frequencies for all
    the ngrams in the file and finally combine them all in a date vise sorted csv file.
    :param input_file_folder_path: Path to the folder in which input files are stored
    :param output_file: Path to the output file
    :param number_of_users: To identify the input file as they are named based on the number of users
    :param start_date: Date from which function will start to calculate the ngram frequencies
    :param end_date: Date up to which function will calculate the ngram frequencies
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    :param cutoff_freq: The ngrams that has less frequency than the cut off frequency will not be included in the
                        output file. The default value is 5.
    :param alpha_numeric_flag: filter all non alpha numeric words. Default is false.
    :param stop_words_flag: filter all stop words. Default is false.
    """

    curr_date = start_date

    end_date = dt.strptime(end_date, '%Y_%m_%d')
    end_date += datetime.timedelta(days=1)
    end_date = dt.strftime(end_date, '%Y_%m_%d')

    while curr_date != end_date:
        input_f = os.path.join(input_file_folder_path, curr_date + '_profiles_' + str(number_of_users) + '.zip')
        if os.path.exists(input_f):
            ngram_freq = count_ngram_frequency(input_f, n, alpha_numeric_flag, stop_words_flag)
            ngram_freq = ngram_freq.most_common()

            # Creating the new row to add to the daily collector file
            # new_row1 = {'Date': re.findall(r'[0-9]{4}_[0-9]{2}_[0-9]{2}', input_f)[0]}
            new_row1 = {'Date': curr_date}
            # Extracting the Date from the filename
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

        curr_date = dt.strptime(curr_date, '%Y_%m_%d')
        curr_date += datetime.timedelta(days=1)
        curr_date = dt.strftime(curr_date, '%Y_%m_%d')


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


def ngram_histogram(input_file, output_file, n=1, cutoff_freq=5, alpha_numeric_flag=0, stop_words_flag=0):
    """
    The function to plot and store the histogram of the specified ngram and their frequencies for the ngrams which has
    frequency greater than cutoff_freq
    :param input_file: Path to input file
    :param output_file: Path to output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    :param cutoff_freq: The ngrams that has less frequency than the cut off frequency will not be included in the
                        output file.  The default value is 5.
    :param alpha_numeric_flag: filter all non alpha numeric words. Default is false.
    :param stop_words_flag: filter all stop words. Default is false.
    """
    ngram_freq = count_ngram_frequency(input_file, n, alpha_numeric_flag, stop_words_flag)
    ngram_freq = ngram_freq.most_common()

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


def ngram_adjacency_matrix(input_file, output_file, n=1, cut_off=5, alpha_numeric_flag=False, stop_words_flag=False):
    """
    The function writes the adjacency matrix to the output file, where the rows and columns are ngram and each cell is
    the number of users that has both the ngram in their description.
    :param input_file: Path to input file
    :param output_file: Path to output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    :param cut_off: The ngrams that has less frequency than the cut off frequency will not be included in the
                    output file. The default value is 5.
    :param alpha_numeric_flag: filter all non alpha numeric words. Default is false.
    :param stop_words_flag: filter all stop words. Default is false.
    """
    ngram_freq = count_ngram_frequency(input_file, n, alpha_numeric_flag, stop_words_flag)

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

        ngram_list = _get_ngram_list(text, n, alpha_numeric_flag, stop_words_flag)
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


def ngram_alloy_matrix(input_file1, input_file2, output_file, n=1, alpha_numeric_flag=False, stop_words_flag=False):
    """
    Alloy matrix count the number of new ngram pairings. If a ngram A is present at time 1 and at time 2. If a ngram B
    is not present at time 1 but present at time 2, then AB is an alloy and its count will incremented by 1 for each
    new occurrence.
    :param input_file1: Path to input file
    :param input_file2: Path to input file
    :param output_file: Path to output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    :param alpha_numeric_flag: filter all non alpha numeric words. Default is false.
    :param stop_words_flag: filter all stop words. Default is false.
    """

    with zipfile.ZipFile(input_file1, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    text = ''
    for user in json_list:
        text += user['description'] + ' '

    ngram_set1 = set(_get_ngram_list(text, n, alpha_numeric_flag, stop_words_flag))

    with zipfile.ZipFile(input_file2, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    text = ''
    for user in json_list:
        text += user['description'] + ' '

    ngram_set2 = set(_get_ngram_list(text, n, alpha_numeric_flag, stop_words_flag))
    ngram_set_combine = ngram_set1.copy()
    ngram_set_combine.update(ngram_set2)

    alloy_matrix = pd.DataFrame(np.zeros((len(ngram_set_combine), len(ngram_set_combine))), columns=ngram_set_combine,
                                index=ngram_set_combine)

    user_description1 = get_user_description_dict(input_file1)
    user_description2 = get_user_description_dict(input_file2)

    for user in user_description1:
        if user in user_description2:
            user_ngram_list1 = _get_ngram_list(user_description1[user], n, alpha_numeric_flag, stop_words_flag)
            user_ngram_list2 = _get_ngram_list(user_description2[user], n, alpha_numeric_flag, stop_words_flag)
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


def ngram_transmutation_matrix(input_file1, input_file2, output_file, n=1, alpha_numeric_flag=False,
                               stop_words_flag=False):
    """
    Alloy matrix count the number of new ngram pairings. If a ngram A is present at time 1 but not at time 2.
    If a ngram B is not present at time 1 but present at time 2, then AB is an alloy and its count will incremented by
    1 for each new occurrence.
    :param input_file1: Path to input file
    :param input_file2: Path to input file
    :param output_file: Path to output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    :param alpha_numeric_flag: filter all non alpha numeric words. Default is false.
    :param stop_words_flag: filter all stop words. Default is false.
    """

    with zipfile.ZipFile(input_file1, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    text = ''
    for user in json_list:
        text += user['description'] + ' '

    ngram_set1 = set(_get_ngram_list(text, n, alpha_numeric_flag, stop_words_flag))

    with zipfile.ZipFile(input_file2, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    text = ''
    for user in json_list:
        text += user['description'] + ' '

    ngram_set2 = set(_get_ngram_list(text, n, alpha_numeric_flag, stop_words_flag))
    ngram_set_combine = ngram_set1.copy()
    ngram_set_combine.update(ngram_set2)

    transmutation_matrix = pd.DataFrame(np.zeros((len(ngram_set_combine), len(ngram_set_combine))),
                                        columns=ngram_set_combine, index=ngram_set_combine)

    user_description1 = get_user_description_dict(input_file1)
    user_description2 = get_user_description_dict(input_file2)

    for user in user_description1:
        if user in user_description2:
            user_ngram_list1 = _get_ngram_list(user_description1[user], n, alpha_numeric_flag, stop_words_flag)
            user_ngram_list2 = _get_ngram_list(user_description2[user], n, alpha_numeric_flag, stop_words_flag)
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


def ngram_document_term_matrix(input_file, word_list_file, output_file, n=1, alpha_numeric_flag=False,
                               stop_words_flag=False):
    """
    The function writes the adjacency matrix to the output file, where the rows and columns are ngram and each cell is
    the number of users that has both the ngram in their description.
    :param input_file: Path to input file
    :param word_list_file: Path to the word list. This list contains the word for which you want to count the frequency
    :param output_file: Path to output file
    :param n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigram.
    :param alpha_numeric_flag: filter all non alpha numeric words. Default is false.
    :param stop_words_flag: filter all stop words. Default is false.
    """
    word_list = []
    with open(word_list_file) as file:
        for line in file:
            line = line.strip()
            word_list.append(line.lower())

    columns = ['id', 'description'] + word_list
    matrix = pd.DataFrame(columns=columns)
    temp = {word: 0 for word in word_list}
    with zipfile.ZipFile(input_file, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    for user in json_list:
        text = user['description']

        ngram_list = _get_ngram_list(text, n, alpha_numeric_flag, stop_words_flag)
        for word in ngram_list:
            if n == 1:
                if word[0] in word_list:
                    temp[word[0]] = 1
            else:
                if word in word_list:
                    temp[word] = 1
        matrix = matrix.append(pd.Series([user['id_str']] + [text] + list(temp.values()), index=columns),
                               ignore_index=True)

    matrix.set_index('id', inplace=True)
    matrix.to_csv(output_file)


def calculate_present_absent(input_file_folder_path, output_file, number_of_users, start_date, end_date, pattern):
    """
    This function calculates the number of times the twitter user has added ot removed the pattern defined here in
    his/her description. There are total 4 possible cases:
    1. User has the given pattern in the description on day 1 as well as on the day 2 (present to present = p2p)
    2. User did not has the given pattern in the description on day 1 but has on the day 2 (absent to present = a2p)
    3. User has the given pattern in the description on day 1 but not on the day 2 (present to absent = p2a)
    4. User did not has the given pattern in the description on day 1 as well as on the day 2 (absent to absent = a2a)
    The function stores the count of the these 4 cases as well the total of them for each date in between the
    start date and the end date in the output file.
    :param input_file_folder_path: Path to the folder in which input files are stored
    :param output_file: Path to the output file
    :param number_of_users: To identify the input file as they are named based on the number of users
    :param start_date: Date from which function will start to calculate the ngram frequencies
    :param end_date: Date up to which function will calculate the ngram frequencies
    :param pattern: Pattern to search for in the description
    """

    user_present_absent_dict = {}
    curr_date = start_date

    pattern = re.compile(pattern)

    columns = ['date', 'p2p', 'p2a', 'a2p', 'a2a', 'total']
    matrix = pd.DataFrame(columns=columns)

    user_descriptions = reconstruct_user_description_dictionary(input_file_folder_path, number_of_users, curr_date)

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
        input_f = os.path.join(input_file_folder_path, curr_date + '_profiles_' + str(number_of_users) + '.zip')

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
    matrix.to_csv(output_file)


def _generate_state_dictionary():
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


def get_locations(input_file, output_file):
    """
    The function writes the user id and his/her us state name in the output file based on the the value of location key
    in the user information and state_locations mapping. If function does not find the location in the state_locations
    mapping then N/A will be written against the user id.
    :param input_file: Path to input file
    :param output_file: Path to output file
    """
    with zipfile.ZipFile(input_file, 'r') as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                json_list = json.load(f)

    state_locations = _generate_state_dictionary()
    location_dict = {}
    for item in json_list:
        location_dict[item['id']] = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?]', item['location'].lower())
    state_flag = 0
    us_flag = 0
    cnt = 0
    for user_id in location_dict:
        for item in location_dict[user_id]:
            for state in state_locations:
                if item == state:
                    location_dict[user_id] = state
                    state_flag = 1
                    break
            if state_flag == 1:
                break
        if state_flag == 0:
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
                location_dict[user_id] = 'N/A'
                cnt += 1

    with open(output_file, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['user_id', 'location'])
        for data in location_dict:
            writer.writerow([data, location_dict[data]])


def entities_count_difference(input_file1, input_file2, output_file):
    """
    The function calculates the difference between the followers count, following count, total tweets and total likes
    of each user between the two input files that  are generate at two different time
    :param input_file1: Path to user profiles file of a specific date (earlier date)
    :param input_file2: Path to user profiles file of a specific date (later date)
    :param output_file: Path to output file
    """

    user_profiles_1 = get_user_profile_dict(input_file1)
    user_profiles_2 = get_user_profile_dict(input_file2)

    entity_count_difference = pd.DataFrame(columns=['user_id', 'tweet_diff', 'follower_diff', 'following_diff',
                                                    'like_diff'], index=None)

    for user in user_profiles_1:
        if user in user_profiles_2:
            tweet_diff = user_profiles_2[user]['statuses_count'] - user_profiles_1[user]['statuses_count']
            follower_diff = user_profiles_2[user]['followers_count'] - user_profiles_1[user]['followers_count']
            following_diff = user_profiles_2[user]['friends_count'] - user_profiles_1[user]['friends_count']
            like_diff = user_profiles_2[user]['favourites_count'] - user_profiles_1[user]['favourites_count']

            entity_count_difference.loc[user] = [user, tweet_diff, follower_diff, following_diff, like_diff]

    # Setting the user_id as the index
    entity_count_difference.set_index(['user_id'], inplace=True)

    entity_count_difference.to_csv(output_file)


def description_change_frequency(input_file_folder_path, output_file, number_of_users, start_date, end_date):
    """
    The function calculates and store the number of times the user has made changes in his/her description.
    :param input_file_folder_path: Path where all the daily user profiles are stored
    :param output_file: Path to output file
    :param number_of_users: To identify the input file as they are named based on the number of users
    :param start_date: Date from which function will start to count the change
    :param end_date: Date up to which function will count the change
    """

    base_flag = 1
    base_continue_flag = 0
    user_change_freq = {}
    curr_date = start_date

    end_date = dt.strptime(end_date, '%Y_%m_%d')
    end_date += datetime.timedelta(days=1)
    end_date = dt.strftime(end_date, '%Y_%m_%d')

    while curr_date != end_date:
        input_f = os.path.join(input_file_folder_path, curr_date + '_profiles_' + str(number_of_users) + '.zip')
        if os.path.exists(input_f):
            with zipfile.ZipFile(input_f, 'r') as z:
                for filename in z.namelist():
                    with z.open(filename) as f:
                        if base_flag:
                            base_json_list = json.load(f)
                            base_flag = 0
                            base_continue_flag = 1
                        else:
                            compare_json_list = json.load(f)
                if base_continue_flag == 1:
                    base_continue_flag = 0
                    continue

            # Generating dictionaries to compare the user description between two time stamps
            # Key is user id and value is the description of user
            base_description = {}
            for user in base_json_list:
                base_description[user['id']] = user['description']

            compare_description = {}
            for user in compare_json_list:
                compare_description[user['id']] = user['description']

            # Checking user has change its description or not if yes replace base case with new description for to capture
            # Future changes and increment the user change frequency by 1
            for user_id in base_description:
                if user_id in compare_description:
                    if user_id not in user_change_freq:
                        user_change_freq[user_id] = 0
                    if base_description[user_id] != compare_description[user_id]:
                        base_description[user_id] = compare_description[user_id]
                        user_change_freq[user_id] += 1

        curr_date = dt.strptime(curr_date, '%Y_%m_%d')
        curr_date += datetime.timedelta(days=1)
        curr_date = dt.strftime(curr_date, '%Y_%m_%d')

    # Store the user change frequency dictionary as a csv file
    with open(output_file, "w+") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['user_id', 'change_frequency'])
        for key, value in user_change_freq.items():
            writer.writerow([key, value])