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

import json
import logging
from xml.dom import minidom

import webapp2
from apiclient.http import MediaIoBaseUpload
from oauth2client.appengine import StorageByKeyName

from model import Credentials
import util

import coordinates


class Card:
	def __init__(self):
		self.facts = []

	def add_fact(self, fact):
		self.facts.append(fact)

	def add_image(self, img_url):
		self.image = img_url

#	def add_text(self, text):
#		self.text = text

	def set_kind(self, kind):
		self.kind = kind


class Building:
	def __init__(self, latitude, longitude):
		for key, value in coordinates.latlongpoints.iteritems():
			if self.point_in_poly(latitude, longitude, key):
				self.name = value
				self.cards = []

				self.get_xml_data()
				break

	def add_card(self, card):
		self.cards.append(card)

	def point_in_poly(self, x, y, poly):
		# Determine if a point is inside a given polygon or not
		# Polygon is a list of (x,y) pairs. This function
		# returns True or False.  The algorithm is called
		# the "Ray Casting Method".

		n = len(poly)
		inside = False

		p1x, p1y = poly[0]
		for i in range(n + 1):
			p2x, p2y = poly[i % n]
			if y > min(p1y, p2y):
				if y <= max(p1y, p2y):
					if x <= max(p1x, p2x):
						if p1y != p2y:
							xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
						if p1x == p2x or x <= xints:
							inside = not inside
			p1x, p1y = p2x, p2y

		return inside

	def get_xml_data(self):
		try:
			xmlDoc = minidom.parse("XML/" + self.name.replace("'", "") + ".xml")
		except IOError:
			xmlDoc = minidom.parse("XML/Wheaton College.xml")
		building = xmlDoc.getElementsByTagName('building')

		for card in building[0].getElementsByTagName('card'):
			type_card = Card()
			if card.attributes['type'].value == "spring_fling":
				type_card.set_kind("spring_fling")
				type_card.add_image(card.getElementsByTagName("image")[0].attributes['url'].value)
				type_card.add_fact(card.getElementsByTagName("text")[0].childNodes[0].nodeValue)
			elif card.attributes['type'].value == "secret_agent":
				type_card.set_kind("secret_agent")
				#type_card.set_kind("secret_agent_num2")
				type_card.add_image(card.getElementsByTagName("image")[0].attributes['url'].value)
				for text in card.getElementsByTagName("text"):
					type_card.add_fact(text.childNodes[0].nodeValue)
			elif card.attributes['type'].value == "paragraph":
				type_card.set_kind("paragraph")
				type_card.add_fact(card.getElementsByTagName("text")[0].childNodes[0].nodeValue)
			elif card.attributes["type"].value == "modified_abe":
				type_card.set_kind("modified_abe")
				type_card.add_image(card.getElementsByTagName("image")[0].attributes['url'].value)
				type_card.add_fact(card.getElementsByTagName("text")[0].childNodes[0].nodeValue)
            else:
                type_card.set_kind("error")
			self.add_card(type_card)


class NotifyHandler(webapp2.RequestHandler):
	"""Request Handler for notification pings."""

	def post(self):
		"""Handles notification pings."""
		logging.info('Got a notification with payload %s', self.request.body)
		data = json.loads(self.request.body)
		userid = data['userToken']
		# TODO: Check that the userToken is a valid userToken.
		self.mirror_service = util.create_service('mirror', 'v1', StorageByKeyName(Credentials, userid, 'credentials').get())
		if data.get('collection') == 'locations':
			self._handle_locations_notification(data)
		elif data.get('collection') == 'timeline':
			self._handle_timeline_notification(data)

	def _handle_locations_notification(self, data):
		"""Handle locations notification."""
		location = self.mirror_service.locations().get(id=data['itemId']).execute()
		latitude = location.get('latitude')
		longitude = location.get('longitude')

		building = Building(latitude, longitude)

		if hasattr(building, 'name'):
			logging.info("Located user at %s", building.name)
			html = ""
			for card in building.cards:
                if card.kind == "error":
                    logging.info("card kind type error")
                else:
                    f = open('./html_templates/' + card.kind + '.html', 'r')
                    myHtml = f.read()
                    f.close()

                    if card.kind == "spring_fling":
                        html += myHtml.format(card.image, card.facts[0])
                    elif card.kind == "secret_agent":
                        html += myHtml.format(card.image, card.facts[0], card.facts[1])
                    elif card.kind == "modified_abe":
                        html += myHtml.format(card.image, card.facts[0])
                    elif card.kind == "paragraph":
                        html += myHtml.format(card.facts[0])

		else:
			html = 'Lyon Tracks says you are at {0} by {1}.'.format(latitude, longitude)
		logging.info("Posting location HTML to the Glass: %s", html)
		body = {
		'html': html,
		'location': location,
		#'menuItems': [{'action': 'NAVIGATE'}],
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
				logging.info("I don't know what to do with this notification: %s", user_action)


NOTIFY_ROUTES = [
	('/notify', NotifyHandler)
]
