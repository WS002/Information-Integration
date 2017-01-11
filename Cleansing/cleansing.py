# Add the main folder to the python library, so that we can import our database singleton
import sys
sys.path.append('../')
import database
import math
import Levenshtein

blacklist = ['a', 'e', 'i', 'o', 'u', ' ', '-', ':', '.', ',', ';', '`', '\'', '"', '<', '>', '(', ')', '+', '=', '&', '#', '$', '^', '*', '@', '%', '!', '?', '/', '|' ]

# Duplicate after certain floating point number, e.g. 1000 => after third comma digit 
floatingPointThreshold = 1000

levenshteinThreshold = 0.9

# Get instance of the database connection
myDB = database.DBConnection()

def _createAndSortKeys(data):
	print "Return keys"

	keyWithCoordinates = []
	for index, row in enumerate(data):
		# row[0] = ID, 1 = name, 2 = lat, 3 = lng, 4 = tourismCategory, 5 = checkinsCount, 6 = description
		if index + 1 < len(data):
			key = ''

			if row[1] is not None and row[1] != '':
				for c in row[1]:
					if c not in blacklist: 
						key += c.upper()

			if row[4] is not None and row[4] != '':
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

def _levenshteinDistance(str1, str2):
	return Levenshtein.distance(str1, str2)

def _compare(data, windowSize):
	if windowSize < 2:
		return 0 

	duplicateCandidates = []

	for index, item in enumerate(data):	
		if index+windowSize < len(data):
			duplicateFound = 0			
			for i, secondItem in enumerate(data[(index+1):(index+windowSize)]):	
				euDistance = -1
				levenshteinDistance = -1
				if item[1][2] is not None and item[1][3] is not None and secondItem[1][2] is not None and secondItem[1][3] is not None:		
					x1 = [item[1][2], item[1][3]]
					x2 = [secondItem[1][2], secondItem[1][3] ]
					euDistance = _euclideanDistance(x1, x2)

				# At least one of the items in the pair must have coordinates
				if ( (item[1][2] is not None and item[1][3] is not None) or (secondItem[1][2] is not None and secondItem[1][3] is not None) ):			
					

					if item[0] is not None and item[0] != '' and secondItem[0] is not None and secondItem[0] != '':					
						levenshteinDistance = _levenshteinDistance(item[0], secondItem[0])
				
					if euDistance > -1 and levenshteinDistance > -1:
						if int(euDistance * floatingPointThreshold) == 0 and levenshteinDistance >= levenshteinThreshold:
							duplicateCandidates.append([item, secondItem])
							del data[index]
							del data[i]
							duplicateFound = 1
					elif euDistance > -1:
						if int(euDistance * floatingPointThreshold) == 0:
							duplicateCandidates.append([item, secondItem])
							del data[index]
							del data[i]
							duplicateFound = 1
					elif levenshteinDistance > -1 and levenshteinDistance >= levenshteinThreshold:
							duplicateCandidates.append([item, secondItem])
							del data[index]
							del data[i]
							duplicateFound = 1
							
			if duplicateFound == 1:
				continue
	return duplicateCandidates




def _merge(duplicates):
	# Merge Strategy
	for item in duplicates:
		firstItem =  item[0][1]
	        secondItem =  item[1][1]

		valueString = ''
		values = []
		keys = ''
		
		# take one of the names
		if firstItem[1] != '' and firstItem[1] is not None:
			valueString += '%s'
			values.append(firstItem[1])
			keys += 'name'
		elif secondItem[1] != '' and secondItem[1] is not None:
			valueString += '%s'
			values.append(firstItem[1])
			keys += 'name'

			

		# take the AVG of lat and lng from the both items
		if firstItem[2] is not None and firstItem[2] != '' and secondItem[2] is not None and secondItem[2] != '':
			lat = (float(firstItem[2]) + float(secondItem[2])) / 2.0
			lng = (float(firstItem[3]) + float(secondItem[3])) / 2.0
			valueString += ',%s, %s'
			values.append(str(lat))
			values.append(str(lng))
			keys += ', lat, lng'	
		elif firstItem[2] is not None and firstItem[2] != '':
			lat = firstItem[2]
			lng = firstItem[3]
			valueString += ',%s, %s'
			values.append(str(lat))
			values.append(str(lng))
			keys += ', lat, lng'
		else:
			lat = secondItem[2]
			lng = secondItem[3]
			valueString += ',%s, %s'
			values.append(str(lat))
			values.append(str(lng))
			keys += ', lat, lng'		


		# take the category that starts with capital letter
		if firstItem[4] is not None and firstItem[4] != '' and firstItem[4][0].isupper():
			valueString += ', %s'
			values.append(firstItem[4])
			keys += ', tourismCategory'
		elif secondItem[4] is not None and secondItem[4] != '':
			valueString += ', %s'
			values.append(secondItem[4])
			keys += ', tourismCategory'

		# take the checkinsCount != None 
		if firstItem[5] != '' and firstItem[5] is not None:
			values.append(str(firstItem[5]))
			valueString += ', %s'
			keys += ', checkinsCount'
		elif secondItem[5] != '' and secondItem[5] is not None:
			values.append(str(secondItem[5]))
			valueString += ', %s'
			keys += ', checkinsCount'
		
		# same for description
		if firstItem[6] != '' and firstItem[6] is not None:
			values.append(firstItem[6])
			valueString += ', %s'
			keys += ', description'
		elif secondItem[6] != '' and secondItem[6] is not None:
			values.append(secondItem[6])
			valueString += ', %s'
			keys += ', description'

		print "Executing ... "
		print "INSERT INTO matched_schema ("+keys+") VALUES ("+', '.join(values)+")" 
		sql="INSERT INTO matched_schema ("+keys+") VALUES ("+valueString+")"
		myDB.executeQuery(sql, values)		

		print "Executing ... " 
		print "DELETE FROM matched_schema WHERE ID = " + str(firstItem[0]) + " OR ID = " + str(secondItem[0]) 
		sql="DELETE FROM matched_schema WHERE ID = " + str(firstItem[0]) + " OR ID = " + str(secondItem[0])
		myDB.executeQuery(sql, [])	


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
