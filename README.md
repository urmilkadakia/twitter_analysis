# twitter_analysis

A python project to study patterns in identity change as revealed by the edits users make to their online profiles using 
data from Twitter.

## Install instructions

### Creating a Twitter developer account
- You need to have a twitter account. If you don't have to create one.
- Follow the instruction on the page 
[developer portal](https://developer.twitter.com/en/docs/basics/developer-portal/overview) and click on 
**Apply for developer account**.
- From the dashboard click on **your username -> Apps**. 
If you want to use an **existing app** select one or click on  **Create an app**.
- Fill the application form and click on **Create**.

### Tweepy
- **Tweepy** is a wrapper around the Twitter Rest API.
- For more information on tweepy visit: [Tweepy Documentation](https://tweepy.readthedocs.io/en/3.7.0/index.html#).

### Botometer
- Botometer checks the activity of a Twitter account and gives it a score based on how likely the account is to be a 
bot. Higher scores are more bot-like. 
- For more information regarding the botometer score please visit: [botometer](https://botometer.iuni.iu.edu/#!/)

### Mashape Market API key
- Botometer runs on the Mashape server, so to use botomerter you must signup for a free account to get the Mashape 
secret key.
- Visit [API endpoint page](https://market.mashape.com/OSoMe/botometer) and look in the **Request Example -> 
X-Mashape-Key** to get the secret key.

### Updating the api_keys.py file
- In the Dashboard of your **twitter developer account -> App** menu select your app. Under the section **Keys and 
tokens** you will find your API keys and access tokens.
- Visit [API endpoint page](https://market.mashape.com/OSoMe/botometer) and look in the **Request Example -> 
X-Mashape-Key** to get the secret Mashape key for the botometer.
- Copy and paste the keys and tokens to the respective variables and save the file.

### Downloading and installing dependencies
- To download and install dependencies run the following command:
    ```
    sh install.sh
    ```

## Usage
1. **tweepy_methods.twitter_scraper(input_file, output_file, format, size, clean_userid)**
    - Method to send the api calls to twitter and get the user data in the json format. The method stores all the data 
    in the user specified format(json or csv) in the zip file format to reduce the storage space and also prints out 
    the list of failed user ids.
    - **Parameters**:
        - **input_file**: Path to the input file
        - **output_file**: Path to the output file
        - **format**: format of output file json or csv
        - **size_flag**: Specify True if you do not want to store tweets with profile information. This will reduce 
        file size
        - **clean_userid_flag**: A flag to store the list of user ids for which we get the data without any error. 
        Pass True to store the list as csv file

2. **twitter_methods.get_twitter_user_id_from_screen_name(input_file_path, output_file_path)**
    - Method to get the twitter user_id from the screen name
    - **Parameters**:
        - **input_file_path**: path to input file that contains the list of screen name
        - **output_file_path**: path to the output file where the corresponding the user_ids are saved

3. **analysis_methods.count_ngram_frequency(input_file, ngram, alpha_numeric_flag, stop_words_flag)**
    - The function will count the frequencies for the given ngram
    - **Parameters**:
        - **input_file**: Path to the input file
        - **ngram**: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 
        which represents unigrams.
        - **alpha_numeric_flag**: Filter all non alpha numeric words. Default is false.
        - **stop_words_flag**: Filter all stop words. Default value is False.
    - **return**: Returns the dictionary of ngram and frequency as the key value pairs sorted in the decreasing order.  
    
4. **analysis_methods.ngram_frequency_dist(input_file, output_file, ngram, alpha_numeric_flag, stop_words_flag)**
    - The function counts the frequency of each ngram specified by the input parameter ngram and store the output as 
    the csv at the output file location.
    - **Parameters**:
        - **input_file**: Path to the input file
        - **output_file**: Path to the output file
        - **ngram**: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 
        which represents unigrams.
        - **alpha_numeric_flag**: Filter all non alpha numeric words. Default is false.
        - **stop_words_flag**: Filter all stop words. Default value is False.

5. **analysis_methods.changing_ngram(input_file1, input_file2, output_file, ngram, alpha_numeric_flag, 
stop_words_flag)**
     - The function counts the difference between the frequencies of the two given files for the specified ngram and 
     store it in the output file.
     - **Parameters**:
        - **input_file1**: Path to the input file 1
        - **input_file2**: Path to the input file 2
        - **output_file**: Path to the output file
        - **ngram**: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which 
        represents unigrams.
        - **alpha_numeric_flag**: Filter all non alpha numeric words. Default is false.
        - **stop_words_flag**: Filter all stop words. Default value is False.

6. **analysis_methods.daily_ngram_collector(input_file, output_file, start_date, end_date, ngram, cutoff_freq, 
alpha_numeric_flag, stop_words_flag)**
     - The function reads all the files that are in the input file folder and has a date between start_date and end_date 
     and counts the ngram frequencies for all the ngrams in the file and finally combine them all in a date vise sorted 
     csv file.
     - **Parameters**:
        - **input_file_folder_path**: Path to the folder in which input files are stored        
        - **output_file**: Path to the output file
        - **start_date**: Date from which function will start to calculate
        - **end_date**: Date up to which function will calculate
        - **ngram**: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which 
        represents unigrams.
        - **cutoff_freq**: The ngrams that has less frequency than the cutoff frequency will not be included in the 
        output file. The default value is 5.
        - **alpha_numeric_flag**: Filter all non alpha numeric words. Default is false.
        - **stop_words_flag**: Filter all stop words. Default value is False.
       
7. **analysis_methods.char_length_histogram(input_file, output_file)**
     - The function to plot and store the histogram of the character length description of each user in the file
     - **Parameters**:
        - **input_file**: Path to the input file
        - **output_file**: Path to the output file
        
8. **analysis_methods.ngram_histogram(input_file, output_file, ngram, cutoff_freq, alpha_numeric_flag, 
stop_words_flag)**
     - The function to plot and store the histogram of the specified ngram and their frequencies for the ngrams 
     which has frequency greater than cutoff_freq
     - **Parameters**:
        - **input_file**: Path to the input file
        - **output_file**: Path to the output file
        - **ngram**: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which 
        represents unigrams.
        - **cutoff_freq**: The ngrams that has less frequency than the cutoff frequency will not be included in the 
        output file. The default value is 5.
        - **alpha_numeric_flag**: Filter all non alpha numeric words. Default is false.
        - **stop_words_flag**: Filter all stop words. Default value is False.
        
9. **analysis_methods.ngram_adjacency_matrix(input_file, output_file, ngram, cutoff_freq, alpha_numeric_flag, 
stop_words_flag)**
    - The function writes the adjacency matrix to the output file, where the rows and columns are ngram and each cell is 
    the number of users that has both the ngram in their description.
    - **Parameters**:
        - **input_file**: Path to the input file
        - **output_file**: Path to the output file
        - **ngram**: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which 
        represents unigrams.
        - **cutoff_freq**: The ngrams that has less frequency than the cutoff frequency will not be included in the 
        output file. The default value is 5.
        - **alpha_numeric_flag**: Filter all non alpha numeric words. Default is false.
        - **stop_words_flag**: Filter all stop words. Default value is False.
        
10. **analysis_methods.ngram_alloy_matrix(input_file1, input_file2, output_file, ngram, cutoff_freq, alpha_numeric_flag, 
stop_words_flag)**
     - Alloy matrix count the number of new ngram pairings. If a ngram A is present at time 1 and at time 2. If a ngram 
     B is not present at time 1 but present at time 2, then AB is an alloy and its count will incremented by 1 for each 
     new occurrence.
     - **Parameters**:
        - **input_file1**: Path to the input file 1
        - **input_file2**: Path to the input file 2
        - **output_file**: Path to the output file
        - **ngram**: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which 
        represents unigrams.
        - **cutoff_freq**: The ngrams that has less frequency than the cutoff frequency will not be included in the 
        output file. The default value is 5.
        - **alpha_numeric_flag**: Filter all non alpha numeric words. Default is false.
        - **stop_words_flag**: Filter all stop words. Default value is False.
        
11. **analysis_methods.ngram_transmutation_matrix(input_file1, input_file2, output_file, ngram, cutoff_freq, 
alpha_numeric_flag, stop_words_flag)**
    - Alloy matrix count the number of new ngram pairings. If a ngram A is present at time 1 but not at time 2. If a 
    ngram B is not present at time 1 but present at time 2, then AB is an alloy and its count will incremented by 1 for 
    each new occurrence.
    - **Parameters**:
        - **input_file1**: Path to the input file 1
        - **input_file2**: Path to the input file 2
        - **output_file**: Path to the output file
        - **ngram**: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which 
        represents unigrams.
        - **cutoff_freq**: The ngrams that has less frequency than the cutoff frequency will not be included in the 
        output file. The default value is 5.
        - **alpha_numeric_flag**: Filter all non alpha numeric words. Default is false.
        - **stop_words_flag**: Filter all stop words. Default value is False.
        
12. **analysis_methods.ngram_document_term_matrix(input_file1, word_list_file, output_file, ngram, cutoff_freq, 
alpha_numeric_flag, stop_words_flag)**
    - The function writes the adjacency matrix to the output file, where the rows and columns are ngram and each cell is 
    the number of users that has both the ngram in their description.
    - **Parameters**:
        - **input_file1**: Path to the input file 1
        - **word_list_file**: Path to the word list. This list contains the word for which you want to count the 
        frequency
        - **output_file**: Path to the output file
        - **ngram**: n represents the n in n-gram which is a contiguous sequence of n items. The default vale is 1 which 
        represents unigrams.
        - **cutoff_freq**: The ngrams that has less frequency than the cutoff frequency will not be included in the 
        output file. The default value is 5.
        - **alpha_numeric_flag**: Filter all non alpha numeric words. Default is false.
        - **stop_words_flag**: Filter all stop words. Default value is False.

13. **analysis_methods.calculate_present_absent(input_file, output_file, number_of_users, start_date, end_date, 
pattern)**
    - This function calculates the number of times the twitter user has added ot removed the pattern defined here in 
    his/her description.
    - **Parameters**:
        - **input_file_folder_path**: Path to the folder in which input files are stored
        - **output_file**: Path to the output file
        - **number_of_users**: To identify the input file as they are named based on the number of users
        - **start_date**: Date from which function will start to calculate
        - **end_date**: Date up to which function will calculate
        - **pattern**: Pattern to search for in the description

14. **analysis_methods.get_locations(input_file, output_file)**
     - The function writes the user id and his/her us state name in the output file based on the the value of location 
     key in the user information and state_location dictionary. If function does not find the location in the 
     state_locations dictionary then not in usa will be written against the user id.
     - **Parameters**:
        - **input_file**: Path to the input file
        - **output_file**: Path to the output file

15. **analysis_methods.entities_count_difference(input_file1, input_file2, output_file)**
     - The function calculates the difference between the followers count, following count, total tweets and total 
     likes of each user between the two input files that  are generate at two different time.
     - **Parameters**:
        - **input_file1**: Path to user profiles file of a specific date (earlier date)
        - **input_file2**: Path to user profiles file of a specific date (later date)
        - **output_file**: Path to the output file

16. **analysis_methods.description_change_frequency(input_file, output_file, number_of_users, start_date, end_date)**
     - The function calculates and store the number of times the user has made changes in his/her description between 
     the start_date and the end_date.
     - **Parameters**:
        - **input_file_folder_path**: Path to the folder in which input files are stored
        - **output_file**: Path to the output file
        - **number_of_users**: To identify the input file as they are named based on the number of users
        - **start_date**: Date from which function will start to calculate
        - **end_date**: Date up to which function will calculate

17. **botometer_methods.bot_or_not(input_file, output_file)**
    - This function creates a file which contains the Botometer scores for each user in the input_file
    - **Parameters**:
        - **input_file**: Path to the input file
        - **output_file**: Path to the output file
      
18. **reconstruction_methods.get_user_description_dict(input_file)**
    - The method read the json file and generates dictionary where each key is user id and corresponding value is 
    his/her profile description.
    - **Parameters**:
        - **input_file**: path to input file
    - **return**: Return a dictionary where user id is key and his/her description is its value.      

19. **reconstruction_methods.reconstruct_user_description_dictionary(input_file_folder_path, number_of_users, 
end_date)**
    - This function will reconstruct the a dictionary, where keys are user ids and values are corresponding profile 
    descriptions. It uses the 1st day of the month as the base file and updates/adds the user descriptions that have 
    made changes in their descriptions.
    - **Parameters**:
        - **input_file_folder_path**: Path to the folder in which input files are stored
        - **output_file**: Path to the output file
        - **number_of_users**: To identify the input file as they are named based on the number of users
        - **end_date**: Date up to which the function will reconstruct data. Default is today.

20. **reconstruction_methods.get_user_profile_dict(input_file)**
    - The method read the json file and returns a dictionary where each key is user id and corresponding value is 
    his/her profile data.
    - **Parameters**:
        - **input_file**: Path to input file

21. **reconstruction_methods.reconstruct_data_dictionary(input_file_folder_path, number_of_users, end_date)**
    - This function will reconstruct the a dictionary, where keys are user ids and values are corresponding profile 
    data. It uses the 1st day of the month as the base file and updates/adds the user profiles that have made changes in 
    their descriptions.
    - **Parameters**:
        - **input_file_folder_path**: Path to the folder in which input files are stored
        - **output_file**: Path to the output file
        - **number_of_users**: To identify the input file as they are named based on the number of users
        - **end_date**: Date up to which the function will reconstruct data. Default is today.

22. **reconstruction_methods.reconstruct_longitudinal_data(input_file_folder_path, output_file_path, number_of_users, 
end_date)**
    - This function calls the reconstruct_data_dictionary function to get the updated user profiles dictionary and 
    store it as a zip file in the user specified location.
    - **Parameters**:
        - **input_file_folder_path**: Path to the folder in which input files are stored
        - **output_file**: Path to the output file
        - **number_of_users**: To identify the input file as they are named based on the number of users
        - **end_date**: Date up to which the function will reconstruct data. Default is today.        

## Example
- Use the following command to run any function on terminal:
    ```
    python driver.py <function name> <args>
    ```
- Pass `-h` as argument for help menu.
- In similar fashion one can run any other function. To get help regarding the function specific arguments run:
    ```
    python driver.py <function name> -h
    ```
- For example, to run the **ngram_frequency_dist** with ngram of size 2, with alpha_numeric_flag and stop_words_flag as 
True, run the following 
command:
    ```
    python driver.py ngram_frequency_dist -i <input file> -o <output file> -ngram 2 -alpha_numeric True -stop_words True
    ``` 

## Logs
- All the errors, exceptions and information status generated Twitter REST API, Tweepy and Botometer during a call to 
the function that uses them are written in the respected month's log file.
- For more information please refer to the 
[Twitter REST API HTTP status codes](https://developer.twitter.com/en/docs/basics/response-codes) 
and [Botometer HTTP error codes](https://github.com/IUNetSci/botometer-python/wiki/Troubleshooting-&-FAQ).

## Crontab
- The crontab runs the given tasks in the background at specific times. We can use the crontab to scrape the user 
profiles daily.
- Follow the below commands to setup the crontab on your system:
  - open terminal
  - Use command `crontab -e` to open or edit the crontab file.
  - If asked to select an editor choose according to your preference. 
  - Use arrow keys to reach to the bottom of the file.
  - Lines in the crontab has the following format:
       ```
       minute(0-59) hour(0-23) day(1-31) month(1-12) weekday(0-6) command
       ```
  - Use * to match any value.
  -   Write the following command in the file to run the 
  **twitter_scraper** daily at 9:59 am:
       ```
       59 9 * * * cd <path to twitter_analysis folder> && /usr/bin/python <path to Driver.py> twitter_scarper -i <input file> -o <output file folder path> -format <json|csv> -size <True|False>  -cleaned_userid <True|False> -
       ```
  - The location or the name of the python interpreter may vary.

### License
Apache
