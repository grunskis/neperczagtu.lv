#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, logging

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util
from google.appengine.api import images
from google.appengine.api.labs import taskqueue

import helper, oauth, config

from post import Post

class EditHandler(webapp.RequestHandler):
    def get(self):
        try:
            post = db.get(self.request.get('p'))
            if post.secret != self.request.get('s'):
                logging.warning('Somebody tried to update post (p=%s) with incorrect secret (s=%s)' % (self.request.get('p'), self.request.get('s')))
                self.redirect('/')
        except:
            self.redirect('/')
            return

        if not config.DEBUG and not post.confirmed_at:
            logging.warning('Somebody tried edit post (p=%s) that is not yet confirmed' % self.request.get('p'))
            return self.redirect('/')
        
        values = {
            'post': post, 'errors': []
        }
        self.response.out.write(helper.render('edit', values))

    def post(self):
        errors = []
        
        post = db.get(self.request.get('key'))

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
        else:
            if post.stolen_at:
                post.stolen_at = None
        
        photo = self.request.get("photo")
        if photo:
            try:
                thumbnail = images.resize(photo, 250)
                post.photo = db.Blob(images.resize(photo, 600))
                post.thumbnail = db.Blob(thumbnail)
                post.thumbnail_height = images.Image(thumbnail).height
            except Exception, e:
                logging.error(e)
                errors.append('Kļūda apstrādājot bildi (maksimāli pieļaujamais bildes izmērs ir 1 Mb)')

        if len(errors) > 0:
            data = {
                'post': post, 'errors': errors
            }
            self.response.out.write(helper.render('new', data))
            return

        if self.request.get('found', default_value="no") == "on":
            post.found_at = datetime.datetime.utcnow()

        post.put()
        
        # update twitter
        taskqueue.add(url='/post/twitter', params={'key': post.key()})
        
        self.redirect('/')


application = webapp.WSGIApplication([('/edit', EditHandler)], debug=config.DEBUG)
        
if __name__ == '__main__':
    util.run_wsgi_app(application)
