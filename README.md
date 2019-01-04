# twitter_analysis

A python project to study patterns in identity change as revealed by the edits users make to their online profiles using data from Twitter.

## Install instructions

### Creating twitter developer account
- You need to have a twitter account. If you don't have create one.
- Follow the instruction on the page [developer portal](https://developer.twitter.com/en/docs/basics/developer-portal/overview) and click on **Apply for devepoler account**.
- From the dashboard click on **your username -> Apps**. If you want to use an **existing app** select one or click on **Create an app**.
- Fill the application form and click on **Create**.

### Updating the api_keys.py file
- In the Dashboard of your **twitter developer account->App** menu select your app. Under the section **Keys and tokens** you will find your api keys and access tokens.
- Copy and paste the keys and tokens to the respective variables and save the file.


### installing Tweepy
- **Tweepy** is a wrapper around the Twitter Rest API.
- Install using pip run: `pip install tweepy`
- Install using anaconda Cloud run: ` conda install -c conda-forge tweepy`
- For more information on tweepy visit: [Tweepy Documentation](https://tweepy.readthedocs.io/en/3.7.0/index.html#).

### Botometer
- Botometer checks the activity of a Twitter account and gives it a score based on how likely the account is to be a bot. Higher scores are more bot-like. 
- For more information regarding the botometer score please visit: [botometer](https://botometer.iuni.iu.edu/#!/)
- **Instaling Botometer**
```
pip install botometer
```
- **Python dependencies**:
  - **tweepy** install as mentioned above.
  - **requests** install using following command: `pip install requests`.

### Mashape Market API key
- Botometer runs on the Mashape server, so to use botomerter you must signup for a free account to get the Mashape secret key.
- Visit [API endpoint page](https://market.mashape.com/OSoMe/botometer) and look in the **Request Example -> X-Mashape-Key** to get the secret key.


## Usage
1. **profile_collector.py**
   - This code takes the list the userids as input and return 2 files. The first file contains the user lookups and second file contains the a list of userids that are are not unknown, suspended or deleted.
   - Use the following command to run scraper.py on terminal:
   ```
   python profile_collector.py -i <input file> -o <output file folder path> -f <json|csv> -u <1|0>
   ```
   - Pass `-h` as argument for help menu.
   
 2. **botornot.py**
    - This code returns a file which contains the botometer score for each user.
    - Use the following command to run botornot.py on terminal:
    ```
    python botornot.py -i <input file> -o <output file>
    ```
    - Pass `-h` as argument for the help menu.
    
 3. **Ngram frequencies and summary stastistics**
    - This code returns a file that contains the frequency of specified ngram along with the user description length histogram.
    ```
    python ngram_frequency.py -i <input file> -o <output file> -n <1|2|3|...>
    ```
    - Here n refers to the type of ngram, 1 for unigram, 2 for bigram, 3 for trigram etc.
    - Pass `-h` as argument for the help menu.
  
  4. **Crontab**
     - The crontab runs the given tasks in the background at specific times. We can use the crontab to scrape the user profiles daily.
     - Follow the below commands to setup the crontab on your system:
       - open terminal
       - Use command `crontab -e` to open or edit the crontab file.
       - If asked to select an editor choose according to your preference. **Nano** is the easiest.
       - Use arrow keys to reach to the bottom of the file.
       - Lines in the crontab has the following format:
       ```
       minute(0-59) hour(0-23) day(1-31) month(1-12) weekday(0-6) command
       ```
       - Use * to match any value.
       -   Write the follwoing command in the file to run the profile collector daily at 9:59 am:
       ```
       59 9 * * * cd <path where all the files are stored> && /usr/bin/python <path to profile_collector.py> -i <input file> -o <output file folder path> -f <json|csv> -u <1|0>
       ```
       - The location or the name of the python interpreter may vary.

### License
GNU


