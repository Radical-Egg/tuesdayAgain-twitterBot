#!/mnt/nfs/home/pi/.virtualenvs/twitter-env/bin/python3
import tweepy

import time
import datetime
import json
import os
import re
import json
import requests
import random
import logging
from os import environ

CONSUMER = environ['CONSUMER']
CONSUMER_SECRET = environ['CONSUMER_SECRET']

ACCESS_TOKEN = environ['ACCESS']
ACCESS_TOKEN_SECRET = environ['ACCESS_SECRET']

GIPHY_API_KEY = environ['GIPHY']

NASA_API_KEY = environ['NASA_API']


# Teepy API Auths
auth = tweepy.OAuthHandler(CONSUMER, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

# making sure i can connect
try:
    api.verify_credentials()
    print("Auth OK")
except:
    print("Something went wrong")


# class for tweepy/tweeting each day of the week
class tuesdayListener:
    # data members
    def __init__(self):
        self.todayIs = datetime.date.today().weekday() # day of the week
        self.userList = ["no_probIem_", "And_Dads_Car", "catoutofcontxt"] # list of users i want to retweet from
        self.tweets = [api.user_timeline(self.userList[0], count = 5), api.user_timeline(self.userList[1], count = 5), api.user_timeline(self.userList[2], count = 5)] # list to get the first 5 tweets of each user on the userList
        self.regex = ["^https://*"] # the regex to make sure i am retweeting the stuff I want to retween
        self.flag = True 

    # searching through tweets (static twitter accounts like tuesdayAgain) and favoriting/retweeting if not already done so
    def searchMatch(self, tweets, search_term):
        self.flag = True
        for status in tweets:
            match = re.search(search_term, status.text) # making sure theres a match
            if match != None and self.flag: # retweeting / favorting the tweet 
                try:
                    if not status.retweeted: # checking that it hasn't been retweeted already
                        status.retweet()
                    if not status.favorited: # checking that it hasn't been faovrited already
                        status.favorite()
                    self.flag = False
                except:
                    logging.warning("Error trying to retweet/favorite this tweet")
            else:
                logging.info("No new tweets, or the tweet has already been retweeted")
                return

    # helper function for tweeting gifs, takes the url, the temp file path (temp.jpg, temp.gif etc) and the message you want to send
    def tweet_media(self, url, temp, message=""):
        with open(temp, 'wb') as f: # make a request for the url.content and write it to a file
            f.write(requests.get(url).content)

            f.close()
        try: # try to tweet media
            api.update_with_media(temp, message)
            logging.info("{} with message '{}' has been tweeted".format(temp, message))
        except: 
            logging.warning("unable to update status with image {}".format(temp))
        try:
            os.remove(temp)
        except:
            logging.info("no temp dir to remove for tweet_image func")

# class for downloading gifs from giphys API
class giphy:
    # getting data - if search is None then just get a random gif
    def gif(search=None):
        # getting random
        if search == None:
            api_request = requests.get("https://api.giphy.com/v1/gifs/random?api_key={}".format(GIPHY_API_KEY))
            data = json.loads(api_request.text)
            dataCap = data['data']['images']['original']['url']

            return dataCap
        # getting specific gif by search
        else:
            api_request = requests.get("https://api.giphy.com/v1/gifs/search?q={}&api_key={}&limit=10".format(search, GIPHY_API_KEY))
            data = json.loads(api_request.text)
            choice = random.randint(0, 9)
            dataCap = data['data'][choice]['images']['original']['url']

            return dataCap

# class for getting astonomy photo/video of the day
class APOD(tuesdayListener):
    def __init__(self):
            self.apod_request = requests.get("https://api.nasa.gov/planetary/apod?api_key={}".format(NASA_API_KEY))
            self.data = json.loads(self.apod_request.text)
            self.media_type = None
            self.url = None
            self.description = None
            self.copyright = None
            self.date = None
            self.title = None
            self.code = None

    # tweeting the Astronomy Photo of the day
    def APOD(self):
        try:
            # get meida type
            self.media_type = self.data['media_type']
            self.description = self.data['explanation']

            try:
                self.copyright = self.data['copyright']
            except:
                self.copyright = None
            self.date = self.data['date']
            self.title = self.data['title']

            # try for hdurl [not sure if all images provide one]
            try:
                self.url = self.data['hdurl']
            except:
                self.url = self.data['url']
            
            if self.media_type == 'video':
                return
                # need to figure out stuff for video still
            elif self.media_type == 'image':
                temp = "./temp.jpg"

                with open(temp, "wb") as f:
                    f.write(requests.get(self.url).content)

                    f.close()
        
                self.tweet_media(self.url, temp, 
                """Copyright: {}
Title: {}
#APOD""".format(self.copyright, self.title))

        except:
            self.code = self.data['code']
            logging.warning("API Unavailable code {}".format(self.code))
            return


# Work in progress 
# getting top trending tags on twitter / not using this at the moment
class trends:
    def __init__(self):
        self.trends1 = api.trends_place(1)
        self.data = self.trends1[0]
        self.trends = self.data['trends']
        self.names = [trend['name'] for trend in self.trends]
        self.trendsName = ', '.join(self.names)
        self.trendArray = list(self.trendsName.split(','))

    def printTrendArray(self):
        for trends in range(len(self.trendArray)):
            print(self.trendArray[trends])

# main
if __name__ == "__main__":
    # logging
    logging.basicConfig(filename='bot.log',level=logging.DEBUG)


    while True:
        # objects for tweeting and such
        listener = tuesdayListener()
        apod = APOD()

        if listener.todayIs == 0:
            logging.info("Metal Monday")
            listener.tweet_media(giphy.gif("metal"), "./temp.gif", "Metal Monday")
            listener.searchMatch(listener.tweets[2], listener.regex[0])
            apod.APOD()
        if listener.todayIs == 1:
            logging.info("its tuesday again")
            listener.searchMatch(listener.tweets[0], listener.regex[0])
            listener.searchMatch(listener.tweets[2], listener.regex[0])
            apod.APOD()
        if listener.todayIs == 2:
            logging.info("Cat Wednesday")
            listener.tweet_media(giphy.gif("cats"), "./temp.gif", "It is cat wednesday")
            listener.searchMatch(listener.tweets[2], listener.regex[0])
            apod.APOD()
        if listener.todayIs == 3:
            logging.info("Kitten Thursday, cause why not")
            listener.tweet_media(giphy.gif("kitten"), "./temp.gif", "It is kitten thursday")
            listener.searchMatch(listener.tweets[2], listener.regex[0])
            apod.APOD()
        if listener.todayIs == 4:
            logging.info("its friday again")
            listener.tweet_media(giphy.gif(), "./temp.gif")
            listener.searchMatch(listener.tweets[2], listener.regex[0])
            apod.APOD()
        if listener.todayIs == 5:
            logging.info("Saturday for cars")
            listener.searchMatch(listener.tweets[1], listener.regex[0])
            listener.searchMatch(listener.tweets[2], listener.regex[0])
            apod.APOD()
        if listener.todayIs == 6:
            logging.info("Sushi Sunday") 
            listener.tweet_media(giphy.gif("sushi"), "./temp.gif", "Sushi Sunday")
            listener.searchMatch(listener.tweets[2], listener.regex[0])
            apod.APOD()

        del listener
        del apod

        time.sleep(86400)
