#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import wikiAPI
import sys
# Add the main folder to the python library, so that we can import our database singleton
sys.path.append('../../')
import database
import json

# Get instance of the database connection
myDB = database.DBConnection()

wikiAPI = wikiAPI.WikiAPI()


def insertArticle(name):
	openSearch = wikiAPI.openSearchDE(name.encode('utf-8'))
	if openSearch != 0:
		searchResponse = json.loads(openSearch)
		if searchResponse[1] != '':
			if len(searchResponse[1]) > 0:
				print "Found article: " + searchResponse[1][0]
				paragraphResponse = wikiAPI.extractParagraph(searchResponse[1][0].encode('utf-8'))
				if paragraphResponse != 0:
					pages = json.loads(paragraphResponse)['query']['pages']
					for page in pages:
						# Save pages[page]['title'] as title
						# Save pages[page]['extract'] as content
						myDB.executeQuery("INSERT INTO wiki_articles (title, content) VALUES (%s, %s)", (pages[page]['title'], pages[page]['extract']))



# Get wiki articles for all osm_tags with k = name 

sql="SELECT v FROM osm_tags WHERE k='name'"
cursor = myDB.conn.cursor(buffered=True)
cursor.execute(sql)

for (resultList) in cursor:
	name = resultList[0]
	insertArticle(name)
	
cursor.close()


# Get wiki articles with all foursquare_venues with name

sql="SELECT name FROM foursquare_venues"
cursor = myDB.conn.cursor(buffered=True)
cursor.execute(sql)

for (resultList) in cursor:
	name = resultList[0]
	insertArticle(name)
	
cursor.close()
