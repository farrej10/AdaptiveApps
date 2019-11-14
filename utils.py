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
import socket
import random 
import webbrowser

INI_FILE = 'subsuggester.ini'

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
    comments = ''
    for comment in redditor.comments.new(limit=None):
        comments = '{} {}'.format(comments, comment.body)
    return comments

def get_subreddits(redditor):
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

def receive_connection():
    """Wait for and then return a connected socket..
    Opens a TCP connection on port 8080, and waits for a single client.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8000))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def authenticate_user(code):    
    
    config = configparser.ConfigParser()
    config.read(INI_FILE)
    client_id = config['REDDIT_API']['client_id']
    client_secret = config['REDDIT_API']['client_secret']
    user_agent = config['REDDIT_API']['user_agent']
    
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         redirect_uri="http://localhost:8000/suggestion",
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
                         redirect_uri="http://localhost:8000/suggestion",
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
    print('They are subscribed to:')
    for subreddit in reddit.user.subreddits():
        print(subreddit)
        
if __name__ == '__main__':    
    new_user()