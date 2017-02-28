import json
import tweepy
from config import esconn, aws_config, twitter_config
import os
from datetime import datetime as dt
from config import s3conn

# unicode mgmt
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# Twitter auth and api call setup
auth = tweepy.OAuthHandler(twitter_config.CONSUMER_KEY, twitter_config.CONSUMER_SECRET)
auth.set_access_token(twitter_config.ACCESS_TOKEN, twitter_config.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Get elasticsearch connection
es = esconn.esconn()

if len(sys.argv) > 2:
    sys.exit('ERROR: Received 2 or more arguments: {} {} {} Expected 1: User file name'.format(sys.argv[0], sys.argv[1], sys.argv[2]))

elif len(sys.argv) == 2:
    try:
        with open(sys.argv[1]) as f:
            users = f.readlines()
    except Exception:
        sys.exit('ERROR: Expected user file %s not found' % sys.argv[1])
else:
    try:
        with open('users.txt') as f:
            users = f.readlines()
    except:
        sys.exit('ERROR: Default users.txt not found. No alternate topic file  was provided')


USERS = [user.replace('\n', '').strip() for user in users]

def retrieve_user_data():
    try:
        return api.lookup_users(user_ids=USERS)
    except tweepy.TweepError as e:
        sys.exit("An error occured looking up the user_ids. Verify the correctness and existance of the given screen names, handles or ids.")

def map_user_for_es(user, time_stamp):
    return {
        'timestamp': time_stamp,
        'id': user.id,
        'name': user.screen_name,
        'screen_name': user.screen_name,
        'followers_count': user.followers_count,
        'friends_count': user.friends_count,
        'location': user.location,
        'description': user.description,
        'favorites_count': user.favorites_count,
        'statuses_count': user.statuses_count,
        'listed_count': user.listed_count,
        'profile_background_image_url': user.profile_background_image_url,
        'profile_image_url': user.profile_image_url
    }  

def dump_to_elastic(bodydata):
    es.index(index='twitter', doc_type="users", body=bodydata)

def get_time_stamp():
    return dt.now()

def get_twitter_users_pipeline():
    time_stamp = get_time_stamp()
    user_data = retrieve_user_data()
    for user in user_data:
        mapped_user_data = map_user_for_es(user_data, time_stamp)
        dump_to_elastic(mapped_user_data)

get_twitter_users_pipeline()