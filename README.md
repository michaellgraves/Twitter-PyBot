# bot-master

A Python3-based Twitter bot leveraging the [Tweepy API] (http://www.tweepy.org/)

This bot automates a number of Twitter-related activities including: 
1. Searching Twitter for specific keywords, retweeting relevant tweets 
2. Liking a tweet
3. Following an author of a relevant tweet
4. Like a set of tweets from a random follower
5. Like a set of tweets from authors who have retweeted your tweets
6. Providing limits to bot activity to prevent Twitter bot restrictions
7. Provide a profanity filter to avoid retweeting profane tweets
8. Implementing randomness for activity heartbeat, friend/follower ratios, and bot activity window such that your account does not look bot-controlled
9. Tweeting out random message from a list of messages.

In addition this project also includes these helpful features:
1. Externalized JSON configuration files each striped by bot id, allowing you to easily run several bots using the same program instance
2. Robust exception handling to ensure your bot keeps running even when encountering tweepy/Twitter errors
3. Detailed log files which roll over and are limited in size to ensure they do not fill up your machine's disk space
4. A stats file which tracks your Twitter activity and followers over time
5. A bot launcher which ensures your JSON configuration files are well-formed and that each bot's Twitter credentials are valid before launching the bots into a seperate thread
6. Metadata refresh between bot cycles such that you can change the bot configuration parameters while the bot is still running

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

Cross-bot configuration
* searchTerms - file name which includes list of bot search terms
* profanityList - file name for profanity list
* excludeTerms - file name for terms to exclude from search results
* tweetText - file name which with list of tweets

Bot-specific configuration
* id - ID number of your bot (optional)
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
* maxTweetsSearch - maxium number of tweets to search
* targetTweetActionsPerSession -- maxium number of tweet actions per session
* friendFollowerRatio - target friend to follower ratio
* friendPacingTier - point at which the friend to follower ratio kicks in
* relevancyProximit - how close two words need to be together to be considered relevant
* morningStartTime - 24H time in PST for the bot to start activity
* eveningEndTime - 24H time in PST for the bot to end activity


## Instructions to deploy Bot to AWS:

With an Amazon Prime account, you have access to a free EC2 micro environment which has 1 CPU, 1 gb space.

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
6. Return to same screen name
* screen -r <screen_name>
