# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 19:03:27 2016
@author: gravesm
"""
import tweepy
import random
import time
import logging
import logging.handlers
import hashlib
import string
import json
import threading
import os
from datetime import datetime
from pytz import timezone
from random import shuffle
import nltk.data
import botornot
  
class Stream(threading.Thread):


    def __init__(self,bot_number):
        threading.Thread.__init__(self)

        self.botid = int(bot_number)
        
        # get bot metadata file
        with open(os.getcwd() + '/config/' + 'bot-config.json') as data_file:    
            self.config_data = json.load(data_file)

        # get behavior metadata
        get_behaviors(self) 

        # get credentials, create api object.        
        self.consumer_key = self.config_data["bots"][self.botid]["accessKeys"]["consumerKey"]
        self.consumer_secret = self.config_data["bots"][self.botid]["accessKeys"]["consumerSecret"]
        self.access_token = self.config_data["bots"][self.botid]["accessKeys"]["accessToken"]
        self.access_secret = self.config_data["bots"][self.botid]["accessKeys"]["accessSecret"]
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_secret)
        self.api = tweepy.API(auth)
        
        # create logger for operational data
        self.bot_name = self.config_data["bots"][self.botid]["name"]
        self.LOG_FILENAME = os.getcwd() + '/logs/' + self.config_data["bots"][self.botid]["logFileName"]
        self.max_size_log_file = int(self.config_data["bots"][self.botid]["maxSizeLogFile"])
        self.lgr = logging.getLogger(self.bot_name)
        self.lgr.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(              # Add the log message handler to the logger
                      self.LOG_FILENAME, maxBytes=self.max_size_log_file, backupCount=3)
        frmt = logging.Formatter('%(asctime)s,%(name)s,%(message)s') # create a formatter and set the formatter for the handler.
        handler.setFormatter(frmt)
        self.lgr.addHandler(handler)
        # create logger for stats data
        self.STATS_LOG_FILENAME = os.getcwd() + '/stats/' + self.config_data["bots"][self.botid]["logFileName"] + '_stats'        
        self.lgr_stats = logging.getLogger(self.bot_name+'_stats')
        self.lgr_stats.setLevel(logging.DEBUG)
        handler_stats = logging.handlers.RotatingFileHandler(              # Add the log message handler to the logger
                  self.STATS_LOG_FILENAME, maxBytes=self.max_size_log_file, backupCount=3)
        frmt_stats = logging.Formatter('%(asctime)s,%(name)s,%(message)s') # create a formatter and set the formatter for the handler.
        handler_stats.setFormatter(frmt_stats)
        self.lgr_stats.addHandler(handler_stats)


    def run(self):
        #Main Loop for the bot program
        i = 1
        while True:

            print('Loop--'+str(i) + '_for_bot_' + str(self.bot_name))
            self.lgr.info('--' * 20)
            self.lgr.info('Loop #: ' + str(i) + ' for bot: ' + str(self.bot_name))
            self.lgr.info('--' * 20)

            # get behavior metadata
            get_behaviors(self) 

            #Put behaviors that should happen during active time here:
            if not is_it_sleep_time(self): # check if the bot should be active
                self.lgr.info('Time for bot to be active...')    
                process_list(self) #start a twitter interaction
                # frequency for follower actions
                if i%self.follower_actions_frequency == 0: 
                    print('Taking_follower_actions..._for_bot_' + str(self.bot_name))
                    like_follower_tweets(self) 
                    like_retweeters_tweets(self)
                    follow_my_followers(self)   
                # frequency to tweet
                if self.tweet_status=='True' and i%self.tweet_status_frequency == 0: 
                    tweet_status(self,get_status_text(self))

            #Put behaviors that happen during inactive hours here (e.g. account clean-up):
            if is_it_sleep_time(self): # check if the bot should be active
                self.lgr.info('Bot is inactive...')    
                if i%self.remove_friends_frequency == 0: # frequency for removing friends
                    cleanup_friends(self)                        

            #Put behaviors that happen 24x7 hours here:
            if i%self.logging_frequency == 0: # frequency to tweet
                log_user_metrics(self) 
                print('Saving_Metrics..._for_bot_' + str(self.bot_name))
            
            #Reset the sleep time - this sets the overall bot heartbeat
            rand_num=random.randint(0,int(self.max_wait_time_between_activity))
            self.lgr.info('--' * 20)
            self.lgr.info('Sleep for: ' + str(int(self.config_data["globalParameters"]["minSleepTime"])+ rand_num) + ' for bot: ' + str(self.bot_name))
            self.lgr.info('--' * 20)
            print('Sleep--'+str(int(self.config_data["globalParameters"]["minSleepTime"])+rand_num) + '_for_bot_' + str(self.bot_name))
            time.sleep(int(self.config_data["globalParameters"]["minSleepTime"])+rand_num)   #Sets the main heartbeart for the bot
            
            #increment the counter, restart the loop        
            i=i+1
 
def get_behaviors(self):
    # get latest bot meta data file
    with open(os.getcwd() + '/config/' + 'bot-config.json') as data_file:    
            self.config_data = json.load(data_file)

    self.max_tweets_search=int(self.config_data["bots"][self.botid]["behaviors"]["maxTweetsSearch"])   # maxium number of tweets to search
    self.target_tweet_actions_per_session=int(self.config_data["bots"][self.botid]["behaviors"]["targetTweetActionsPerSession"])  # maxium number of tweet actions per session
    self.friend_to_follower_ratio=int(self.config_data["bots"][self.botid]["behaviors"]["friendFollowerRatio"])   # target ration of friends to followers
    self.friend_pacing_tier=int(self.config_data["bots"][self.botid]["behaviors"]["friendPacingTier"])   # tier at which bot starts pacing friend requests
    self.num_friends_to_remove=int(self.config_data["bots"][self.botid]["behaviors"]["numFriendsToRemove"])   # number of friends to remove during clean-up cycle
    self.remove_friends_frequency=int(self.config_data["bots"][self.botid]["behaviors"]["removeFriendsFrequency"])   # frequency to remove friends
    self.max_wait_time_between_activity=int(self.config_data["bots"][self.botid]["behaviors"]["maxWaitTimeBetweenActivity"])   # maxium wait time between bot activity
    self.process_list_like=self.config_data["bots"][self.botid]["behaviors"]["processListLike"]   # boolean, determines if bot will like tweets 
    self.process_list_retweet=self.config_data["bots"][self.botid]["behaviors"]["processListRetweet"]   # boolean, determines if bot will rewteet  
    self.process_list_follow=self.config_data["bots"][self.botid]["behaviors"]["processListFollow"]   # boolean, determines if bot will follow      
    self.tweet_status=self.config_data["bots"][self.botid]["behaviors"]["tweetStatus"]   # Boolean, whether should tweet status
    self.tweet_status_frequency=int(self.config_data["bots"][self.botid]["behaviors"]["tweetStatusFrequency"])   # Frequency with which to tweet status
    self.logging_frequency=int(self.config_data["bots"][self.botid]["behaviors"]["loggingFrequency"])   # frequency to log stats
    self.follower_actions_frequency=int(self.config_data["bots"][self.botid]["behaviors"]["followerActionsFrequency"])   # frequency to conduct follower actions
    self.relevancy_proximity=int(self.config_data["bots"][self.botid]["behaviors"]["relevancyProximity"])   # required proximity of search terms 
    self.morning_start_time=int(self.config_data["bots"][self.botid]["behaviors"]["morningStartTime"])   # bot start time
    self.evening_end_time=int(self.config_data["bots"][self.botid]["behaviors"]["eveningEndTime"])   # bot end time

def is_it_sleep_time(self):
    #format to 24Hour time
    fmt = '%H' 
    # Current time in UTC
    server_utc = datetime.now(timezone('UTC'))
    server_now_pst = server_utc.astimezone(timezone('US/Pacific'))
    sdt = int(server_now_pst.strftime(fmt))

    if (sdt > 12 and sdt > self.evening_end_time) or (sdt < 12 and sdt < self.morning_start_time):
        return True
    else:
        return False

def bon_analysis(self,twitter_handle): #bot or not score - more info here: https://truthy.indiana.edu/botornot/
    twitter_app_auth = {
    'consumer_key': self.consumer_key,
    'consumer_secret': self.consumer_secret,
    'access_token': self.access_token,
    'access_token_secret': self.access_secret,
    }

    bon = botornot.BotOrNot(**twitter_app_auth)
    # Check a single account
    try:
        result = bon.check_account(twitter_handle)
        score = result['score']
    except botornot.NoTimelineError as e:
        score = 'null'
    
    return score
    

def log_tweepy_error_message(self, error_text,tweep_error):    

    self.lgr.info(error_text +': ,1,' + 'code:, ' + str(tweep_error.api_code) + ', error: ,' + str(tweep_error))

def log_user_metrics(self):
    try:            
        self.lgr_stats.info(str(self.api.me().statuses_count)+','+str(self.api.me().friends_count)+','+str(self.api.me().followers_count)+','+ str(bon_analysis(self,self.api.me().screen_name)))
    except tweepy.TweepError as e:
        log_tweepy_error_message(self,'Error logging user metrics',e)

# get a preformed message to tweet....
def get_status_text(self):    

    #Load text for status updates
    with open(os.getcwd() + '/config/' + self.config_data["jsonConfigFiles"]["tweetText"]) as data_file:    
        status_text = json.load(data_file)
    # select text to tweet
    rand_num=random.randint(0, len(status_text)-1)
    statement=status_text["bots"][self.botid]["statements"][rand_num]
    self.lgr.info('status text:, ' + statement)    
    return statement    
    
# send out a tweet
def tweet_status(self,status):
    try:            
        self.api.update_status(status) #tweet status update
        self.lgr.info('Tweet Status: ,1')
    except tweepy.TweepError as e:
        log_tweepy_error_message(self,'Error on tweet status',e)

# Check application Get request available in 15 minute window
def check_application_limit(self):

     try:
         rate_limit_payload = self.api.rate_limit_status()
         application_limit = rate_limit_payload['resources']['application']['/application/rate_limit_status']['remaining']
         self.lgr.info('Application limit for current 15 minute window:, ' + str(application_limit))
     except tweepy.TweepError as e:
         log_tweepy_error_message(self,'Get application limit error',e)
    
     if application_limit>20: # proceed if there are more than 20 calls available
         return True
     else:
         return False

def get_search_data(self):
    #laod search terms
    with open(os.getcwd() + '/config/' + self.config_data["jsonConfigFiles"]["searchTerms"]) as data_file:    
        search_data = json.load(data_file)
    #grab a random one..
    rand_num=random.randint(0, len(search_data["bots"][self.botid]["searchTerms"])-1)
    term=search_data["bots"][self.botid]["searchTerms"][rand_num]    
    self.lgr.info('Search Term:, ' + str(term))
    return term    

def like_tweet(self,tweet_id):
    try:
        self.api.create_favorite(tweet_id)
        self.lgr.info('Liked Tweet - count:,1') # add a count to make log file analytics a bit easier
        return True
    except tweepy.TweepError as e:
        log_tweepy_error_message(self,'Like Tweet error on',e)
        return False
        
def retweet(self,tweet_id):
    try:
        self.api.retweet(tweet_id)
        self.lgr.info('Retweet - count:, 1')
        return True
    except tweepy.TweepError as e:
        log_tweepy_error_message(self,'Retweet error on',e)
        return False
         
def follow_user(self,author_id):
            
    try:
        friends_count=self.api.me().friends_count
        followers_count=self.api.me().followers_count

        if followers_count > 0:  #Ensure there is at least one follower..            
            friend_to_follower=friends_count/followers_count    

            if friends_count < self.friend_pacing_tier or friend_to_follower < self.friend_to_follower_ratio: # check to see if there are already too many friends....
                try:
                    self.api.create_friendship(author_id)
                    self.lgr.info('Following user: ,1')
                    return True
                except tweepy.TweepError as e:
                    log_tweepy_error_message(self,'Follow user error on',e)
                    return False
            else:
                self.lgr.info('No friend request made')
        else:
                self.lgr.info('This user has no followers')
    except tweepy.TweepError as e:
        log_tweepy_error_message(self,'Follow user error - unable to get api.me() stats',e)
        

def remove_profane_tweets(self,raw_list_p):
    clean_list=[]
    num_profane_tweets=0
    #laod profanity list
    with open(os.getcwd() + '/config/' + self.config_data["jsonConfigFiles"]["profanityList"]) as data_file:    
        profane_data = json.load(data_file)
        profane_terms=profane_data['profanityList']
    
    for tweet in raw_list_p:
        tweet_text=str(tweet[2]).lower()
        if any(ext in tweet_text for ext in profane_terms):
            num_profane_tweets +=1
        else: 
            clean_list.append(tweet)

    self.lgr.info('Number of profane tweets removed:, ' + str(num_profane_tweets))    
    self.lgr.info('Number of clean tweets remaining:, ' + str(len(clean_list)))
    
    return clean_list

def remove_excludedterms_from_tweets(self,raw_list_e):
    remaining_excluded_list=[]
    num_excludedterms_tweets=0
    #laod exclude terms list
    with open(os.getcwd() + '/config/' + self.config_data["jsonConfigFiles"]["excludeTerms"]) as data_file:    
        exclude_data = json.load(data_file)
        exclude_terms=exclude_data["bots"][self.botid]["excludeTerms"]
    
    for tweet in raw_list_e:
        tweet_text=str(tweet[2]).lower()
        if any(ext in tweet_text for ext in exclude_terms):
            num_excludedterms_tweets +=1
        else: 
            remaining_excluded_list.append(tweet)

    self.lgr.info('Number of tweets removed from excluded list:, ' + str(num_excludedterms_tweets))    
    self.lgr.info('Number of clean tweets remaining:, ' + str(len(remaining_excluded_list)))
    
    return remaining_excluded_list

# remove duplicate tweets using md5 hash
def remove_duplicates(self,raw_list_d):
    hash_list=[]
    unique_list=[]    
    for tweet in raw_list_d:
        hash = hashlib.md5(str(tweet[2]).encode('utf-8')).hexdigest()
        if hash not in hash_list:
            hash_list.append(hash)
            unique_list.append(tweet)

    self.lgr.info('# of unique tweets:, ' + str(len(unique_list)))
    
    return unique_list

def retweets_of_me(self):

    my_retweeted_list=[] # list of my authored tweets which have been retweeted
    retweeters_list=[] # list of authors who retweeted my authored tweets

    try:     
        my_retweeted_list=self.api.retweets_of_me() 
        
        if len(my_retweeted_list) > 0:                
            for rtweet in my_retweeted_list:
                retweets_list=[]
                retweets_list=self.api.retweets(rtweet.id)                
                if len(retweets_list) > 0:                
                        for rtweet in retweets_list:
                            # create list of unique authors
                            if rtweet.author.id not in retweeters_list:
                                retweeters_list.append(rtweet.author.id)
                 
        self.lgr.info('# of authors who have retweeted my tweets:, ' + str(len(retweeters_list)))
        
    except tweepy.TweepError as e:
        log_tweepy_error_message(self,'Unable to get retweets of me',e)

    return retweeters_list

def search_tweets(self,search_terms):

    raw_list=[] # initiate raw list with a value.
    my_id_counter=0

    try:
        my_id=self.api.me().id
    except tweepy.TweepError as e:
        log_tweepy_error_message(self,'Unable to get bot info from twitter in search tweets call',e)
        raise tweepy.TweepError("search_tweets my_id error")
        
    try:
        for status in tweepy.Cursor(self.api.search,q=search_terms,lang='en').items(self.max_tweets_search):
            if my_id != status.author.id: #exclude my tweets from the search results                    
                tweet_data=[status.id,status.author.id,status.text] # tweet data with fields required for downstream processing
                raw_list.append(tweet_data)
            else:
                my_id_counter +=1
    except tweepy.TweepError as e:
            log_tweepy_error_message(self,'Tweepy error in search_tweets()',e)
            raise tweepy.TweepError("search_tweets tweepy_cursor error")
            
    self.lgr.info('# of tweets searched:, ' + str(self.max_tweets_search))
    self.lgr.info('# of raw tweets tweeted by me:, ' + str(my_id_counter))
    self.lgr.info('# of tweets returned from search_tweets():, ' + str(len(raw_list)))

    return raw_list


#check the degree of relevancy of the search terms within tweet text
def check_relevancy(self,search_terms,raw_list_r):
    relevant_list=[]
    query_list=search_terms.lower().split()
    translator = str.maketrans({key: None for key in string.punctuation})
    #load nltk training data. Used to split tweet text into sentences
    sent_detector = nltk.data.load('bot/punkt/english.pickle')
    for tweet in raw_list_r:
        tweet_sentences = sent_detector.tokenize(tweet[2].strip())

        for tweet_text in tweet_sentences:
            tt_clean=tweet_text.lower().translate(translator)        
            tweet_text_list = tt_clean.split()        
            if (query_list[0] in tweet_text_list) and (query_list[1] in tweet_text_list): #both terms should be in the tweet text
                index_1 = tweet_text_list.index(query_list[0])     
                index_2 = tweet_text_list.index(query_list[1])
                difference = abs(index_1 - index_2) #find proximity of terms
                if difference < self.relevancy_proximity : 
                    relevant_list.append(tweet) #append if it's within proximity target
                    break; # if get match, break out of the loop
                
    self.lgr.info('# of relevant tweets remaining:, ' + str(len(relevant_list)))

    return relevant_list

#obtain a list of high-quality tweets to process....
def curate_tweet_list(self):

    curated_list=[]
    
    while len(curated_list)<self.target_tweet_actions_per_session and check_application_limit(self):
        search_terms = get_search_data(self) #get new tweet search terms
        if len(search_terms.split())==2: # make sure we have two search terms

            try:                        
                raw_list_search = search_tweets(self,search_terms) #search to get raw list of tweets
                deduped_list = remove_duplicates(self,raw_list_search) #get rid of duplicates
                clean_list = remove_profane_tweets(self,deduped_list) #remove any profane tweets
                excluded_list=remove_excludedterms_from_tweets(self,clean_list) #remove any tweets that contain terms on the excluded list
                relevant_list = check_relevancy(self,search_terms,excluded_list) #remove tweets that don't meet relevancy test

                for tweet in relevant_list:
                    curated_list.append(tweet)

            except tweepy.TweepError as e:
                log_tweepy_error_message(self,'Could not process list',e)
                raise tweepy.TweepError("curate_tweet_list error")

        self.lgr.info('Curated List length:, ' + str(len(curated_list)))

    return curated_list

def process_list(self):

    try:
        proc_list=[]
        proc_list = curate_tweet_list(self) #obtain list of tweets to take action on
        tweet_actions=0
        for tweet in proc_list:   
            if self.process_list_like=='True': # check if bot should like tweets
                if like_tweet(self,tweet[0]):
                    tweet_actions += 1
            if self.process_list_retweet=='True': # check if bot should rewteet                    
                if retweet(self,tweet[0]): 
                    tweet_actions += 1
            if self.process_list_follow=='True': # check if bot should follow                                        
                if follow_user(self,tweet[1]):            
                    tweet_actions += 1 
            if tweet_actions >= self.target_tweet_actions_per_session: #keep actions per session within specified limit
                break
            self.lgr.info('Tweet actions for this session:, ' + str(tweet_actions))

    except tweepy.TweepError as e:
        log_tweepy_error_message(self,'Could not process list',e)

        
def follow_my_followers(self):
    try:
        my_id=self.api.me().id
        friends=self.api.friends_ids(my_id)

        for follower in self.api.followers_ids(my_id):
            if follower not in friends:
                self.lgr.info('Creating friendship with follower:, ' + str(follower))    
                self.api.create_friendship(follower)
    except tweepy.TweepError as e:
        log_tweepy_error_message(self,'Tweepy error in follow_my_followers',e)

# pick a randaom follower and like their tweets....
def like_follower_tweets(self):
    try:
        followers=self.api.followers_ids(self.api.me().id)        
        if len(followers) > 0:            
            rand_num=random.randint(0, len(followers)-1)
            follower_to_like=followers[rand_num]
            self.lgr.info('Like follower tweets ,1, follower ' + str(self.api.get_user(id=follower_to_like).screen_name))    
            timeline=self.api.user_timeline(id=follower_to_like)
            for status in timeline[0:5]: #choose the first 5 tweets
                like_tweet(self,status.id)
        else:
            self.lgr.info('This user has no followers')    
    except tweepy.TweepError as e:
        log_tweepy_error_message(self,'Tweepy error in follow_my_followers()',e)

#get a list of authors who have retweeted users authored tweets, like their tweets
def like_retweeters_tweets(self):
    authors_to_like=[]
    authors_to_like=retweets_of_me(self)
    if len(authors_to_like) >0:
        for author in authors_to_like[0:5]: #pick the last 5 followers to like, keep this limited to avoid twitter usage violations 
            try:                
                timeline=self.api.user_timeline(id=author) # get timeline for this author
            except tweepy.TweepError as e:
                log_tweepy_error_message(self,'Tweepy error in follow_my_followers()',e)
            if len(timeline)>0: 
                for status in timeline[0:5]: #choose the first 5 tweets
                    like_tweet(self,status.id) #like author's tweets
    else:
        self.lgr.info('This user has no retweeters')    
        

def cleanup_friends(self):
    try:        
        friends_count=self.api.me().friends_count
        followers_count=self.api.me().followers_count
 
        if followers_count > 0:  #Ensure there is at least one follower..            
                
            friend_to_follower=friends_count/followers_count    

            if friends_count > self.friend_pacing_tier: # don't bother to do any clean-up if friend count is below the pacing tier
                 if friend_to_follower > self.friend_to_follower_ratio: # check friend to follower ratio vs. target
                    total_num_to_remove=friends_count-(followers_count*self.friend_to_follower_ratio) #determine total friends to remove
                    
                    if total_num_to_remove>self.num_friends_to_remove: 
                        num_to_cleanup= self.num_friends_to_remove # number of friends to remove.
                    else:
                        num_to_cleanup= total_num_to_remove # only remove the 

                    self.lgr.info('Time to clean-up friends list! Friend count: ' + str(num_to_cleanup))
                    friends_list=self.api.friends_ids(self.api.me().id)
                    followers_list=self.api.followers_ids(self.api.me().id)
                    friends_to_remove_list= [x for x in friends_list if x not in followers_list]
                    shuffle(friends_to_remove_list) # randomize the remove list

                    for id in friends_to_remove_list[0:num_to_cleanup]:
                            try:
                                self.api.destroy_friendship(id)
                            except tweepy.TweepError as e:
                                self.lgr.info('Tweepy error in friends_user_cleanup(): ' + str(e))                         
                 else:
                    self.lgr.info('Friends to followers ratio looks good!')
            else:
                self.lgr.info('Friends list below pacing tier')
        else:
            self.lgr.info('This user has no followers')
            
    except tweepy.TweepError as e:
        log_tweepy_error_message(self,'Unable to peform friends_clean-up()',e)
   