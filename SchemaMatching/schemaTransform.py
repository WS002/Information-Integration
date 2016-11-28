import sys
import mysql.connector
from mysql.connector import FieldType

# Get the automatic schema matcher 
import schemaMatcher

# Add the main folder to the python library, so that we can import our database singleton
sys.path.append('../')
import database


def getDatabaseSchema(cursor):
	dbSchema = {'elements' : [], 'constraints': []}

	for i in range(len(cursor.description)):
		#print("Column {}:".format(i+1))
		desc = cursor.description[i]
		if desc[0] != 'ID':
			dbSchema['elements'].append(desc[0])
			#print("  column_name = {}".format(desc[0]))
			dbSchema['constraints'].append(FieldType.get_info(desc[1]))
			#print("  type = {} ({})".format(desc[1], FieldType.get_info(desc[1])))

	return dbSchema


def getDatabaseSampleData(cursor):
	sampleData = []
	
	for row in cursor[0]:
		sampleData.append(row)

	return sampleData

def loadData(matchedElements, sourceTable, targetTable, myDB):
	sourceElements = []
	targetElements = []

	for elTuple in matchedElements:
		sourceElements.append(elTuple[0])
		targetElements.append(elTuple[1])		
		
	print "INSERT INTO "+targetTable+" ("+','.join(targetElements)+") (SELECT "+','.join(sourceElements)+" FROM "+sourceTable+" )"
	myDB.cursor.execute("INSERT INTO "+targetTable+" ("+','.join(targetElements)+")  (SELECT "+','.join(sourceElements)+" FROM "+sourceTable+" )")

	myDB.conn.commit()



def getSampleData(cursor):
	data = []

	for row in cursor:
		index = 0
		for value in row:
			# Ignore the ID
			if index > 0:
				data.append(value)
			index += 1
		break

	return data


