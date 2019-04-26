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
1. **twitter_scraper.generate_file()**
   - Method to send the api calls to twitter and get the user data in the json format. The method stores all the
     data in the user specified format(json or csv) in the zip file format to reduce the storage space and also
     prints out the list of failed user ids.
   - Parameters:
     - format: format of output file json or csv
     - size: Specify 1 if you do not want to store tweets with profile information. This will reduce file size
     - clean_userid: a flag to store the list of user ids for which we get the data without any error. Pass 1
                     to store the list as csv file
   - Use the following command to run profile_collector.py on terminal:
   ```
   python profile_collector.py -i1 <input file> -o <output file folder path> -f <json|csv> -s <1|0> -u <1|0>
   ```
   - Pass `-h` as argument for help menu.
2. **twitter_scraper.reconstruct_data()**
   - This function calls the reconstruct_data_dictionary function to get the updated user profiles dictionary and
     store it as a zip file in the user specified location.
   
 3. **account_methods.bot_or_not()**
    - This code returns a file which contains the botometer score for each user.
    - Use the following command to run botornot.py on terminal:
    - Parameters:
      - input_file: Path to the input file
      - output_file: Path to the output file
    - return: returns a file which contains the botometer score for each user.

    
 4. **ngram_methods.count_ngram_frequency()**
    - The function will count the frequencies for the given ngram
    - Parameters:
      - input_file: Path to the input file
      - n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
              represents unigrams.
    - return: Returns the dictionary of ngram and frequency as the key value pairs sorted in the decreasing order.  
    
 5. **ngram_methods.ngram_frequency_dist()**
     - The function counts the frequency of each ngram specified by the input parameter n and store the output as the csv at the output file location.
     - Parameters:
       - input_file: Path to the input file
       - output_file: Path to the output file
       - n represents the n in n-gram which is a contiguous sequence of n item
 6. **ngram_methods.changing_ngram()**
     - The function counts the difference between the frequencies of the two given files for the specified ngram and store it in the output file path folder.
     - Parameteres:
       - input_file1: Path to the input file 1
       - input_file2: Path to the input file 2
       - output_file: Path to the output file
       - n: n represents the n in n-gram which is a contiguous sequence of n items.
 7. **ngram_methods.daily_ngram_collector()**
     - The function reads all the files that are in the input file folder and counts the ngram frequencies for all the ngrams in the file and finally combine them all in a date vise sorted csv file.
     - Parameters:
       - input_file_path: Path to the folder in which input files are stored
       - output_file: Path to the output file
       - n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
            represents unigrams.
       - cutoff_freq: The ngrams that has less frequency than the cut off frequency will not be included in the
                      output file. The default value is 5.
 8. **ngram_methods.char_length_histogram()**
     - The function to plot and store the histogram of the character length description of each user in the file
     - Parameters:
       - input_file: Path to the input file
       - output_file: Path to the output file
 9. **ngram_methods.ngram_histogram()**
     - The function to plot and store the histogram of the specified ngram and their frequencies for the ngrams which has frequency greater than cutoff_freq
     - Parameters:
       - input_file: Path to input file
       - output_file: Path to output file
       - n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
            represents unigrams.
       - cutoff_freq: The ngrams that has less frequency than the cut off frequency will not be included in the
                      output file. The default value is 5.
 10. **ngram_methods.ngram_adjacency_matrix()**
    - The function writes the adjacency matrix to the output file, where the rows and columns are ngram and each cell is
      the number of users that has both the ngram in their description.
    - Parameters:
      - input_file: Path to input file
      - output_file: Path to output file
      - n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
            represents unigrams.
      - cutoff_freq: The ngrams that has less frequency than the cut off frequency will not be included in the
                      output file. The default value is 5.
 11. **ngram.methods.ngram_alloy_matrix()**
     - Alloy matrix count the number of new ngram pairings. If a ngram A is present at time 1 and at time 2. If a ngram B is not present at time 1 but present at time 2, then AB is an alloy and its count will incremented by 1 for each new occurrence.
     - Parameter:
       - input_file1: Path to input file 1
       - input_file2: Path to input file 2
       - output_file: Path to output file
       - n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
            represents unigrams.
 12. **ngram_methods.ngram_transmutation_matrix()**
     - Alloy matrix count the number of new ngram pairings. If a ngram A is present at time 1 but not at time 2.
       If a ngram B is not present at time 1 but present at time 2, then AB is an alloy and its count will incremented by 1 for each new occurrence.
     - Parameters:
       - input_file1: Path to input file 1
       - input_file2: Path to input file 2
       - output_file: Path to output file
       - n: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which
            represents unigrams.
       - cutoff_freq: The ngrams that has less frequency than the cut off frequency will not be included in the
                      output file. The default value is 5.
 13. **account_methods.get_locations()**
     - The function writes the user id and his/her us state name in the output file based on the the value of location key in the user information and state_location dictionary. If function does not find the location in the state_locations dictionary then not in usa will be written against the user id.
     - Parameters:
       - input_file1: Path to input file
       - input_file2: Path to the usa location file 
       - output_file: Path to output file
 14. **account_methods.entities_count_difference()**
     - The function calculates the difference between the followers count, following count, total tweets and total likes        of each user between the two input files that  are generate at two different time.
     - Parameters:
       - input_file1: Path to user profiles file of a specific date (earlier date)
       - input_file2: Path to user profiles file of a specific date (later date)
       - output_file: Path to output file
 15. **account_methods.description_change_frequency()**
     - The function calculates and store the number of times the user has made changes in his/her description.
     - Parameters:
       - input_file_path: Path where all the daily user profiles are stored
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



