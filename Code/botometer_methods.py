import botometer
import csv
from datetime import datetime as dt
import logging
import requests
import tweepy
import api_keys
from logger import log_twitter_error


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

filename = 'Logs/botometer_methods_' + dt.now().strftime("%m_%Y") + '.log'
file_handler = logging.FileHandler(filename)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def bot_or_not(input_file_path, output_file_path):
    """
    The function decides whether each user id is a bot machine or human being and stores the user id and botometer
    scores in the input
    :param input_file_path: Path to input file
    :param output_file_path: Path to output file
    """
    input_file = open(input_file_path)
    output_file = csv.writer(open(output_file_path, "w+"))

    try:
        auth = tweepy.OAuthHandler(api_keys.api_key, api_keys.api_secret_key)
        auth.set_access_token(api_keys.access_token, api_keys.access_token_secret)
        auth.get_authorization_url()
    except tweepy.TweepError as e:
        log_twitter_error(logger, e)
        del auth
        exit(1)

    twitter_app_auth = {
        'consumer_key': api_keys.api_key,
        'consumer_secret': api_keys.api_secret_key,
        'access_token': api_keys.access_token,
        'access_token_secret': api_keys.access_token_secret,
    }
    bom = botometer.Botometer(wait_on_ratelimit=True,
                              mashape_key=api_keys.mashape_key,
                              **twitter_app_auth)

    count = 1
    failed_count = 0
    accounts = []
    length_of_file = sum(1 for _ in input_file)

    input_file = open(input_file_path)
    for line in input_file:
        accounts.append(int(float(line.strip())))

        # Call the lookup function for a list of 100 user IDs
        if count % 100 == 0 or count == length_of_file:
            try:
                for screen_name, result in bom.check_accounts_in(accounts):
                    if 'error' in result.keys():
                        output_file.writerow([str(screen_name), 'error'])
                        failed_count += 1
                        continue
                    output_file.writerow([str(screen_name), str(result['cap']['universal'])])
            except requests.exceptions.HTTPError as e:
                logger.error("invalid Botometer(RapidAPI mashape application) authentication key")
                exit(1)
            accounts.clear()
        count += 1
    logger.info('Number of successful ID:' + str(length_of_file - failed_count) + ' and '
                + 'Number of failed ID:' + str(failed_count))

