<?php

// connect to mongodb

require_once('libs/database.php');

class Controller {

	private $params;
	private $aggregatedData;
	private $db;

	function __construct($params)
   	{
		
		$db = New Database();
		$db->initConnection();
		$this->db = $db;
		$this->params = $params;
	}

	function getVenues() {
		$query = "SELECT * from matched_schema where checkinsCount > 0";		
		$res = $this->db->getData($query);

		$venues = [];
		if ($res->num_rows > 0) {
		    // output data of each row
		    	while($row = $res->fetch_assoc()) {
				$venue = array();
				$venue['id'] = $row['ID'];
				$venue['name'] = utf8_encode($row['name']);
				$venue['category'] = $row['tourismCategory'];
				$venue['hereNow'] = array('count' => $row['checkinsCount']);
				$venue['description'] = utf8_encode($row['description']);
				$venue['location'] = array('lat'=>$row['lat'], 'lng'=>$row['lng']);
				$venues[] = $venue;				
			}

		}

		header('Content-Type: application/json');
		echo json_encode($venues);	
	}

	

} // End of class


?>
