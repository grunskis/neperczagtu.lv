#!/usr/bin/env python

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util

from post import Post

import config

class ImageHandler(webapp.RequestHandler):
    def get(self, key, size="normal"):
        try:
            post = db.get(key)
            if post.photo and post.thumbnail:
                self.response.headers['Content-Type'] = "image/png"
                if not size or size == "normal":
                    self.response.out.write(post.photo)
                else:
                    self.response.out.write(post.thumbnail)
        except:
            self.error(404)


application = webapp.WSGIApplication([('/img_(.*)-(.*)\.png', ImageHandler)], debug=config.DEBUG)

def main():
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
