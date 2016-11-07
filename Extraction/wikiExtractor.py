#!/usr/bin/python
# Need to use a streaming cursor approach to parse the XML data, due to it being too large to load it into a DOM Tree first and then traverse it. => Use SAX, which is event-based streaming cursor. Overload the ContentHandler class and its event functions startElement and endElement.
import xml.sax
import bz2
import re

class XMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.node = ""
        self.xmlpath = []
        self.title = ""
        self.content = ""
        self.state = "none"

    # Call when an element starts
    def startElement(self, tag, attributes):
        self.xmlpath.append(tag)
        if tag == "title" and self.xmlpath == ["mediawiki","page","title"]:
            self.state = "title"
        elif tag == "text" and self.xmlpath == ["mediawiki","page","revision","text"]:
            self.state = "content"

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
            print "Page read complete. Do internal Handling here."
            print "title:", self.title
            print "content:", self.content
            #for i, part in enumerate(re.split("\n==[^=]", self.content)):
            #    print "Part %d: ==" % i, part
            exit(1)


if (__name__ == "__main__"):
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    # override the default ContextHandler
    Handler = XMLHandler()
    parser.setContentHandler(Handler)
    parser.parse(bz2.BZ2File("dewiki-20161101-pages-meta-current.xml.bz2"))