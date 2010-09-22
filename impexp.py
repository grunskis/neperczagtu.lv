import base64

from google.appengine.api import images
from google.appengine.api import datastore_types
from google.appengine.ext.bulkload.transform import none_if_empty

def blobproperty_from_base64_with_img_resize(width):
  @none_if_empty
  def wrapper(value):
    decoded_value = base64.b64decode(value)
    return datastore_types.Blob(images.resize(decoded_value, width))
  
  return wrapper
