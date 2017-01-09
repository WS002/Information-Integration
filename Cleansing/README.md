************************************************CLEANSING************************************************


			    	       Duplicate Detection solution:

1. Perform Sorted Neigborhood Algorithm on the matched_schema. Key for each row is defined as all consonants, taken from the name and category fields.
2. The result is then being sorted alphabetically.
3. A defined window moves through the sorted list to find duplicates.
4. 
	4.1 Calculate the euclidean distance between the coordinates of each pair inside the moving window and define a certain threshold. If the distance is less than the threshold, mark the pair for duplicate candidate. ( In our case, the threshold are the 0's after the floating point. E.g. for 0.000**** works quite fine )
	4.2 Calculate the levenshtein distance between the keys string. If the distance is bigger than the defined threshold, mark the pair for duplicate candidate.
	4.3 Take both thresholds ONLY if the pair fields exist. For merging reasons, take only these pairs, in which at least one item has coordinates! 


5. Merge the duplicates according to these rules:
	5.1. Calculate the AVG between the latitude and longitude of the pairs ( or take either of the coordinates, if one of items in the pair does not contain coordinates )
	5.2  Take a certain field only if it is existent in at least one of the items in the pairs
	5.3  The category, starting with a capital letter is preferred


This should work for the wiki articles as well, each of which will try to get merged with an item with coordinates, based only on the levenshtein distance of the key, without euclidean distance ( no coordinates )

6. Rerun the script until all data converges, that is, until nothing changes.



