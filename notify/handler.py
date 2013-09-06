# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Request Handler for /notify endpoint."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import io
import json
import logging
import webapp2

from apiclient.http import MediaIoBaseUpload
from oauth2client.appengine import StorageByKeyName

from model import Credentials
import util

latlong = {((41.965491, 41.964765), (-71.18446, -71.18317)): "Old Science Center", ((41.967438, 41.967238), (-71.186934, -71.186289)): "The Sem"}

# latlongPoints = {((x1,y1),(x2,y2),(x3,y3),(x4,y4)): "Place", ... }
# make sure points are in order
latlongPoints = {((0,4), (4, 4), (4, 0), (0,0)): "box"}

class Mapper():
    def __init__(self, lat, longi):
        self.location = None
        for key, value in latlongPoints.iteritems():
            if point_in_poly(lat, longi, key):
                self.location = value


    def point_in_poly(x,y,poly):
        # Determine if a point is inside a given polygon or not
        # Polygon is a list of (x,y) pairs. This function
        # returns True or False.  The algorithm is called
        # the "Ray Casting Method".

        n = len(poly)
        inside = False

        p1x,p1y = poly[0]
        for i in range(n+1):
            p2x,p2y = poly[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x,p1y = p2x,p2y

        return inside


class NotifyHandler(webapp2.RequestHandler):
  """Request Handler for notification pings."""

  def post(self):
    """Handles notification pings."""
    logging.info('Got a notification with payload %s', self.request.body)
    data = json.loads(self.request.body)
    userid = data['userToken']
    # TODO: Check that the userToken is a valid userToken.
    self.mirror_service = util.create_service(
        'mirror', 'v1',
        StorageByKeyName(Credentials, userid, 'credentials').get())
    if data.get('collection') == 'locations':
      self._handle_locations_notification(data)
    elif data.get('collection') == 'timeline':
      self._handle_timeline_notification(data)

  def _handle_locations_notification(self, data):
    """Handle locations notification."""
    location = self.mirror_service.locations().get(id=data['itemId']).execute()
    latitude = location.get('latitude')
    longitude = location.get('longitude')
    mapper = Mapper(latitude, longitude)
    building = mapper.location
    if building:
        text = 'Glass 299 Demo says you are in %s.' % building
        logging.info(text)
    else:
        text = 'Glass 299 Demo says you are at %s by %s.' % \
            (location.get('latitude'), location.get('longitude'))
    body = {
        'text': text,
        'location': location,
        'menuItems': [{'action': 'NAVIGATE'}],
        'notification': {'level': 'DEFAULT'}
    }
    self.mirror_service.timeline().insert(body=body).execute()

  def _handle_timeline_notification(self, data):
    """Handle timeline notification."""
    for user_action in data.get('userActions', []):
      if user_action.get('type') == 'SHARE':
        # Fetch the timeline item.
        item = self.mirror_service.timeline().get(id=data['itemId']).execute()

        # Create a dictionary with just the attributes that we want to patch.
        body = {
            'text': 'Python Quick Start got your photo! %s' % item.get('text', '')
        }

        # Patch the item. Notice that since we retrieved the entire item above
        # in order to access the caption, we could have just changed the text
        # in place and used the update method, but we wanted to illustrate the
        # patch method here.
        self.mirror_service.timeline().patch(
            id=data['itemId'], body=body).execute()

        # Only handle the first successful action.
        break
      else:
        logging.info(
            "I don't know what to do with this notification: %s", user_action)


NOTIFY_ROUTES = [
    ('/notify', NotifyHandler)
]
