### requirements install botometer client and mashape API key
### command: pip install botometer
### ref: https://github.com/IUNetSci/botometer-python, https://market.mashape.com/OSoMe/botometer

### Rate limit : Our rate limit is set at 2,000 requests per day, per user

import botometer
import api_keys
import csv
from config import parse_args2


def bot_or_not(inputfile, outputfile):
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
    for line in inputfile:
        accounts.append(int(line.strip()))
        # Call the lookup function for a list 100 user IDs
        if count % 100 == 0:
            for screen_name, result in bom.check_accounts_in(accounts):
                if 'error' in result.keys():
                    outputfile.writerow([str(screen_name), 'error'])
                    failed_count += 1
                    continue
                outputfile.writerow([str(screen_name), str(result['cap']['universal'])])
            accounts.clear()
            print(count)
        count += 1
    print(failed_count)


def main():

    args = parse_args2()
    inputfile = open(args.inputfile)
    outputfile = csv.writer(open(args.outputfile))

    bot_or_not(inputfile, outputfile)


if __name__ == "__main__":
    main()

