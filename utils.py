"""
Created on Mon Nov  4 10:05:23 2019
@author: David
"""
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
import configparser
import praw
import yake
import random 
import pickle
import joblib
import sklearn
from collections import Counter
import requests

INI_FILE = 'subsuggester.ini'

numOfKeywordsComments=80

numOfKeywordsSubmissions=20

kw_extractor_comments = yake.KeywordExtractor(top=numOfKeywordsComments)
kw_extractor_posts = yake.KeywordExtractor(top= numOfKeywordsSubmissions)

def encode_keywords(keywords):
    keywords = keywords.split(',')
    keywords = [keywords]
    feature_encoder = joblib.load(open('multilabelbinarizer_features.sav', 'rb'))    
    encoded_features = feature_encoder.transform(keywords)
    return encoded_features


def predict_subreddits(encoded_features):
    decision_tree_model = joblib.load(open('decision_tree_model.sav', 'rb'))
    result = decision_tree_model.predict(encoded_features)
    label_encoder = joblib.load(open('multilabelbinarizer_labels.sav', 'rb'))
    subreddits = label_encoder.inverse_transform(result)
    return subreddits[0]





def get_comments_and_subreddits_users_have_commented_in(user):
    most_common_num = 10
    comment_objects = list(user.comments.top(limit=200))
    comments = ','.join([comment_objects[num].body for num in range(len(comment_objects))])
    most_common = Counter([comment_objects[num].subreddit.display_name for num in range(len(comment_objects))]).most_common(most_common_num)
    if len(most_common) == most_common_num:
        string_subreddits = ','.join([most_common[num][0] for num in range(len(most_common))])
    else:
        string_subreddits = ''
    return comments, string_subreddits

def get_submissions(user):
    #print("Getting users submissions")
    submission_objects = list(user.submissions.top(limit=200))
    submissions = " ".join(submission_objects[num].title for num in range(len(submission_objects)))
    return submissions

def extract_comment_keywords(keyphrase):
    keywords_list = kw_extractor_comments.extract_keywords(keyphrase)
    keywords = ",".join(keywords_list[num][1] for num in range(len(keywords_list)))
    return keywords

def extract_submission_keywords(keyphrase):
    keywords_list = kw_extractor_posts.extract_keywords(keyphrase)
    keywords = ",".join(keywords_list[num][1] for num in range(len(keywords_list)))
    return keywords

def create_redditor(user_name):
    config = configparser.ConfigParser()
    config.read(INI_FILE)
    reddit = praw.Reddit(client_id=config['REDDIT_API']['client_id'],
                         client_secret=config['REDDIT_API']['client_secret'],
                         user_agent=config['REDDIT_API']['user_agent']
                        )
    reddit_user_object = reddit.redditor(user_name)
    
    return reddit_user_object

def get_comments(redditor):
    subreddits = dict() 
    for comment in redditor.comments.new(limit=None):
        if comment.subreddit.display_name not in subreddits:
            subreddits[comment.subreddit.display_name] = 1
        else:
            subreddits[comment.subreddit.display_name] += 1
    return subreddits

def get_upvoted_topics(redditor):
    upvoted_titles = ''
    try:
        for upvote in redditor.upvoted(limit=None):
            upvoted_titles = '{} {}'.format(upvoted_titles, upvote.title) 
        return upvoted_titles
    except:
        return None
    
def get_submissions(redditor):
    submissions = ''
    for submission in redditor.submissions.new(limit=None):
        submissions = '{} {}'.format(submissions, submission.title)
    return submissions

def extract_keywords(keyphrase):
    kw_extractor = yake.KeywordExtractor()
    keywords = kw_extractor.extract_keywords(keyphrase)
    return keywords



def authenticate_user(code):    
    
    config = configparser.ConfigParser()
    config.read(INI_FILE)
    client_id = config['REDDIT_API']['client_id']
    client_secret = config['REDDIT_API']['client_secret']
    user_agent = config['REDDIT_API']['user_agent']
    
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         redirect_uri="http://subsuggester.com/suggestion",
                         user_agent=user_agent)

    refresh_token = reddit.auth.authorize(code)
    return refresh_token

def new_user():
    config = configparser.ConfigParser()
    config.read(INI_FILE)
    client_id = config['REDDIT_API']['client_id']
    client_secret = config['REDDIT_API']['client_secret']
    user_agent = config['REDDIT_API']['user_agent']
    
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         redirect_uri="http://subsuggester.com/suggestion",
                         user_agent=user_agent)
    state = str(random.randint(0, 65000))
    url = reddit.auth.url(['mysubreddits', 'read', 'identity', 'history'], state, 'permanent')
    return url

def parse_authorisation_error(authorisation):    
    if authorisation[0] == 'STATE_ERROR':
        print('State mismatch. Expected: {} Received: {}'.format(authorisation[1],
                                                                 authorisation[2]))        
    elif authorisation[0] == 'DECLINED_AUTHORISATION':
        print('User declined authentication')

        
def get_authenticated_user_data(refresh_token):
    
    config = configparser.ConfigParser()
    config.read(INI_FILE)
    client_id = config['REDDIT_API']['client_id']
    client_secret = config['REDDIT_API']['client_secret']
    user_agent = config['REDDIT_API']['user_agent']
    
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         refresh_token=refresh_token,
                         user_agent=user_agent)
    print('Now authorised as: {}'.format(reddit.user.me()))

    keywords = get_data(reddit.user.me())
    
    # Change this to sent a request
    #
    #
    params = dict(
        keywords = keywords
    )
    r = requests.get("http://34.66.204.144:5000/model", params=params)
    sublist_json = r.json()
    sublist = sublist_json['sublist']
    
    return sublist

def get_data(user_name):
    #print("Currently processing user {}".format(row[0]))
    user = create_redditor(str(user_name))

    comments, commented_subreddits = get_comments_and_subreddits_users_have_commented_in(user)
    #if commented_subreddits == '':
        
    submissions = get_submissions(user)

    comments_keywords = ""
    submission_keywords = ""

    #print("Getting keywords from user comments")
    if comments != '':
        comments_keywords = extract_comment_keywords(comments)
    #print("Getting keywords from user submissions")
    if submissions != '': 
        submission_keywords = extract_submission_keywords(submissions)
    
    return "%s,%s" % (comments_keywords, submission_keywords)
        



if __name__ == '__main__':    
    new_user()