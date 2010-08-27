#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from post import Post

import helper, config, logging

class MainHandler(webapp.RequestHandler):
  def get(self):
    posts = Post.all()
    if not config.DEBUG and not self.request.host_url.endswith('appspot.com'):
      posts.filter('confirmed_at !=', None)
    posts.order('-confirmed_at')

    values = {
      'posts': posts
    }
    self.response.out.write(helper.render('main', values))

application = webapp.WSGIApplication([('/', MainHandler)], debug=config.DEBUG)

def main():
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
