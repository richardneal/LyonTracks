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
from xml.dom import minidom

from apiclient.http import MediaIoBaseUpload
from oauth2client.appengine import StorageByKeyName

from model import Credentials
import util

#latlong = {((41.965491, 41.964765), (-71.18446, -71.18317)): "Old Science Center", ((41.967438, 41.967238), (-71.186934, -71.186289)): "The Sem"}

latlongpoints = {((41.966584,-71.184175),(41.966899,-71.183285),(41.966592,-71.183129),(41.966377,-71.183869)): "Balfour",
                ((41.966448,-71.184121),(41.9665,-71.18396),(41.966253,-71.183783),(41.966233,-71.183955)): "Doll House",
                ((41.966149,-71.184604),(41.966313,-71.184052),(41.965986,-71.183805),(41.965754,-71.184384)): "Madeleine Clark Wallis Library",
                ((41.965914,-71.183923),(41.966261,-71.182979),(41.965966,-71.182641),(41.965479,-71.183488)): "Mars Center for Science and Technology",
                ((41.96522,-71.18439),(41.965479,-71.183767),(41.964925,-71.183344),(41.964701,-71.183944)): "Science Center",
                ((41.965455,-71.184518),(41.965555,-71.184255),(41.96534,-71.184127),(41.96524,-71.184373)): "Kollett",
                ((41.964833,-71.183478),(41.964917,-71.183285),(41.964757,-71.183167),(41.964689,-71.183381)): "Green House",
                ((41.964646,-71.183242),(41.9651,-71.18182),(41.96435,-71.181225),(41.963908,-71.182871)): "Haas Athletic Center",
                ((41.966584,-71.185795),(41.966544,-71.185344),(41.966105,-71.185226),(41.966038,-71.18572)): "Everett Hall",
                ((41.966624,-71.185248),(41.966708,-71.185076),(41.966409,-71.184888),(41.966329,-71.185066)): "Cragin Hall",
                ((41.966225,-71.185194),(41.966293,-71.185001),(41.96595,-71.18476),(41.965874,-71.184974)): "Stanton Hall",
                ((41.965754,-71.185382),(41.96587,-71.185044),(41.965679,-71.184899),(41.965535,-71.185248)): "Gebbie Hall",
                ((41.965766,-71.185575),(41.96579,-71.18542),(41.965667,-71.185414),(41.965643,-71.18558)): "22 Howard",
                ((41.965527,-71.185479),(41.965507,-71.18521),(41.965176,-71.18521),(41.96514,-71.185452)): "Keefe Hall",
                ((41.964985,-71.18594),(41.965001,-71.18506),(41.964757,-71.184947),(41.964757,-71.185935)): "Beard Hall",
                ((41.96504,-71.186203),(41.965032,-71.186053),(41.964917,-71.186063),(41.964917,-71.186203)): "Counseling Center",
                ((41.965008,-71.186771),(41.965012,-71.18661),(41.964873,-71.186616),(41.964869,-71.186766)): "44 Howard",
                ((41.964789,-71.186734),(41.964769,-71.186541),(41.964622,-71.186557),(41.96463,-71.186745)): "Lyon's Den",
                ((41.96631,-71.186133),(41.966328,-71.185886),(41.966156,-71.185884),(41.966144,-71.186125)): "White House",
                ((41.966651,-71.186326),(41.966729,-71.186163),(41.966655,-71.186098),(41.966591,-71.186264)): "11 Howard",
                ((41.966306,-71.186857),(41.96636,-71.186643),(41.966186,-71.186551),(41.966128,-71.186777)): "Old Town Bookstore",
                ((41.965471,-71.181064),(41.966089,-71.180624),(41.965611,-71.179395),(41.964973,-71.17983)): "Mirrione Stadium",
                ((41.96704,-71.186447),(41.967117,-71.186281),(41.96697,-71.186122),(41.966904,-71.186325)): "Davis International House",
                ((41.967244,-71.186503),(41.967301,-71.186382),(41.9672,-71.186293),(41.967151,-71.186408)): "Center for Global Education",
                ((41.967395,-71.186692),(41.967486,-71.186515),(41.967366,-71.186421),(41.96728,-71.186594)): "The Sem",
                ((41.967636,-71.186895),(41.9677,-71.186781),(41.967591,-71.186683),(41.967535,-71.186793)): "Marshall Center for Intercultural Learning",
                ((41.968614,-71.185972),(41.968778,-71.185505),(41.968562,-71.185371),(41.968407,-71.185833)): "President's House",
                ((41.967467,-71.182143),(41.967334,-71.182276),(41.967382,-71.181651),(41.967382,-71.181651)): "Meadows West",
                ((41.967334,-71.182276),(41.967382,-71.181651),(41.967382,-71.181651),(41.967382,-71.181651)) :"Meadows East",
                ((41.967777,-71.181997),(41.967856,-71.181719),(41.967728,-71.181624),(41.967631,-71.181901)) :"Meadows Center",
                ((41.967978,-71.181994),(41.968137,-71.181552),(41.968020,-71.181459),(41.967840,-71.181925)) :"Meadows North",
                ((41.968475,-71.182630),(41.968530,-71.182464),(41.968161,-71.182221),(41.968103,-71.182389)): "MacIntire Hall",
                ((41.968839,-71.183231),(41.968883,-71.183105),(41.968455,-71.182830),(41.968406,-71.182963)): "Clark Hall",
                ((41.969045,-71.182595),(41.969095,-71.182466),(41.968608,-71.18213),(41.968558,-71.182279)): "Young Hall",
                ((41.968327,-71.184846),(41.968521,-71.184229),(41.967959,-71.18462),(41.968212,-71.183985)): "Watson",
                ((41.967854,-71.184234),(41.968046,-71.183716),(41.967921,-71.183618),(41.967806,-71.183998)): "Meneely",
                ((41.967734,-71.184319),(41.967806,-71.183998),(41.967489,-71.184107),(41.967659,-71.183773)) : "Mars Arts and Humanities",
                ((41.968103,-71.183228),(41.968286,-71.182708),(41.968116,-71.182598),(41.967935,-71.18311)): "Chase Round",
                ((41.967974,-71.182955),(41.968084,-71.182665),(41.967896,-71.182544),(41.967793,-71.182839)): "Chase Square",
                ((41.970338,-71.185408),(41.970372,-71.185208),(41.970324,-71.18518),(41.970284,-71.185383)): "Old Observatory",
                ((41.967626,-71.180519),(41.967818,-71.179543),(41.966677,-71.179274),(41.966565,-71.180229)): "Keefe Athletic Field",
                ((41.98126,-71.185373), (41.968183, -71.185188), (41.96784, -71.184921), (41.967753,-71.185197)): "Mary Lyon",
                ((41.967649,-71.184897), (41.967775,-71.184585), (41.9674,-71.184284), (41.967294,-71.184673)): "Knapton",
                ((41.967164,-71.184572), (41.967358,-71.184089), (41.96719,-71.183913), (41.966979,-71.184455)): "Chapel",
                ((41.966845,-71.184373), (41.967027,-71.183916), (41.966741,-71.183726), (41.966578,-71.184199)): "Admissions",
                ((41.967786,-71.185735), (41.967838,-71.185574), (41.967521,-71.185373), (41.967465,-71.185534)): "Park Hall",
                ((41.967336,-71.186034), (41.967433,-71.185741), (41.967328,-71.185678), (41.967226,-71.185964)): "Chapin",
                ((41.967282,-71.185678), (41.96734,-71.185517), (41.967082,-71.185359), (41.967028,-71.185519)): "Larcom",
                ((41.966887,-71.185838), (41.967012,-71.185307), (41.966697,-71.185154), (41.966596,-71.185744)): "Emerson",
                ((41.968141,-71.187305), (41.968191,-71.187195), (41.968002,-71.187045), (41.96796,-71.18719)): "Nursery School",
                ((41.969282,-71.188166), (41.969523,-71.187611), (41.969178,-71.187391), (41.968937,-71.188051)): "Clark Center",
                ((41.967937,-71.186066), (41.967975,-71.185943), (41.9677,-71.185774), (41.967658,-71.185905)): "Metcalf",
                ((41.967794,-71.186444), (41.967844,-71.186323), (41.967571,-71.186146), (41.967525,-71.186267)): "Kilham",
                ((41.969995,-71.190441), (41.97041,-71.182501), (41.966493,-71.176386), (41.963908,-71.187115)): "Wheaton College"}