if __name__ == "__main__":
	
	# Get instance of the database connection
	myDB = database.DBConnection()

	targetTable = "matched_schema"

	sql="SELECT * FROM "+targetTable+" LIMIT 1"
	cursor = myDB.conn.cursor(buffered=True)
	cursor.execute(sql)

	targetSchema = getDatabaseSchema(cursor)

	########## Schema match(based only on constraint and element) foursquare_venues and LOAD the data into the matched schema #########
	sourceTable = "foursquare_venues"
	sql="SELECT * FROM "+sourceTable+" LIMIT 1"
	cursor = myDB.conn.cursor(buffered=True)
	cursor.execute(sql)

	sourceSchema = getDatabaseSchema(cursor)
	
	# Get schema matcher instance
	schemaMatcher = schemaMatcher.Matcher(sourceSchema, targetSchema)
	# Match elements

	print " "
	print "Best matching elements for source table [" + sourceTable + "] and target table [" + targetTable + "]"
	print " "
	matchedElements = schemaMatcher.matchSchemasByElementAndConstraintLinguistic()
	
	# Insert to DB
	loadData(matchedElements, sourceTable, targetTable, myDB)
	###################################################################################################################################

	########## Get target sample data ########
	sql="SELECT * FROM "+targetTable+" LIMIT 1"
	cursor = myDB.conn.cursor(buffered=True)
	cursor.execute(sql)
	schemaMatcher.target['data'] = getSampleData(cursor)
	################################################################################################################################


	########## Schema match wiki_articles and LOAD the data into the matched schema ###########################################
	sourceTable = "wiki_articles"
	sql="SELECT * FROM "+sourceTable+" LIMIT 1"
	cursor = myDB.conn.cursor(buffered=True)
	cursor.execute(sql)

	sourceSchema = getDatabaseSchema(cursor)

	schemaMatcher.source['elements'] = sourceSchema['elements']
	schemaMatcher.source['constraints'] = sourceSchema['constraints']
	schemaMatcher.source['data'] = getSampleData(cursor)

	print " "
	print "Best matching elements for source table [" + sourceTable + "] and target table [" + targetTable + "]"
	print " "
	matchedElements = schemaMatcher.matchSchemas()
	loadData(matchedElements, sourceTable, targetTable, myDB)

	########## Schema match osm_nodes and osm_tags and LOAD the data into the matched schema ################################
	## The schema and data for these tables is not standard, so cant use the functions defined above. Just do it manually. ##

	sourceTable = "osm_nodes"
	secondarySourceTable = "osm_tags"	

	sql="SELECT * FROM "+sourceTable+" LIMIT 1"
	cursor = myDB.conn.cursor()
	cursor.execute(sql)

	sampleData = []
	#extract nodeID
	nodeID = 0
	for row in cursor:
		index = 0
		for value in row:
			if index == 0:
				nodeID = value		
			else:
				sampleData.append(value)
			index += 1

	sourceSchema = getDatabaseSchema(cursor)
	sourceSchema['data'] = sampleData

	
	sql="SELECT * FROM "+secondarySourceTable + " WHERE node_id=" + str(nodeID)
	cursor = myDB.conn.cursor()
	cursor.execute(sql)

	secondarySchema = getDatabaseSchema(cursor)
	for row in cursor:
		# k = row[2]
		# v = row[3]
		sourceSchema['data'].append(row[3])
		sourceSchema['elements'].append(row[2])
		sourceSchema['constraints'].append(secondarySchema['constraints'][2])
		
	schemaMatcher.source['elements'] = sourceSchema['elements']
	schemaMatcher.source['constraints'] = sourceSchema['constraints']
	schemaMatcher.source['data'] = sourceSchema['data']

	print " "
	print "Best matching elements for source table [" + sourceTable + "] [" + secondarySourceTable + "] and target table " + targetTable + "]"
	print " "
	
	
	# Define a threshold to match the values with similarity percentage greater than this threshold
	threshold = 0.1

	matchedElements = schemaMatcher.matchSchemas(threshold)

	###### Load data from osm_nodes and osm_tags to the matched_schema ##########
	sourceElements = []
	targetElements = []
        for elTuple in matchedElements:
		sourceElements.append(elTuple[0])
		targetElements.append(elTuple[1])

	sql="SELECT * FROM "+sourceTable
	cursor = myDB.conn.cursor()
	cursor.execute(sql)

	valuesToInsert = {}
	
	for row in cursor:	 	
		nodeID = str(row[0])
		valuesToInsert[nodeID] = []
		
		for value in row[1:]:		
			if not isinstance(value, basestring):
				value = str(value)
			else:
				value.encode('utf-8')

			valuesToInsert[nodeID].append(value)
	
		
	# Get tags for each node
	sql="SELECT * FROM "+secondarySourceTable + " WHERE node_id in (" + ','.join(valuesToInsert.keys()) + ")"
	secondaryCursor = myDB.conn.cursor()
	secondaryCursor.execute(sql)
	


	for tRow in secondaryCursor:
		nodeID = str(tRow[1])
		k = tRow[2]
		v = tRow[3]
		if k in sourceElements:
			if not isinstance(v, basestring):
				v = str(v)
			else:
				v.encode('utf-8')
			
			if v != '' and v is not None:
				valuesToInsert[nodeID].append(v)				


	


	# Finally insert the values found	
	for key in valuesToInsert:
		if len(valuesToInsert[key]) != len(targetElements):
			continue

		values = ''
		for x in range(0, len(valuesToInsert[key])):				
			if x == len(valuesToInsert[key]) - 1:
				values += "'"+valuesToInsert[key][x]+"'" 
			else:
				values += "'"+valuesToInsert[key][x]+"',"

		sql = "INSERT INTO "+targetTable+" ("+','.join(targetElements)+") VALUES("+ values +")"
		myDB.cursor.execute(sql)					
		myDB.conn.commit()
	
	#########################################################################################################################
	secondaryCursor.close()	




