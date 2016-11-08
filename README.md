# Information-Integration


Four Subtasks:

1. Extraction - extract relevant data from sources and convert to a common data model
2. Schema matching, standardization, transformation, definition of global schema
3. Cleansing - Duplicate detection, data fusion
4. Visualization - Query definition, execution, mashup...


Each step will have its own folder, containing its scrips and presentation.

******************************** IDEA ******************************************************************************************************

Retrieve all points of interest (cultural/tourist places) around the stuttgart area. For each point of interest(POI) retrieve its corresponding wikipedia article. Optionally, one could retrieve the number of check-ins from a social network for the current POI. The integrated data can be visualized on a map, with each POI at its corresponding coordinates. By clicking on a POI, information from wikipedia should be displayed to theuser. If the check-in number is also involved, the visualization could consist of circles with different radius, proportional to the number of check-ins. 

******************************** EXTRACTION ************************************************************************************************

The POI can be retrieved from OpenStreetMap (http://wiki.openstreetmap.org/wiki/DE:Points_of_interest), which needs to be integrated with the information retrieved from Wikipedia  (https://en.wikipedia.org/wiki/Wikipedia:Database_download) (https://meta.wikimedia.org/wiki/Data_dumps).
For the social network, data from Foursquare/Facebook or Twitter could be used. (optional)

The common data model should be a relational schema, MySQL? (debatable). 

For the data source(OpenStreetMap, Wikipedia):
1. Create database table.
2. Create extractor for loading data into database.

For the OpenStreetMap data, load only the relevant entities into the database.
For the Wikipedia data, load all articles into the database.

Then merge together the two.

The osmExtractor.py file requires the following python module in order to run:

Install dateutil module with pip:
 	sudo apt-get install python-pip
 	sudo pip install python-dateutil


Schema for the OSM data:

1. CREATE TABLE osm_nodes (ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,  lat DECIMAL(8,6) NOT NULL, lon DECIMAL (9,6) NOT NULL, timestamp TIMESTAMP NULL DEFAULT NULL );

2. CREATE TABLE osm_tags (ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT, node_id INT NOT NULL, k VARCHAR(255) NOT NULL, v VARCHAR(255) NOT NULL, FOREIGN KEY (node_id) REFERENCES osm_nodes(ID));

Schema for the Wiki data:

1. CREATE TABLE wiki_articles ( ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT, title VARCHAR(255) NOT NULL CHARACTER SET utf8 COLLATE utf8_general_ci, content mediumtext NOT NULL CHARACTER SET utf8 COLLATE utf8_general_ci);

*********************************** DATABASE ************************************************************************************************

Requirements: Install the MySQL Python connector driver for your current system. For more info: https://dev.mysql.com/downloads/connector/python/

The database class is a singleton class. It is located in the script database.py in the main folder of the project. Before using this class,
one needs to fill out the dbConfig.cfg file, located in the same folder. 

NOTE: DO NOT COMMIT THE CONFIGURATION FILE. That way, each contributor can have his own database parameters and credentials.


*********************************************************************************************************************************************
