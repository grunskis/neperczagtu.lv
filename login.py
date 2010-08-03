#!/usr/bin/env python

import logging, traceback, sys, cgi, os

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from django.utils import simplejson as json

import oauth, helper, config, urllib, secret

DRAUGIEM_APP_ID="2256"
FACEBOOK_APP_ID = "119851754705738"

class BaseLoginHandler(webapp.RequestHandler):
    def handle_exception(self, exception, debug_mode):
        self.error(500)
        logging.exception(exception)
        if debug_mode:
            lines = ''.join(traceback.format_exception(*sys.exc_info()))
            self.response.clear()
            self.response.out.write('<pre>%s</pre>' % (cgi.escape(lines, quote=True)))
        else:
            self.response.out.write(helper.render('500'))


class DraugiemLoginHandler(BaseLoginHandler):
    def get(self):
        auth_status = self.request.get('dr_auth_status')
        if auth_status:
            if auth_status == 'ok':
                auth_code = self.request.get('dr_auth_code')
                args = dict(app=secret.DRAUGIEM_API_KEY, code=auth_code, action='authorize')
                result = json.load(urllib.urlopen("http://api.draugiem.lv/json/?" + urllib.urlencode(args)))

                logging.info(result) # log users profile

                username = ''
                current_user = result['users'][result['uid']]
                if 'name' in current_user:
                    username = current_user['name']
                    if 'surname' in current_user:
                        username = username + ' ' + current_user['surname']

                if not username or len(username) <= 0:
                    logging.error('User has no name :)')
                    return self.redirect('/')
                
                user = oauth.AuthToken(name=username, token=result['apikey'], service='draugiem')
                if 'place' in result:
                    user.location = result['place']
                user.url = db.Link('http://www.draugiem.lv/friend/?%s' % result['uid'])
                user.put()

                return self.redirect("/new?dr=" + result['apikey'])
            elif auth_status == 'failed':
                logging.warning('User disallowed access to profile')
            else:
                logging.error('Unknown auth_code: ' + auth_status)
            return self.redirect('/')
        else:
            redirect_url = self.request.path_url
            hash = helper.draugiem_hash(secret.DRAUGIEM_API_KEY, redirect_url)
            args = dict(app=DRAUGIEM_APP_ID, hash=hash, redirect=redirect_url)
            return self.redirect("http://api.draugiem.lv/authorize/?" + urllib.urlencode(args))

class FacebookLoginHandler(BaseLoginHandler):
    def get(self):
        verification_code = self.request.get("code")
        args = dict(client_id=FACEBOOK_APP_ID, redirect_uri=self.request.path_url)
        if verification_code:
            args["client_secret"] = secret.FACEBOOK_APP_SECRET
            args["code"] = verification_code
            response = cgi.parse_qs(urllib.urlopen(
                "https://graph.facebook.com/oauth/access_token?" +
                urllib.urlencode(args)).read())
            access_token = response["access_token"][-1]

            # Download the user profile and cache a local instance of the
            # basic profile info
            profile = json.load(urllib.urlopen(
                "https://graph.facebook.com/me?" +
                urllib.urlencode(dict(access_token=access_token))))

            logging.info(profile) # log users profile

            id = str(profile['id'])
            user = oauth.AuthToken(id=id, name=profile["name"], token=access_token, service='facebook')
            if 'hometown' in profile:
                location = profile['hometown']['name']
            user.url = db.Link(profile['link'])
            user.put()
            
            self.redirect("/new?fb=" + access_token)
        else:
            self.redirect(
                "https://graph.facebook.com/oauth/authorize?" +
                urllib.urlencode(args))


class TwitterLoginHandler(BaseLoginHandler):
    def get(self):
        callback_url = "%s/new" % self.request.host_url
    
        client = oauth.TwitterClient(secret.CONSUMER_KEY,
                                     secret.CONSUMER_SECRET,
                                     callback_url)

        return self.redirect(client.get_authorization_url())


application = webapp.WSGIApplication([
        ('/login/twitter', TwitterLoginHandler),
        ('/login/facebook', FacebookLoginHandler),
        ('/login/draugiem', DraugiemLoginHandler)
], debug=config.DEBUG)

def main():
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
