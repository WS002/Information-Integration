#!/usr/bin/python
# Need to use a streaming cursor approach to parse the XML data, due to it being too large to load it into a DOM Tree first and then traverse it. => Use SAX, which is event-based streaming cursor. Overload the ContentHandler class and its event functions startElement and endElement.
#from __future__ import print_function

import xml.sax
import bz2
import sys
from datetime import datetime # For timing

# Add the main folder to the python library, so that we can import our database singleton
sys.path.append('../')
import database

# Get instance of the database connection
myDB = database.DBConnection()

class XMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.node = ""
        self.xmlpath = []
        self.title = ""
        self.content = ""
        self.state = "none"
        self.maxlen = 0
        self.articlecounter = 0

    # Call when an element starts
    def startElement(self, tag, attributes):
        self.xmlpath.append(tag)
        if tag == "title" and self.xmlpath == ["mediawiki","page","title"]:
            self.state = "title"
        elif tag == "text" and self.xmlpath == ["mediawiki","page","revision","text"]:
            self.state = "content"
            self.content = ""

    def characters(self, content):
        if self.state == "title":
            self.title = content
            self.state = "none"
        elif self.state == "content":
            self.content += content

            # Call when an elements ends

    def endElement(self, tag):
        self.xmlpath.pop()
        if  self.state == "content":
            self.state = "none"
            try:
                myDB.executeQuery("INSERT INTO wiki_articles (title, content) VALUES (%s, %s)", (self.title, self.content))
                print 'Saved article "%s" to DB' % self.title
            except Exception as e:
                print 'Article "%s" caused an error:' % self.title, e

if (__name__ == "__main__"):
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    # override the default ContextHandler
    Handler = XMLHandler()
    parser.setContentHandler(Handler)

    start = datetime.now()
    parser.parse(bz2.BZ2File("dewiki-20161101-pages-meta-current.xml.bz2"))
    print "Passed file in", datetime.now() - start