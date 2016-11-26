Change the category values from the options file, according to the need.

The foursquare venues schema looks like this:


```
+---------------+--------------+------+-----+---------+----------------+
| Field         | Type         | Null | Key | Default | Extra          |
+---------------+--------------+------+-----+---------+----------------+
| ID            | int(11)      | NO   | PRI | NULL    | auto_increment |
| name          | varchar(255) | NO   |     | NULL    |                |
| lat           | decimal(8,6) | NO   |     | NULL    |                |
| lng           | decimal(9,6) | NO   |     | NULL    |                |
| categoryName  | varchar(255) | NO   |     | NULL    |                |
| checkinsCount | int(11)      | NO   |     | NULL    |                |
| description   | text         | YES  |     | NULL    |                |
+---------------+--------------+------+-----+---------+----------------+

```
