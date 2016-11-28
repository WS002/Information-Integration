
Before proceeding, please install the Levenshtein module for python with "pip install python-levenshtein"


The source schemas look like this: 

```
			foursquare_venues
+---------------+--------------+------+-----+---------+----------------+
| Field         | Type         | Null | Key | Default | Extra          |
+---------------+--------------+------+-----+---------+----------------+
| ID            | int(11)      | NO   | PRI | NULL    | auto_increment |
| name          | varchar(255) | NO   |     | NULL    |                |
| lat           | decimal(8,6) | NO   |     | NULL    |                |
| lng           | decimal(9,6) | NO   |     | NULL    |                |
| category      | varchar(255) | NO   |     | NULL    |                |
| checkinsCount | int(11)      | NO   |     | NULL    |                |
| description   | text         | YES  |     | NULL    |                |
+---------------+--------------+------+-----+---------+----------------+

CREATE TABLE foursquare_venues (ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255) NOT NULL, lat DECIMAL(8,6) NOT NULL, lng DECIMAL(9,6) NOT NULL, category VARCHAR(255), checkinsCount INT NOT NULL, description TEXT)

			osm_nodes
+-------+--------------+------+-----+---------+----------------+
| Field | Type         | Null | Key | Default | Extra          |
+-------+--------------+------+-----+---------+----------------+
| ID    | int(11)      | NO   | PRI | NULL    | auto_increment |
| lat   | decimal(8,6) | NO   |     | NULL    |                |
| lon   | decimal(9,6) | NO   |     | NULL    |                |
+-------+--------------+------+-----+---------+----------------+

CREATE TABLE osm_nodes (ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,  lat DECIMAL(8,6) NOT NULL, lon DECIMAL (9,6) NOT NULL);


			osm_tags

+---------+--------------+------+-----+---------+----------------+
| Field   | Type         | Null | Key | Default | Extra          |
+---------+--------------+------+-----+---------+----------------+
| ID      | int(11)      | NO   | PRI | NULL    | auto_increment |
| node_id | int(11)      | NO   | MUL | NULL    |                |
| k       | varchar(255) | NO   |     | NULL    |                |
| v       | varchar(255) | NO   |     | NULL    |                |
+---------+--------------+------+-----+---------+----------------+

CREATE TABLE osm_tags (ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT, node_id INT NOT NULL, k VARCHAR(255) NOT NULL, v VARCHAR(255) NOT NULL, FOREIGN KEY (node_id) REFERENCES osm_nodes(ID));

			wiki_articles

+---------+--------------+------+-----+---------+----------------+
| Field   | Type         | Null | Key | Default | Extra          |
+---------+--------------+------+-----+---------+----------------+
| ID      | int(11)      | NO   | PRI | NULL    | auto_increment |
| title   | varchar(255) | NO   |     | NULL    |                |
| content | mediumtext   | NO   |     | NULL    |                |
+---------+--------------+------+-----+---------+----------------+

CREATE TABLE wiki_articles ( ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT, title VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, content MEDIUMTEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL);
```
NOTE: The osm_nodes table has a removed column "timestamp". 


The matched schema should look like this: 

```
			matched_schema
+-----------------+--------------+------+-----+---------+----------------+
| Field           | Type         | Null | Key | Default | Extra          |
+-----------------+--------------+------+-----+---------+----------------+
| ID              | int(11)      | NO   | PRI | NULL    | auto_increment |
| name            | varchar(255) | NO   |     | NULL    |                |
| lat             | decimal(8,6) | YES  |     | NULL    |                |
| lng             | decimal(9,6) | YES  |     | NULL    |                |
| tourismCategory | varchar(255) | YES  |     | NULL    |                |
| checkinsCount   | int(11)      | YES  |     | NULL    |                |
| description     | mediumtext   | YES  |     | NULL    |                |
+-----------------+--------------+------+-----+---------+----------------+

CREATE TABLE matched_schema (ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255) NOT NULL, lat DECIMAL(8,6), lng DECIMAL(9,6), tourismCategory VARCHAR(255), checkinsCount INT, description MEDIUMTEXT)
```


I have populated the wiki_articles tables with values, extracted from the Wiki API only for names in foursquare_venues and osm_tags. I had to do it, because the wiki dump was too large, and could not test with its data. The WikiAPI extractor can be found in folder Extraction/Wikipedia.

The foursquare extractor can be found in folder Extraction/Foursquare.

Please, populate the tables, before proceeding to the matching stage. 



###################################### SCHEMA MATCHING #####################################################

There are 2 relevant files in the SchemaMatching folder:
1. schemaMatcher.py
2. schemaTransform.py

The schemaMatcher is a class, that matches source and target schemas, based on 3 different approaches. 
	1. Schema-only based + Element-level + Linguistic: 

		Input: two schemas with respective sets of attribute values, denoted A and B.

					 General procedure:
		1. Form cross products A x B --> set of attribute pairs
		2. For each attribute pair, compare attributes based on their name (= label).
		3. Comparison is done with the Levenshtein's distance algorithm ( distance = number of edits to match 2 strings )
		4. A similarity percentage is computed for each pair of columns ( from source and target )

	2. Schema-only based + Element-level + Constraint-based

		Input: two schemas with respective sets of constraint values, denoted A and B.
					General procedure:

		Same as (1), but with different input (the types of each column). One could also do different comparison algorithm here, but for the sake of simplicity, the same (Levenshtein's algorithm) is used.

	3. Instance/contents-based + Element-level + Linguistic

		Input: sample data ( 1 row ) for each column of the respective source and target schemas ( tables )
	
					General procedure:

		1. Form cross products --> set of sample datas
		2. For each data pair, calculate the different in string length size ( For sake of simplicity only 1 criteria )
		3. A similarity percentage is computed for each pair of data samples ( from source and target )



	The schemaMatch function performs all approaches on the source and data schema and calculates an overall similarity percentage ( multiplication of the 3 ) for each pair of column names ( source -> target ). The function returns only the pairs with the BEST overall similarity percentage. If a threshold value is set, all pairs, with best overall similarity percentage < threshold, are discarded.


The schemaTransform orchestrates the whole process of feeding data into the schemaMatcher and returning pairs of columns. It then proceeds to transform them (no need in our case), normalize them (no need in our case) and load them into the database. 

NOTE: In order to do instance/contents-based comparison, the target schema(table) must have data in it. So, I have chosen the foursquare_venues table to be the closest match to the matched_schema table and performed only a linguistic- and constraints-based(1 and 2) schema match on these 2 tables. The algorithm then proceeds to insert data to the matched_schema. This data is then used to perform a schema matching with all 3 approaches on the other tables.

NOTE: Some of the code in the schemaTransform is written poorly and manually for the osm_nodes and osm_tags tables. This is due to the fact, that these tables have a very specific structure, which would take a lot of time to standardize into functions. The code for the other 2 tables ( wiki_articles and foursquare_venues ) is standardized.  



Run the script "schemaTransform.py" with no arguments after the tables are properly created and populated.
It would then proceed to match the schemas and log information to the standard output.

#############################################################################################################



