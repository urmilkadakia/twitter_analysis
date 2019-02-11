import botometer
import api_keys
import csv
from util import parse_args


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
                if 'error' in result.keys():
                    output_file.writerow([str(screen_name), 'error'])
                    failed_count += 1
                    continue
                output_file.writerow([str(screen_name), str(result['cap']['universal'])])
            accounts.clear()
        count += 1
    print("Number of failed IDs:", failed_count)


def main():

    args = parse_args()
    bot_or_not(args.input_file1, args.output_file)


if __name__ == "__main__":
    main()
