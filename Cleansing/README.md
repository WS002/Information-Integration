************************************************CLEANSING************************************************


			    	       Duplicate Detection solution:

1. Perform Sorted Neigborhood Algorithm on the matched_schema. Key for each row is defined as all consonants, taken from the name and category fields.
2. The result is then being sorted alphabetically.
3. A defined window moves through the sorted list to find duplicates.
4. Calculate the euclidean distance between the coordinates of each pair inside the moving window and define a certain threshold. If the distance is less than the threshold, mark the pair as a duplicate. ( In our case, the threshold are the 0's after the floating point. E.g. for 0.000**** works quite fine )
5. Merge the duplicates according to these rules:
	5.1. Calculate the AVG between the latitude and longitude of the pairs
	5.2  Take a certain field only if it is existent in at least one of the items in the pairs
	5.3  The category, starting with a capital letter is preferred



P.S. The code is adjusted to work only for rows with defined coordinates. The wiki articles can be adjusted accordingly by performing the same algorithm only with name and/or description or using a totally different algorithm. You decide :)
