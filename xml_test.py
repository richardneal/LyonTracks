from xml.dom import minidom
xmldoc = minidom.parse('information.xml')
itemlist = xmldoc.getElementsByTagName('building')

for building in itemlist:
    print building.attributes['name'].value
    for card in building.getElementsByTagName('card'):
    	if card.attributes['type'].value == "facts":
    		for fact in card.getElementsByTagName("fact"):
    			print fact.childNodes[0].nodeValue