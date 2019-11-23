# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 21:10:09 2019

@author: David
"""

import joblib


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

    