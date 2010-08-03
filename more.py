#!/usr/bin/env python

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util

from post import Post

import helper, config

class ImageHandler(webapp.RequestHandler):
    def get(self):
        try:
            post = db.get(self.request.get('p'))
        except:
            self.redirect('/')
            return

        self.response.out.write(helper.render('more', {'post': post}))


application = webapp.WSGIApplication([('/more.html', ImageHandler)], debug=config.DEBUG)

if __name__ == '__main__':
  util.run_wsgi_app(application)
