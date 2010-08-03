import os, hashlib

from google.appengine.ext.webapp import template

def create_secret(post):
    secret = hashlib.new('md5')
    secret.update(str(post.created_at))
    return secret.hexdigest()

def draugiem_hash(app, redirect_url):
    secret = hashlib.new('md5')
    secret.update(str(app) + str(redirect_url))
    return secret.hexdigest()

def render(name, data={}):
    filename = '%s.html' % name
    path = os.path.join(os.path.dirname(__file__), 'views', filename)
    return template.render(path, data)
