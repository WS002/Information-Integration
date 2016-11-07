#!/usr/bin/python
# Need to use a streaming cursor approach to parse the XML data, due to it being too large to load it into a DOM Tree first and then traverse it. => Use SAX, which is event-based streaming cursor. Overload the ContentHandler class and its event functions startElement and endElement.
import xml.sax

class Tag:
	def __init__(self, k, v):
		self.k = k
		self.v = v

class Node:
	def __init__(self, ID, lat, lon, ver, timestamp):
		self.ID = ID
		self.lat = lat
		self.lon = lon
		self.ver = ver
		self.timestamp = timestamp
		# If the node contains a tag named tourism, save the whole node instance into the DB
		self.saveToDB = 0
		self.tags = []

	def addTag(self, tag):
		self.tags.append(tag)

class XMLHandler( xml.sax.ContentHandler ):
	def __init__(self):
		self.CurrentData = ""
		self.node = ""


	# Call when an element starts
	def startElement(self, tag, attributes):
		self.CurrentData = tag
		if tag == "node":			
			print ""
			print "*****Node*****"

			ID = attributes["id"]
			print "ID:", ID
			print ""

			lat = attributes["lat"]
			print "Lat:", lat
			lon = attributes["lon"]
			print "Lon:", lon
			version = attributes["version"]
			print "Version:", version
			timestamp = attributes["timestamp"]
			print "Timestamp:", timestamp
			print ""
			self.node = Node(ID, lat, lon, version, timestamp)

		elif tag == "tag":			
			k = attributes["k"]
			#Extract only tourism nodes
			print "Key:", k			
			v = attributes["v"]
			print "Value:", v
			#save tag to nodeID = self.node
			if k == "tourism":
				self.node.saveToDB = 1
			self.node.addTag(Tag(k, v))


	# Call when an elements ends
	def endElement(self, tag):
		if tag == "node":
			print ""
			if self.node.saveToDB == 1:				
				print "End of node ", self.node.ID , " . Node contains tourism tag, save to DB!"
				# save self.node class to DB
			else:
				print "End of node ", self.node.ID , " . Node contains NO tourism tag, DO NOT save to DB!" 
	

if ( __name__ == "__main__"):
	# create an XMLReader
	parser = xml.sax.make_parser()
	# turn off namepsaces
	parser.setFeature(xml.sax.handler.feature_namespaces, 0)
	# override the default ContextHandler
	Handler = XMLHandler()
	parser.setContentHandler( Handler )
	parser.parse("openStreetMapData.xml")
