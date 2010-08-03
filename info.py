#!/usr/bin/env python

import logging

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util

from post import Post

import helper, config

class InfoHandler(webapp.RequestHandler):
    def get(self, post_id):
        try:
            post = Post.get_by_id(int(post_id))
            if not post:
                raise Exception('Post with id %s not found' % post_id)
        except Exception, e:
            logging.error(e)
            self.redirect('/')
            return

        self.response.out.write(helper.render('info', {'post': post}))

application = webapp.WSGIApplication([('/info/(\d+)', InfoHandler)], debug=config.DEBUG)
        
if __name__ == '__main__':
  util.run_wsgi_app(application)
