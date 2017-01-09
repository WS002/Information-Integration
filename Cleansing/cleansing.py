# Add the main folder to the python library, so that we can import our database singleton
import sys
sys.path.append('../')
import database
import math

blacklist = ['a', 'e', 'i', 'o', 'u', ' ', '-', ':', '.', ',', ';', '`', '\'', '"', '<', '>', '(', ')', '+', '=', '&', '#', '$', '^', '*', '@', '%', '!', '?', '/', '|' ]

# Duplicate after certain floating point number, e.g. 1000 => after third comma digit 
floatingPointThreshold = 1000

# Get instance of the database connection
myDB = database.DBConnection()

def _createAndSortKeys(data):
	print "Return keys"

	keyWithCoordinates = []
	for index, row in enumerate(data):
		# row[0] = ID, 1 = name, 2 = lat, 3 = lng, 4 = tourismCategory, 5 = checkinsCount, 6 = description
		if index + 1 < len(data) and row[2] != '' and row[2] is not None and row[3] != '' and row[3] is not None:
			key = ''
			for c in row[1]:
				if c not in blacklist: 
					key += c.upper()
			for c in row[4]:
				if c not in blacklist:
					key += c.upper()

			keyWithCoordinates.append([key, row])			

	# Sort first based on euclidean distance
	euSortedKeys = sorted(keyWithCoordinates, key=lambda pair: pair[0])
	return euSortedKeys

def _euclideanDistance(x1, x2):
	latDistance = float(x1[0]) - float(x2[0])
	lngDistance = float(x1[1]) - float(x2[1])
	return math.sqrt(latDistance * latDistance + lngDistance * lngDistance)

def _compare(data, windowSize):
	if windowSize < 2:
		return 0 

	duplicateCandidates = []

	for index, item in enumerate(data):	
		if index+windowSize < len(data):			
			for secondItem in data[(index+1):(index+windowSize)]:				
				x1 = [item[1][2], item[1][3]]
				x2 = [secondItem[1][2], secondItem[1][3] ]
				euDistance = _euclideanDistance(x1, x2)
				if int(euDistance * 1000) == 0:
					duplicateCandidates.append([item, secondItem])

				
	return duplicateCandidates


def _merge(duplicates):
	# Merge Strategy
	for item in duplicates:
		firstItem =  item[0][1]
	        secondItem =  item[1][1]

		values = ''
		keys = ''

		# take one of the names
		if firstItem[1] != '' and firstItem[1] is not None:
			values += '"' + firstItem[1] + '"'
			keys += 'name'
			print values
		elif secondItem[1] != '' and secondItem[1] is not None:
			values += '"' + secondItem[1] + '"'
			keys += 'name'

			

		# take the AVG of lat and lng from the both items
		if firstItem[2] is not None and firstItem[2] != '' and secondItem[2] is not None and secondItem[2] != '':
			lat = (float(firstItem[2]) + float(secondItem[2])) / 2.0
			lng = (float(firstItem[3]) + float(secondItem[3])) / 2.0
			values += ', "' + str(lat) + '", "' + str(lng) + '"'
			keys += ', lat, lng'			


		# take the category that starts with capital letter
		if firstItem[4] is not None and firstItem[4] != '' and firstItem[4][0].isupper():
			values += ', "' + firstItem[4] + '"'
			keys += ', tourismCategory'
		elif secondItem[4] is not None and secondItem[4] != '':
			values += ', "' + secondItem[4] + '"'
			keys += ', tourismCategory'

		# take the checkinsCount != None 
		if firstItem[5] != '' and firstItem[5] is not None:
			values += ', "' + str(firstItem[5]) + '"'
			keys += ', checkinsCount'
		elif secondItem[5] != '' and secondItem[5] is not None:
			values += ', "' + str(secondItem[5]) + '"'
			keys += ', checkinsCount'
		
		# same for description
		if firstItem[6] != '' and firstItem[6] is not None:
			values += ', "' + firstItem[6] + '"'
			keys += ', description'
		elif secondItem[6] != '' and secondItem[6] is not None:
			values += ', "' + secondItem[6] + '"'
			keys += ', description'

		print "Executing ... " 
		print "DELETE FROM matched_schema WHERE ID = " + str(firstItem[0]) + " OR ID = " + str(secondItem[0]) 
		sql="DELETE FROM matched_schema WHERE ID = " + str(firstItem[0]) + " OR ID = " + str(secondItem[0])
		cursor = myDB.conn.cursor()
		cursor.execute(sql)
		myDB.conn.commit()

		print "Executing ... "
		print "INSERT INTO matched_schema ("+keys+") VALUES ("+values+")" 
		sql="INSERT INTO matched_schema ("+keys+") VALUES ("+values+")"
		cursor = myDB.conn.cursor()
		cursor.execute(sql)
		myDB.conn.commit()

def sortedNeighbourhood(data):
	# Duplicate detection in 3 steps:
	# 1. Create key
	# 2. Sort
	# 3. Merge
	keys = _createAndSortKeys(data)
 	duplicates = _compare(keys, 2)	
	_merge(duplicates)


if __name__ == "__main__":


	sql="SELECT * FROM matched_schema"
	cursor = myDB.conn.cursor(buffered=True)
	cursor.execute(sql)

	data = []
	for c in cursor:
		data.append(c)

	sortedNeighbourhood(data)
