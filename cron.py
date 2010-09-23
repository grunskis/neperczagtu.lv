#!/usr/bin/env python

import logging

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util

import config

from post import *

class CleanupHandler(webapp.RequestHandler):
    def get(self):
        tokens = AuthToken.all() # TODO: select only tokens older than 1 hour
        
        for token in tokens:
            post = Post.gql("WHERE user = :1", token).get()
            if post is None:
                token.delete()
                logging.info("AuthToken (id=%d) deleted..." % token.key().id())

application = webapp.WSGIApplication([('/cron/cleanup_auth_tokens', CleanupHandler)], debug=config.DEBUG)

def main():
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
