#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, cgi, traceback, sys

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util
from google.appengine.api import images
from google.appengine.api import urlfetch

import helper, oauth, config, logging, secret

from post import *

class NewHandler(webapp.RequestHandler):
    def get_auth_token(self, token, service):
        return AuthToken.gql("WHERE service=:1 AND token=:2", service, token).get()

    def draugiem_new(self, auth_token):
        return self.get_auth_token(auth_token, 'draugiem')

    def twitter_new(self, auth_token, auth_verifier):
        token = self.get_auth_token(auth_token, 'twitter')

        if not token:
            return None
        
        if not token.name:
            callback_url = "%s/new" % self.request.host_url
            
            client = oauth.TwitterClient(secret.CONSUMER_KEY,
                                         secret.CONSUMER_SECRET,
                                         callback_url)

            user_info = client.get_user_info(auth_token, auth_verifier=auth_verifier)

            token.name = user_info['username']
            token.location = user_info['location']
            token.url = db.Link('http://twitter.com/%s' % token.name)
            token.put()
            
        return token
        
    def facebook_new(self, auth_token):
        return self.get_auth_token(auth_token, 'facebook')
        
    def get(self):
        auth_token = self.request.get("oauth_token")
        auth_verifier = self.request.get("oauth_verifier")
        fb_token = self.request.get("fb")
        dr_token = self.request.get("dr")

        if auth_token and auth_verifier:
            user = self.twitter_new(auth_token, auth_verifier)
        elif fb_token:
            user = self.facebook_new(fb_token)
        elif dr_token:
            user = self.draugiem_new(dr_token)
        else:
            logging.warning('/new called with incorrect parameters')
            return self.redirect('/')

        if not user:
            logging.warning("Failed to get username from service...")
            return self.redirect('/')

        post = Post()
        post.user = user
        
        self.response.out.write(helper.render('new', {'post': post}))

    def post(self):
        errors = []
        
        post = Post()
        post.user = db.get(self.request.get('user'))

        description = self.request.get('description')
        if not description or len(description.strip()) == 0:
            errors.append('Informācija par velosipēdu ir obligāta')
        else:
            post.description = description

        date = self.request.get('date')
        try:
            post.stolen_on = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except:
            errors.append('Norādīts kļūdains datums')

        time = self.request.get('time')
        if time:
            try:
                post.stolen_at = datetime.datetime.strptime(time, '%H:%M').timetz()
            except:
                errors.append('Norādīts kļūdains laiks')
            
        photo = self.request.get("photo")
        if not photo:
            errors.append('Nav norādīta bilde')
        else:
            try:
                thumbnail = images.resize(photo, 250)
                post.photo = db.Blob(images.resize(photo, 600))
                post.thumbnail = db.Blob(thumbnail)
                post.thumbnail_height = images.Image(thumbnail).height
            except Exception, e:
                logging.error(e)
                errors.append('Kļūda apstrādājot bildi (maksimāli pieļaujamais bildes izmērs ir 1 Mb)')

        email = self.request.get('email')
        try:
            post.email = db.Email(email)
        except:
            errors.append('Norādīts kļūdains e-pasts')

        latitude = float(self.request.get('lat'))
        longitude = float(self.request.get('lng'))
        post.location = db.GeoPt(latitude, longitude)
        
        if len(errors) > 0:
            data = {
                'post': post, 'errors': errors
            }
            self.response.out.write(helper.render('new', data))
            return

        post.secret = helper.create_secret(post)
        post.put()
        
        self.redirect('/confirm?p=%s&email=%s' % (post.key(), cgi.escape(email)))

    def handle_exception(self, exception, debug_mode):
        self.error(500)
        logging.exception(exception)
        if debug_mode:
            lines = ''.join(traceback.format_exception(*sys.exc_info()))
            self.response.clear()
            self.response.out.write('<pre>%s</pre>' % (cgi.escape(lines, quote=True)))
        else:
            self.response.out.write(helper.render('500'))

application = webapp.WSGIApplication([('/new', NewHandler)], debug=config.DEBUG)

def main():
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
