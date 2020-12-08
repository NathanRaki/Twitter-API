import tweepy
import time
import json
import os
import sys
from datetime import datetime

os.chdir('/home/raki/Repositories/twitter/')

# Handle rate limit
# Issue : raise an error if the cursor has only one value
def limit_handled(cursor) :
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError as error:
            #print(error.__dict__)
            current_time = time.strftime("%H:%M:%S", time.localtime())
            print('Error [', current_time,'] :', error.reason, ' => Sleeping...')
            time.sleep(15 * 60)
            continue
        except StopIteration:
            break

class FarFarAway():
    
    def __init__(self):
        auth = tweepy.OAuthHandler('ywvBktojmiY4BC9UZpFTGX5EV', 'rxmk8uHF16bP3gmAO58cGSekVSRf3p6FeJcT8dDcO7xi3ph8zS')
        auth.set_access_token('1324394569363034115-Kf7LLuJH048Y0fVPuWzkzFMfbIkDxn', 'nsFQMRCcISBfN0c0K2vBZXLclwbybifuvBGxs1yI4Bsqo')

        self.__api = tweepy.API(auth)
        with open("followed.json") as json_file:
            self.__followed = json.load(json_file)
    
    # Follow function
    def follow_user(self, user):
        try:
            user.follow()
        except tweepy.TweepError as error:
            #print(error.__dict__)
            if error.api_code == 162 :
                print(user.name, " : this user blocked you!")
            elif error.api_code == 161 or error.api_code == 403:
                print("Error : You reached the follow limit. Please wait 24h.")
                sys.exit()
            else :
                sys.exit()
            return(error.api_code)
        return(1)
    
    # Cette fonction va atteindre la RateLimit plusieurs fois, en fonction du nombre de personne que vous suivez
    def loadfriends(self):
        for f in limit_handled(tweepy.Cursor(self.__api.friends).items()):
            self.__followed[f.screen_name] = {'tweet' : 'unknown',
                                              'filter' : 'unknown',
                                              'date' : datetime.now().strftime("%d/%m/%Y")}
            self.savefollowed()
    
    # Follow back you followers
    def followback(self):
        for follower in limit_handled(tweepy.Cursor(self.__api.followers).items()) :
            follower.follow()
            
    def savefollowed(self):
        json_obj = json.dumps(self.__followed)
        with open('followed.json', 'w') as f:
            f.write(json_obj)
            
    def isfollowed(self, name):
        if name in self.__followed:
            return(True)
        else:
            return(False)
    
    # Auto-Follow based on filters
    def autofollow(self, amount):
        filters = ["(giveaway jeux) OR (giveaway jeu)",
                   "@TeufeurSoff",
                   "(rembourser zalando) OR (rembourser amazon)",
                   "(rembourser ubereats) OR (rembourser deliveroo)",
                   "zebi"]
        cf = 0
        ct = 0
        limit = amount/len(filters)
        print("Starting to follow", amount, "new users :\n")
        for f in filters :
            print('Filter : ' + f + ' ...')
            ct = ct + 1
            for tweet in limit_handled(tweepy.Cursor(self.__api.search, q=f, lang="fr", tweet_mode="extended").items()) :
                if tweet.user.friends_count < 300 and not self.isfollowed(tweet.user.screen_name) : 
                    if self.follow_user(tweet.user) != 1:
                        print("User could not be followed")
                        continue
                    self.__followed[tweet.user.screen_name] = {'tweet' : tweet.full_text,
                                                               'filter' : f,
                                                               'date' : datetime.now().strftime("%d/%m/%Y")}
                    self.savefollowed()
                    cf = cf + 1
                    print(cf, '/', amount)
                    time.sleep(5)
                elif tweet.user.friends_count < 300:
                    print(tweet.user.screen_name, ": This user has too many friends!")
                elif self.isfollowed(tweet.user.screen_name):
                    print("Already followed!")
                if cf == ct * limit :
                    print("Following Loop Completed!\n")
                    break
            else:
                print("No tweet found!\n")