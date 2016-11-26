import io, sys
import urllib3, json
import datetime
import time
import pytz

# Needed to parse the config file
import ConfigParser
import os


class FoursquareAPI:

	def __init__(self, outputFile):
############################## Parse options ###############################################
		Config = ConfigParser.ConfigParser()
		path = os.path.dirname(os.path.realpath(__file__))
		Config.read(path + "/foursquareOptions.cfg")

		self.options = {}
		for option in Config.options("City"):
			self.options[option] = Config.get("City", option).rstrip('\n')
		for option in Config.options("FoursquareAuth"):
			self.options[option] = Config.get("FoursquareAuth", option).rstrip('\n')
		for option in Config.options("Foursquare"):
			self.options[option] = Config.get("Foursquare", option).rstrip('\n')
############################################################################################

		# Create a HTTP connection pool manager
		self.HTTPManager = urllib3.PoolManager()		
		self.outputFileHandle = open(outputFile, 'w')		
		self.categories = {}
				
		try:			
			mainCategories = json.loads(self.getCategories())['response']['categories']		
			# Populate dynamically the self.categories list depending on tree deep level, defined in options. 
			self._traverseCategories(mainCategories)
		except Exception:
			print "Could not parse categories! Out of request limit?"
		
	
	

	def getVenuesPerCategory(self, categoryId):
		venueRequest = self.HTTPManager.request('GET', 'https://api.foursquare.com/v2/venues/search?near=' + self.options['city'] + '&radius='+self.options['radius']+ '&categoryId='+ categoryId +'&limit='+self.options['venue_limit']+'&intent=browse&client_id='+self.options['client_id'] + '&client_secret='+self.options['client_secret']+'&v=' + datetime.datetime.now().strftime('%Y%m%d'))
		if venueRequest.status >= 400:
			return 0
		else:
			return venueRequest.data

	def getCategories(self):
		categoryRequest = self.HTTPManager.request('GET', 'https://api.foursquare.com/v2/venues/categories?client_id='+self.options['client_id'] + '&client_secret='+self.options['client_secret']+'&v=' + datetime.datetime.now().strftime('%Y%m%d'))

		return categoryRequest.data

	def _traverseCategories(self, categories, currentLevel=0):
		for category in categories:
			if currentLevel < self.options['cat_hierarchy'] and len(category['categories']) > 0:				
				self._traverseCategories(category['categories'], currentLevel+1)
			
			self.categories[category['name']] = category['id']


	def __del__(self):
		if self.outputFileHandle is not None:
			self.outputFileHandle.close()

