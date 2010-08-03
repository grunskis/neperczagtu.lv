#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, os

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util, template
from google.appengine.api import mail
from google.appengine.api.labs import taskqueue
from post import Post

import helper, config

class ConfirmationHandler(webapp.RequestHandler):
    def handle_error(self, message):
        self.redirect('/new?error_message=%s' % message)

    def send_confirmation_request(self, post):
        try:
            message = mail.EmailMessage(sender="do-not-reply@neperczagtu.appspotmail.com",
                                        to=self.request.get('email'),
                                        subject='Apstiprināt zagtu velosipēdu!')

            directory = os.path.dirname(__file__)
            
            template_file = os.path.join(directory, 'views', 'confirmation.html')
            message.html = template.render(template_file, {'post': post}, True)

            message.check_initialized()
        except mail.InvalidEmailError:
            self.handle_error('Invalid email recipient.')
            return
        except mail.MissingRecipientsError:
            self.handle_error('You must provide a recipient.')
            return
        except mail.MissingBodyError:
            self.handle_error('You must provide a mail format.')
            return

        message.send()

    def send_information(self, post):
        try:
            message = mail.EmailMessage(sender="do-not-reply@neperczagtu.appspotmail.com",
                                        to=post.email,
                                        subject='Ieraksts apstiprināts!')

            directory = os.path.dirname(__file__)
            
            template_file = os.path.join(directory, 'views', 'information.html')
            message.html = template.render(template_file, {'post': post}, True)

            message.check_initialized()
        except mail.InvalidEmailError:
            self.handle_error('Invalid email recipient.')
            return
        except mail.MissingRecipientsError:
            self.handle_error('You must provide a recipient.')
            return
        except mail.MissingBodyError:
            self.handle_error('You must provide a mail format.')
            return

        message.send()

    def get(self):
        try:
            post = db.get(self.request.get('p'))
        except:
            self.redirect('/')
            return

        s = self.request.get('s')
        if s:
            if s == post.secret:
                if not post.confirmed_at:
                    post.confirmed_at = datetime.datetime.today()
                    post.put()
                
                    # send info on how to edit post
                    self.send_information(post)
                    # update twitter
                    taskqueue.add(url='/post/twitter', params={'key': post.key()})
            else:
                logging.warning('Somebody tried to confirm post (key=%s) with incorrect secret (s=%s)', (post.key, s))
            return self.redirect('/')
        else:
            self.send_confirmation_request(post)
            self.response.out.write(helper.render('confirm', { 'email': self.request.get('email') }))

application = webapp.WSGIApplication([('/confirm', ConfirmationHandler)], debug=config.DEBUG)

if __name__ == '__main__':
    util.run_wsgi_app(application)
