# twitter_analysis

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

### botometer

### mashable api keys


### Command to run the codes
1. **scraper.py**
   - This code takes the list the userids as input and return 2 files. The first file contains the user lookups and second file contains the a list of userids that are are not unknown, suspended or deleted.
   - Use the following command to run scraper.py on terminal:
   ```
   python scraper.py -i <input file> -o <output file folder path> -f <json|csv> -u <1|0>
   ```
   - Pass `-h` as argument for help menu.
   
 2. **botornot.py**
    - This code returns a file which contains the botometer score for each user.
    - Use the following command to run botornot.py on terminal:
    ```
    python botornot.py -i <input_file> -o <outputfile>
    ```
    - Pass `-h` as argument for the help menu.
    - For more information regarding the botometer score please visit: [botometer](https://botometer.iuni.iu.edu/#!/)
    
 3. **ngram frequencies and summary stastistics**
    - This code returns a file that contains the frequency of specified ngram along with the user description length histogram.
    ```
    python ngram_frequency.py -i <input_file> -o <output_file> -n <1|2|3|...>
    ```
    - Here n refers to the type of ngram, 1 for unigram, 2 for bigram, 3 for trigram etc.
    - Pass `-h` as argument for the help menu.

### setup crontab

### License
GNU



