# Orchestrate the whole foursquare monitoring system process from here
import json
import sys
# Add the main folder to the python library, so that we can import our database  
sys.path.append('../../')
import database


############################################ Foursquare monitoring ##############################################
import foursquareAPI

foursquareAPI = foursquareAPI.FoursquareAPI("foursquareStats.json")

myDB = database.DBConnection()

possibleTourismValues = foursquareAPI.options['tourism'].split(',')

for tourismCat in possibleTourismValues:
	if tourismCat in foursquareAPI.categories:
		categoryID = foursquareAPI.categories[tourismCat]
		while True:
			response = foursquareAPI.getVenuesPerCategory(categoryID)
			try:
				if response != 0:
					currentVenues = json.loads(response)['response']['venues']
					for venue in currentVenues:
						# Get description of venue
						venueResponse = foursquareAPI.getVenue(venue['id'])
						if venueResponse != 0:
							venueDetails = json.loads(venueResponse)['response']['venue']						
							if 'description' in venueDetails:								
								myDB.executeQuery("INSERT INTO foursquare_venues (name, description, lat, lng, category, checkinsCount) VALUES (%s, %s, %s, %s, %s, %s)", (venue['name'], venueDetails['description'], venue['location']['lat'], venue['location']['lng'], tourismCat, venue['stats']['checkinsCount']) )	
							else:
								myDB.executeQuery("INSERT INTO foursquare_venues (name, lat, lng, category, checkinsCount) VALUES (%s, %s, %s, %s, %s)", (venue['name'], venue['location']['lat'], venue['location']['lng'], tourismCat, venue['stats']['checkinsCount']) )			
						else:
							continue
					break
			except Exception:
				print "Error retrieving venues list... Retrying..."
				continue






