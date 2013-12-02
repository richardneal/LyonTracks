# run: python make_html_test.py > test_output
# be sure to run in the Glass299/XML folder
# The templates must be in the same folder (Glass/XML)

# the file test_output will contain the html for every card in the allbuild list below



from xml.dom import minidom

allbuild = ["11 Howard Street",
"22 Howard Street",
"44 Howard Street",
"Admission",
"Balfour-Hood Campus Center",
"Beard Hall",
"Chapin Hall",
"Chase Round",
"Chase Square",
"Clark Athletic Field",
"Clark Center",
"Clark Hall",
"Cole Memorial Chapel",
"Counseling Center",
"Craigin Hall",
"Davis International House",
"Dolls House",
"Elisabeth W. Amen Nursery School",
"Elms House",
"Emerson",
"Everett Hall",
"Gebbie Hall",
"Green House",
"Haas Athletic Center",
"Keefe Athletic Field",
"Keefe Hall",
"Kilham Hall",
"Knapton Hall",
"Kollett Hall",
"Larcom Hall",
"Lot 1A",
"Lyons Den",
"Madeleine Clark Wallace Library",
"Mars Arts and Humanities",
"Mars Center for Science and Technology",
"Marshall Center for Intercultural Learning",
"Mary Lyon",
"McIntire Hall",
"Meadows Center",
"Meadows East",
"Meadows North",
"Meadows West",
"Meneely",
"Metcalf Hall",
"Norton Medical Center",
"Old Observatory",
"Old Town Hall Bookstore",
"Park Hall",
"Presidents House",
"Public Safety",
"Science Center",
"Sidell Stadium",
"Stanton Hall",
"The Sem",
"Watson Fine Arts",
"White House",
"Young Hall"]

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
	def __init__(self, value):
		#print(value)
		self.name = value
		self.cards = []

		self.get_xml_data()
		#break

	def add_card(self, card):
		self.cards.append(card)

	def get_xml_data(self):
		try:
			xmlDoc = minidom.parse(self.name.replace("'", "") + ".xml")
		except:
			xmlDoc = minidom.parse("Wheaton College.xml")

		building = xmlDoc.getElementsByTagName('building')

			
		for card in building[0].getElementsByTagName('card'):
			type_card = Card()
			if card.attributes['type'].value == "spring_fling":
				type_card.set_kind("spring_fling")
				type_card.add_image(card.getElementsByTagName("image")[0].attributes['url'].value)
				type_card.add_fact(card.getElementsByTagName("text")[0].childNodes[0].nodeValue)
			elif card.attributes['type'].value == "secret_agent":
				type_card.set_kind("secret_agent")
				type_card.add_image(card.getElementsByTagName("image")[0].attributes['url'].value)
				for text in card.getElementsByTagName("text"):
					type_card.add_fact(text.childNodes[0].nodeValue)
			elif card.attributes['type'].value =="paragraph":
				type_card.set_kind("paragraph")
				type_card.add_fact(card.getElementsByTagName("text")[0].childNodes[0].nodeValue)
			elif card.attributes["type"].value == "modified_abe":
				type_card.set_kind("modified_abe")
				type_card.add_image(card.getElementsByTagName("image")[0].attributes['url'].value)
				type_card.add_fact(card.getElementsByTagName("text")[0].childNodes[0].nodeValue)
			else:
				type_card.set_kind("err")
			self.add_card(type_card)

def main():

		for value in allbuild:
			building = Building(value)
			if hasattr(building, 'name'):
				html = ""
				for card in building.cards:
					if card.kind == "err":
						print("err at " + building.name)
					else:
						f = open(card.kind + '.html', 'r')
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

			print(html + "\n")
main()