# latlongPoints = {((x1,y1),(x2,y2),(x3,y3),(x4,y4)): "Place", ... }
# make sure points are in order
# latlongPoints = {((0,4), (4, 4), (4, 0), (0,0)): "box"}

class Card:
    def __init__(self, building_name, card_kind):
        self.kind = card_kind
        self.name = building_name
        self.fact = []

    def add_fact(self, fact):
        self.fact.append(fact)

    def add_img():
        self.image.append(img_url)

        
    

class Building:
    def __init__(self, latitude, longitude):
        #self.name = None
        for key, value in latlongpoints.iteritems():
            if self.point_in_poly(latitude, longitude, key):
                self.cards = Card[]

                self.get_xml_data()

    def add_card(card):
        self.cards.append(card)

    def point_in_poly(self, x, y, poly):
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

    def get_xml_data(self):
        xmldoc = minidom.parse("XML/" + self.name + ".xml")
        building = xmldoc.getElementsByTagName('building')


        for card in building[0].getElementsByTagName('card'):
            if card.attributes['type'].value == "spring_fling":
                type_card = Card(card.getElementByTagName('image'), card.attributes['type'].value)
                for image in card.getElementByTagName('image')
                    type_card.add_image(image)
                for fact in card.getElementsByTagName("fact"):
                    type_card.add_fact(fact.childNodes[0].nodeValue)

                self.add_card(type_card)




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

    building = Building(latitude, longitude)

    if building:
        building_info = Building(building)
        get_xml_data(building_info)


    if building.name:

        f = open('./html_templates/spring_fling.html', 'w')
        myHtml = f.read()
        f.close()

        html = myHtml.format(building.name)

   #     f = open('./html_templates/secret_agent.html', 'w')
   #     myHtml = f.read()
   #     f.close()

   #     if building.history:
   #         html += myHtml.format(building.history[0], building.history[1], building.history[2])

   #     if building.current:
   #         html += """<article>
   #                     <section>
   #                         <ul>
   #                             <li>{0}</li>
   #                             <li>{1}</li>
   #                             <li>{2}</li>
   #                         </ul>
   #                     </section>
   #                 </article>""".format(building.current[0], building.current[1], building.current[2])
   #     
        logging.info(html)
    else:
        html = 'Glass 299 Demo says you are at %s by %s.' % \
            (location.get('latitude'), location.get('longitude'))
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
        logging.info(
            "I don't know what to do with this notification: %s", user_action)


NOTIFY_ROUTES = [
    ('/notify', NotifyHandler)
]
