# Need to install the MySQL Python connector driver for your current system
# For more info: https://dev.mysql.com/downloads/connector/python/
# Please, fill out the dbConfig.cfg file before using this script


import mysql.connector
import ConfigParser
import os


# Need a singleton class to return only ONE connection instance of our DB
def singleton(cls):
	instances = {}
	def getinstance():
		if cls not in instances:
    			instances[cls] = cls()
        	return instances[cls]
    	return getinstance

@singleton
class DBConnection:
	def __init__(self):
		######### Parse config file #########
		Config = ConfigParser.ConfigParser()
		path = os.path.dirname(os.path.realpath(__file__))
		Config.read(path + "/dbConfig.cfg")

		databaseOptions = {}
		for option in Config.options("Database"):
			databaseOptions[option] = Config.get("Database", option)

		############ End parsing ############	
		self.conn = mysql.connector.connect(**databaseOptions)
		self.cursor = self.conn.cursor()	
	
	# If argument list consists of only ONE element, one needs to append a ',' at the end, so that it is recognized as a tuple
	# So e.g. ... argumentList = (1,) 	
	def executeQuery(self, query, argumentList):		
		self.cursor.execute(query, argumentList)
		# If the query is a select statement use the cursor should contain a list of all result values. Try cursor.fetchAll().
		self.conn.commit()
		return self.cursor

	def __del__(self):
		self.conn.close()








