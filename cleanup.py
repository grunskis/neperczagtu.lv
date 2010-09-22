#!/usr/bin/env python

# http://code.google.com/appengine/articles/update_schema.html

# delete post.created_by field
# delete post.service field
# create user object for posts that doesn't already have it

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util, template

from post import Post, AuthToken

import config, urllib

class CleanupHandler(webapp.RequestHandler):
    def get(self):
        secret = self.request.get('secret', None)
        if secret is None:
            post = Post.gql('ORDER BY secret DESC').get()
            secret = post.secret
    
        q = Post.gql('WHERE secret <= :1 ORDER BY secret DESC', secret)
        posts = q.fetch(limit=2)
        current_post = posts[0]
        if len(posts) == 2:
            next_secret = posts[1].secret
            next_url = '/admin/cleanup?secret=%s' % urllib.quote(next_secret)
        else:
            next_secret = 'FINISHED'
            next_url = '/'

#        # model has to be of db.Model type
#        if current_post.user is None:
#            user = AuthToken(service="twitter", token="dummy")
#            user.name = current_post.created_by
#            user.url = "http://twitter.com/" + user.name
#            user.put()
#            current_post.user = user
            
        if hasattr(current_post, 'created_by'):
            delattr(current_post, 'created_by')
        if hasattr(current_post, 'service'):
            delattr(current_post, 'service')
        current_post.put()
    
        context = {
            'current_secret': secret,
            'next_secret': next_secret,
            'next_url': next_url,
            }
        self.response.out.write(template.render('cleanup.html', context))

application = webapp.WSGIApplication([('/admin/cleanup', CleanupHandler)], debug=config.DEBUG)

def main():
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
