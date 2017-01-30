 <?php 

require_once('libs/controller.php');

if(!$_GET['func'])
{
	echo 'Missing "func" parameter!';
	exit();
}

$params = array();
foreach($_GET as $key=>$value)
{
	if($key !='func')
		$params[$key] = $value;
}

$func = $_GET['func'];

$controller = new Controller($params);

if(method_exists($controller, $func)) {	
	$controller->$func($params);
}else {
	echo 'No such function "' . $func . '" exists! ';
	exit(); 
}

 ?> 

