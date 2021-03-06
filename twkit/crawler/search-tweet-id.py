#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################
# (c) 2016-2018 Polyvios Pratikakis
# polyvios@ics.forth.gr
###########################################

"""
get a list of tweet ids, and look them up using twitter api
"""

import sys
import tweepy
from twkit.utils import *
import json
import twitter
import optparse
from progress.bar import Bar
import config

auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)
db, twitterapi = init_state(use_cache=False)

idlist = []
for x in Bar("Lookup:", suffix = '%(index)d/%(max)d - %(eta_td)s').iter(sys.argv[1:]):
  twid = long(x)
  old = db.tweets.find_one({'id': twid})
  if old: continue
  idlist.append(twid)

bulk = db.tweets.initialize_unordered_bulk_op()
cursor = api.statuses_lookup(id_=idlist, trim_user=True)
for tweet in Bar("Tweets:", suffix = '%(index)d/%(max)d - %(eta_td)s').iter(cursor):
  j1 = tweet._json
  tw = twitter.Status.NewFromJsonDict(j1)
  j2 = pack_tweet(db, tw)
  bulk.insert(j2)
bulk.execute()
