### requirements install botometer client and mashape API key
### command: pip install botometer
### ref: https://github.com/IUNetSci/botometer-python, https://market.mashape.com/OSoMe/botometer

### Rate limit : Our rate limit is set at 2,000 requests per day, per user

import botometer
import api_keys
import csv
from config import parse_args2


def bot_or_not(inputfilepath, outputfilepath):

    inputfile = open(inputfilepath)
    outputfile = csv.writer(open(outputfilepath, "w+"))

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
    length_of_file = sum(1 for line in inputfile)

    inputfile = open(inputfilepath)
    for line in inputfile:
        accounts.append(int(float(line.strip())))
        # Call the lookup function for a list 100 user IDs
        if count % 100 == 0 or count == length_of_file:
            for screen_name, result in bom.check_accounts_in(accounts):
                if 'error' in result.keys():
                    outputfile.writerow([str(screen_name), 'error'])
                    failed_count += 1
                    continue
                outputfile.writerow([str(screen_name), str(result['cap']['universal'])])
            accounts.clear()
            # print(count)
        count += 1
    print(failed_count)


def main():

    args = parse_args2()
    bot_or_not(args.inputfile, args.outputfile)


if __name__ == "__main__":
    main()

