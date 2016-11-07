The open street map data has multiple nodes with different categories. We are concerned with key = "tourism" and value one of the following:
1. aquarium
2. attraction
3. gallery
4. museum
5. theme_park
6. zoo
7. view_point

The following values and more are described in detail here: http://wiki.openstreetmap.org/wiki/Key:tourism



<!--Then for each POI name, get its corresponding article through the Wiki API:-->

<!--https://de.wikipedia.org/w/api.php?action=opensearch&search=[articleName]&limit=1&format=xml-->

<!--This API call searches the wiki articles and retrieves the first closest match to the article name field. Could return also multiple articles if parameter limit > 1. The format is xml, but could be returned as an html page aswell-->
