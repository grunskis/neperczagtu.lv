from google.appengine.ext import db

import oauth

class Post(db.Model):
  description = db.StringProperty(multiline=True)
  stolen_on = db.DateProperty()
  stolen_at = db.TimeProperty()
  email = db.EmailProperty()
  photo = db.BlobProperty()
  thumbnail = db.BlobProperty()
  thumbnail_height = db.IntegerProperty()
  created_at = db.DateTimeProperty(auto_now_add=True)
  updated_at = db.DateTimeProperty(auto_now=True)
  location = db.GeoPtProperty()
  confirmed_at = db.DateTimeProperty() # null if not confirmed
  created_by = db.StringProperty() # twitter username
  secret = db.StringProperty()
  found_at = db.DateTimeProperty() # null if not found
  found_comment = db.StringProperty(multiline=True)
  service = db.StringProperty(default="Twitter")
  service_updated_at = db.DateTimeProperty()
  user = db.ReferenceProperty(oauth.AuthToken)

