from xml.dom import minidom

def get_xml_data(building_name="Wheaton College"):
    xmldoc = minidom.parse("XML/" + building_name + ".xml")
    building = xmldoc.getElementsByTagName('building')

    img = building[0].getElementsByTagName('image')[0].attributes['url'].value
    print img

    for card in building[0].getElementsByTagName('card'):
    	if card.attributes['type'].value == "facts":
    		for fact in card.getElementsByTagName("fact"):
    			print fact.childNodes[0].nodeValue

get_xml_data()