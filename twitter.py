#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from datetime import datetime

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util
from google.appengine.api.labs import taskqueue
from google.appengine.api import urlfetch

from django.utils import simplejson as json

from oauth import TwitterClient
from post import Post

import config, secret

class TwitterWorker(webapp.RequestHandler):
    def update_twitter(self, post, found=False):
        try:
            client = TwitterClient(secret.CONSUMER_KEY,
                                   secret.CONSUMER_SECRET, "/")
            
            info_url = "http://www.neperczagtu.lv/info/%s" % post.key().id()
            params = {}
            
            if found:
                params['status'] = "Tikko atrasts velosipēds: %s :)" % info_url
            else:
                params['status'] = "Tikko pievienots nozagts velosipēds: %s :(" % info_url

            response = client.make_request("http://api.twitter.com/1/statuses/update.json",
                                           secret.TOKEN,
                                           secret.TOKEN_SECRET,
                                           params,
                                           True,
                                           urlfetch.POST)

            data = json.loads(response.content)
            
            logging.info('Twitter status update response: %s' % data)
        except Exception, e:
            self.error(500)
            logging.exception(e)
            return False
        
        return True
    
    def post(self):
        key = self.request.get('key')
        
        def txn():
            post = db.get(key)
            if post.found_at and post.service_updated_at:
                # new found bike
                if self.update_twitter(post, found=True):
                    post.service_updated_at = datetime.utcnow()
                    post.put()
            else:
                # new stolen bike
                if self.update_twitter(post):
                    post.service_updated_at = datetime.utcnow()
                    post.put()
                
        db.run_in_transaction(txn)


application = webapp.WSGIApplication([('/post/twitter', TwitterWorker)], debug=config.DEBUG)

def main():
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
