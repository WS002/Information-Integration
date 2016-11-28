#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import io, sys
import urllib3, json
from requests.utils import quote

class WikiAPI:

	def __init__(self):

		# Create a HTTP connection pool manager
		self.HTTPManager = urllib3.PoolManager()		

	
	

	def openSearchDE(self, keyword):
		articleResponse = self.HTTPManager.request('GET', 'https://de.wikipedia.org/w/api.php?action=opensearch&search='+quote(keyword, safe='')+'&limit=1&namespace=0&format=json')
		if articleResponse.status >= 400:
			return 0
		else:
			return articleResponse.data


	def extractParagraph(self, wikiTitle):
		paragraphResponse = self.HTTPManager.request('GET', 'https://de.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&format=json&titles=' + quote(wikiTitle, safe=''))
		if paragraphResponse.status >= 400:
			return 0
		else:
			return paragraphResponse.data
	

