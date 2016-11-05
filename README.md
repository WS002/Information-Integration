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

For each data source:
1. Create database table.
2. Create extractor for loading data into database.
********************************************************************************************************************************************
