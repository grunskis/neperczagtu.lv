#!/usr/bin/env python

import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from post import Post

import helper, config, logging

class PostsHandler(webapp.RequestHandler):
    def get(self, post_id=None, action=None):
        if action is None:
            posts = Post.all()
            self.response.out.write(helper.render('admin/posts', { 'posts': posts }))
        elif action == "delete":
            Post.get_by_id(int(post_id)).delete()
            return self.redirect('/admin/posts')
        elif action == "confirm":
            post = Post.get_by_id(int(post_id))
            post.confirmed_at = datetime.datetime.today()
            post.put()
            return self.redirect('/admin/posts')

urls = [
    ('/admin/posts', PostsHandler),
    ('/admin/posts/(\d+)/(delete|edit|confirm)', PostsHandler)
    ]

application = webapp.WSGIApplication(urls, debug=config.DEBUG)

def main():
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
