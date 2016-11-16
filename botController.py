# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 20:45:08 2016

@author: gravesm
"""
import tweepy
import json
import threading
import os
from bot import stream

# open up the bot config file
try:
    with open(os.getcwd() + '/config/' + 'bot-config.json') as data_file:    
        config_data = json.load(data_file)
    print('Loading bot-config.json...')        
except ValueError as e:
    print('JSON file: bot-config.json is invalid')
    print('Exiting program...')
    exit()

threads = []

def check_bot_creditials(botid):

        with open(os.getcwd() + '/config/' + 'bot-config.json') as data_file:    
            config_data = json.load(data_file)

        consumer_key = config_data["bots"][botid]["accessKeys"]["consumerKey"]
        consumer_secret = config_data["bots"][botid]["accessKeys"]["consumerSecret"]
        access_token = config_data["bots"][botid]["accessKeys"]["accessToken"]
        access_secret = config_data["bots"][botid]["accessKeys"]["accessSecret"]
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)
        
        if api.verify_credentials():
            return True
        else:
            return False

#check that the JSON files valid    
def is_valid(file_name):
    try:
        with open(os.getcwd() + '/config/' + config_data["jsonConfigFiles"][file_name]) as data_file:
            json_object = json.load(data_file)
    except ValueError as e:
        print('JSON file: ' + file_name + ' is invalid')
        return False
    return True

       
# Create new threads
def launch_bots():
    # check if configuration files are all valid
    if is_valid('searchTerms') and is_valid('profanityList') and is_valid('excludeTerms') and is_valid('tweetText'):
        print('All JSON files valid')
    else:
        print('Exiting program...')
        exit()
    #num_bots=1 
    num_bots=len(config_data["bots"])
    print('#_of_bots_to_be_launched:_' + str(num_bots))
    for bot in range(num_bots):
        #check that credentials are good
        print('check_bot_creditials for bot #: ' + str(bot))
        
        if check_bot_creditials(bot):
            print('Credentials are good..Starting_bot:_' + str(bot))
        t=stream.Stream(bot)        
        t.start()
        threads.append(t)

launch_bots()

main_thread = threading.currentThread()

for t in threading.enumerate():
    if t is main_thread:
        continue
    print('joining: ' +  t.getName())
    t.join()

print('enumerate thread: ' + str(threading.enumerate()))
print('active count: ' + str(threading.activeCount()))
print ("Exiting Main Thread")