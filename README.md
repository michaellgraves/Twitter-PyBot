# Twitter-PyBot

A Python3-based Twitter bot leveraging the [Tweepy API] (http://www.tweepy.org/)

This bot automates a number of Twitter-related activities including:

1. Searching Twitter for specific keywords, scoring results based on relevancy, and retweeting relevant tweets 
2. Following an author of a relevant tweet
3. Liking a set of tweets from a random follower
4. Liking a set of tweets from authors who have retweeted your tweets
5. Automatically following users who follow you
6. Providing limits to activity to prevent Twitter bot restrictions
7. Filtering out profane tweets
8. Implementing randomness for activity heartbeat, friend/follower ratios, and bot activity window such that your account does not look bot-controlled
9. Tweeting out random message from a list of messages

In addition this project also includes these helpful features:

1. Externalized JSON configuration files each striped by bot id, allowing you to easily run several bots using the same program instance
2. Robust exception handling to ensure your bot keeps running even when encountering tweepy/Twitter errors
3. Detailed log files which roll over and are limited in size to ensure they do not fill up your machine's disk space
4. A stats file which tracks your Twitter activity and followers over time
5. A bot launcher which ensures your JSON configuration files are well-formed and that each bot's Twitter credentials are valid before launching the bots into a seperate thread
6. Metadata refresh between bot cycles enables you to change the bot configuration parameters while the bot is still running

## This project includes the following files
###Python Programs:
* botContoller.py - This is the controller which validates the configuration files and bot credentials, and then launches each bot
* bot/stream.py - This file contains all the bot logic

###Configuration Files:

Please note that when configuring multiple bots, you must place their metadata in the same order for each file!

* bot-config.json - Configuration file for each bot including credentials and bot behaviours
* search_terms.json - Two-word search parameters. After much experimentation, two word parameters seem to work best with Twitter.
* exclude_terms.json - Terms used to filter out tweet search results
* profanity_list.json - Profane terms to filter out tweet search results. This is the only file not striped by bot id.
* update_status_test.json - List of tweets to send out at random times.

Configuration parameters in bot-config.json:

Global configuration
* searchTerms - file name which includes list of bot search terms
* profanityList - file name for profanity list
* excludeTerms - file name for terms to exclude from search results
* tweetText - file name which with list of tweets
* minSleepTime - minimum time for bot heart beat

Bot-specific configuration
* id - ID number of your bot
* name - name of your bot. This is used in the log file
* logFileName - name of your operational log file. User stats will be written to "logfilename_stats"
* maxSizeLogFile - maximum size of each logfile. There will be 2 log files created, operational and stats, with 4 back-ups each.
* consumerKey - [Define in Twitter Apps](apps.twitter.com)
* consumerSecret - [Define in Twitter Apps](apps.twitter.com)
* accessToken - [Define in Twitter Apps](apps.twitter.com)
* accessSecret - [Define in Twitter Apps](apps.twitter.com)
* searchTerms - source file for seed search terms
* profanityList - source file for profanity list
* tweetText - any seed text that should be tweeted on a period basis
* maxTweetsSearch - maxium number of results to return in Twitter search
* targetTweetActionsPerSession - maxium number of tweet actions per session (includes retweets, likes, and follow actions)
* friendFollowerRatio - target friend to follower ratio. bot will automatically remove friends if you adjust this down.
* friendPacingTier - # friends at which the friend to follower ratio kicks in
* numFriendsToRemove - # of friends to remove each cycle to pace out reduction in the friendFollowerRatio
* removeFriendsFrequency - frequency to remove friends. Tied to the overall hearbeat
* maxWaitTimeBetweenActivity - the frequency (in seconds) between bot cycles. this sets the overall bot heartbeat
* tweetStatus - boolean value, determines whether bot should send out tweets from tweetText file
* tweetStatusFrequency - frequency which bot should send out tweets
* loggingFrequency - frequency which bot should log stats
* followerActionsFrequency - frequency which bot should take follower actions such as like their tweets
* relevancyProximit - how close the two search terms need to be together in order for the tweet to be considered relevant
* morningStartTime - 24H time in PST for the bot to start activity
* eveningEndTime - 24H time in PST for the bot to end activity


## Instructions to deploy Bot to AWS:

An Amazon EC2 micro environment which has 1 CPU, 1 Gb of space is perfect for running this bot

Read [Amazon EC2 Getting Started] (http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html)

To access an AWS EC Linux env from Windows machine, you'll need:

PuTTY
WinSCP

Read [AWS EC2 Putty Guide] (http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/putty.html)

1. Putty to gen key
2. WinSCP to copy files
3. Putty to connect
* sudo yum install python34
* sudo yum install python34-pip
* sudo python34 -m pip install tweepy
* sudo python34 -m pip install pytz
* sudo python34 -m pip install nltk
4. Configure WinScp to connect to your AWS instance
5. Copy bot program files
5. Login via putty
* screen -S <screen_name>
* python34 stream.py

To return to same screen name
* screen -r <screen_name>
