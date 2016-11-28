#!/usr/bin/python
# Need to use a streaming cursor approach to parse the XML data, due to it being too large to load it into a DOM Tree first and then traverse it. => Use SAX, which is event-based streaming cursor. Overload the ContentHandler class and its event functions startElement and endElement.
import xml.sax
import sys

# Install dateutil module with pip:
# sudo apt-get install python-pip
# sudo pip install python-dateutil

import dateutil.parser

# Add the main folder to the python library, so that we can import our database singleton 
sys.path.append('../')
import database

# Get instance of the database connection
myDB = database.DBConnection()

class Tag:
	def __init__(self, k, v):
		self.k = k
		self.v = v

class Node:
	def __init__(self, lat, lon):
		self.lat = lat
		self.lon = lon
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
			lat = attributes["lat"]
			lon = attributes["lon"]

		elif tag == "tag":			
			k = attributes["k"]			
			v = attributes["v"]
			#Extract only tourism nodes
			possibleTourismValues = ('aquarium', 'attraction', 'gallery', 'museum', 'theme_park', 'zoo', 'view_point')
			if k == "tourism" and v in possibleTourismValues:
				self.node.saveToDB = 1
			self.node.addTag(Tag(k, v))


	# Call when an elements ends
	def endElement(self, tag):
		if tag == "node":
			if self.node.saveToDB == 1:				
				print "End of node. Node contains tourism tag with the right values, save to DB!"
				# save self.node class to DB	

				# Do a bunch of insert statements into the db schema			
				cursor = myDB.executeQuery("INSERT INTO osm_nodes (lat, lon) VALUES (%s, %s, %s)", (self.node.lat, self.node.lon) )
				nodeID = cursor.lastrowid
				for tag in self.node.tags:
					myDB.executeQuery("INSERT INTO osm_tags (node_id, k, v) VALUES (%s, %s, %s)", (nodeID, tag.k, tag.v) )
							
	

if ( __name__ == "__main__"):
	# create an XMLReader
	parser = xml.sax.make_parser()
	# turn off namepsaces
	parser.setFeature(xml.sax.handler.feature_namespaces, 0)
	# override the default ContextHandler
	Handler = XMLHandler()
	parser.setContentHandler( Handler )
	parser.parse("openStreetMapData.xml")
