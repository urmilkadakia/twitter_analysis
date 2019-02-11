# twitter_analysis

A python project to study patterns in identity change as revealed by the edits users make to their online profiles using data from Twitter.

## Install instructions

### Creating a Twitter developer account
- You need to have a twitter account. If you don't have to create one.
- Follow the instruction on the page [developer portal](https://developer.twitter.com/en/docs/basics/developer-portal/overview) and click on **Apply for developer account**.
- From the dashboard click on **your username -> Apps**. If you want to use an **existing app** select one or click on **Create an app**.
- Fill the application form and click on **Create**.

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
  - **requests** install using the following command: `pip install requests`.

### Mashape Market API key
- Botometer runs on the Mashape server, so to use botomerter you must signup for a free account to get the Mashape secret key.
- Visit [API endpoint page](https://market.mashape.com/OSoMe/botometer) and look in the **Request Example -> X-Mashape-Key** to get the secret key.

### Updating the api_keys.py file
- In the Dashboard of your **twitter developer account -> App** menu select your app. Under the section **Keys and tokens** you will find your API keys and access tokens.
- Visit [API endpoint page](https://market.mashape.com/OSoMe/botometer) and look in the **Request Example -> X-Mashape-Key** to get the secret Mashape key for the botometer.
- Copy and paste the keys and tokens to the respective variables and save the file.


## Usage
1. **profile_collector.py**
   - This code takes the list the userids as input and return 2 files. The first file contains the user lookups and second file contains the a list of userids that are are not unknown, suspended or deleted.
   - Use the following command to run profile_collector.py on terminal:
   ```
   python profile_collector.py -i1 <input file> -o <output file folder path> -f <json|csv> -u <1|0>
   ```
   - Pass `-h` as argument for help menu.
   
 2. **botornot.py**
    - This code returns a file which contains the botometer score for each user.
    - Use the following command to run botornot.py on terminal:
    ```
    python botornot.py -i1 <input file> -o <output file>
    ```
    - Pass `-h` as argument for the help menu.
    
 3. **ngram_analysis.count_ngram_frequency()**
    - The function will count the frequencies for the given ngram
    - Parameters:
      - input_file: Path to the input file
      - n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigrams.
    - return: Returns the dictionary of ngram and frequency as the key value pairs sorted in the decreasing order.  
    
  4. **ngram_analysis.ngram_frequency_dist()**
     - The function counts the frequency of each ngram specified by the input parameter n and store the output as the csv at the output file location.
     - Parameters:
       - input_file: Path to the input file
       - output_file: Path to the output file
       - n represents the n in n-gram which is a contiguous sequence of n item
  5. **ngram_analysis.changing_ngram()**
     - The function counts the difference between the frequencies of the two given files for the specified ngram and store it in the output file path folder.
     - Parameteres:
       - input_file1: Path to the input file 1
       - input_file2: Path to the input file 2
       - output_file: Path to the output file
       - n: n represents the n in n-gram which is a contiguous sequence of n items.
    6. **ngram_analysis.daily_ngram_collector()**
       - The function reads all the files that are in the input file folder and counts the ngram frequencies for all the ngrams in the file and finally combine them all in a date vise sorted csv file.
       - Parameters:
         - input_file_path: Path to the folder in which input files are stored
         - output_file: Path to the output file
         - n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigrams.
         - cutoff_freq: The ngrams that has less frequency than the cut off frequency will not be included in the
                        output file. The default value is 5.
      7. **ngram_analysis.char_length_histogram()**
         - The function to plot and store the histogram of the character length description of each user in the file
         - Parameters:
           - input_file: Path to the input file
           - output_file: Path to the output file
       8. **ngram_analysis.ngram_histogram()**
          - The function to plot and store the histogram of the specified ngram and their frequencies for the ngrams which has frequency greater than cutoff_freq
          - Parameters:
            - input_file: Path to input file
            - output_file: Path to output file
            - n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
                 represents unigrams.
            - cutoff_freq: The ngrams that has less frequency than the cut off frequency will not be included in the
                           output file. The default value is 5.
        9. **ngram_analysis.get_locations()**
           - The function writes the user id and his/her us state name in the output file based on the the value of location key in the user information and state_location dictionary. If function does not find the location in the state_locations dictionary then not in usa will be written against the user id.
           - Parameters:
             - input_file1: Path to input file
             - input_file2: Path to the usa location file
             - output_file: Path to output file
    
  ## Crontab
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
Apache



