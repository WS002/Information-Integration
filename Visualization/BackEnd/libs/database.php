<?php
ini_set('memory_limit', '-1');

class Database {

   private $userName;
   private $password;
   private $host;
   private $dbconn;

   function __construct()
   {
	$ini_array = parse_ini_file("databaseOptions.ini", true);
	$this->userName = $ini_array['Database']['user'];
	$this->password = $ini_array['Database']['pwd'];
	$this->host = $ini_array['Database']['host'];
	$this->db = $ini_array['Database']['db'];
   }

   function initConnection()
   {
	$conn = mysqli_connect($this->host, $this->userName, $this->password, $this->db);
	
	$this->dbconn = $conn;
	return $this->dbconn;
   }

   function getData($sql) {
	$result = $this->dbconn->query($sql);

	return $result;	
   }

   function __destruct() {
       mysqli_close($this->dbconn);
   }

} 


?>
