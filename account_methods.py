import os
import botometer
import api_keys
import csv
import zipfile
import json
import re
import glob
import pandas as pd
from util import generate_state_dictionary, get_user_profile_dict, date_sort


def bot_or_not(input_file_path, output_file_path):
    """
    The function decides whether each user id is a bot machine or human being and stores the user id and botometer
    scores in the input
    :param input_file_path: Path to input file
    :param output_file_path: Path to output file
    """
    input_file = open(input_file_path)
    output_file = csv.writer(open(output_file_path, "w+"))

    mashape_key = api_keys.mashape_key
    twitter_app_auth = {
        'consumer_key': api_keys.api_key,
        'consumer_secret': api_keys.api_secret_key,
        'access_token': api_keys.access_token,
        'access_token_secret': api_keys.access_token_secret,
    }
    bom = botometer.Botometer(wait_on_ratelimit=True,
                              mashape_key=mashape_key,
                              **twitter_app_auth)

    count = 1
    failed_count = 0
    accounts = []
    length_of_file = sum(1 for _ in input_file)

    input_file = open(input_file_path)
    for line in input_file:
        accounts.append(int(float(line.strip())))
        # Call the lookup function for a list 100 user IDs
        if count % 100 == 0 or count == length_of_file:
            for screen_name, result in bom.check_accounts_in(accounts):
                # print(screen_name,result)
                if 'error' in result.keys():
                    output_file.writerow([str(screen_name), 'error'])
                    failed_count += 1
                    continue
                output_file.writerow([str(screen_name), str(result['cap']['universal'])])
            accounts.clear()
        count += 1
    print("Number of failed IDs:", failed_count)


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
                # print(location_dict[user_id])
                location_dict[user_id] = 'not in usa'
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


def description_change_frequency(input_file_path, output_file):
    """
    The function calculates and store the number of times the user has made changes in his/her description.
    :param input_file_path: Path where all the daily user profiles are stored
    :param output_file: Path to output file
    """

    base_flag = 1
    base_continue_flag = 0
    user_change_freq = {}
    for file in sorted(glob.glob(os.path.join(input_file_path, '*.zip')), key=date_sort):
        with zipfile.ZipFile(file, 'r') as z:
            for filename in z.namelist():
                # print(filename)
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

        # checking user has change its description or not if yes replace base case with new description for to capture
        # future changes and increment the user change frequency by 1
        for user_id in base_description:
            if user_id in compare_description:
                if user_id not in user_change_freq:
                    user_change_freq[user_id] = 0
                if base_description[user_id] != compare_description[user_id]:
                    base_description[user_id] = compare_description[user_id]
                    user_change_freq[user_id] += 1

    # Store the user change frequency dictionary as a csv file
    with open(output_file, "w+") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['user_id', 'location'])
        for key, value in user_change_freq.items():
            writer.writerow([key, value])









