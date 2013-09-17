from xml.dom import minidom

def get_xml_data(building_name="Wheaton College"):
    xmldoc = minidom.parse("XML/" + building_name + ".xml")
    building = xmldoc.getElementsByTagName('building')
    print building[0].attributes["name"].value
    for card in building[0].getElementsByTagName('card'):
    	if card.attributes['type'].value == "spring_fling":
            print card.getElementsByTagName("image")[0].attributes['url'].value
            print card.getElementsByTagName("text")[0].childNodes[0].nodeValue
        if card.attributes['type'].value == "secret_agent":
    		# print card.getElementsByTagName("image")[0].attributes['url'].value
            for fact in card.getElementsByTagName("fact"):
                print fact.childNodes[0].nodeValue
                
    			

get_xml_data()