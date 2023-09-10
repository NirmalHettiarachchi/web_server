<?php
// Get the first command line argument. This is the JSON string passed from our server.py file.
$payload = $argv[1];

// Decode the JSON string into a JSON object.
$json_object = json_decode($payload);

// Setting the variables and methods.
$method = $json_object->method;
$path = $json_object->path;
$parameters = (array)$json_object->parameters;

// Setting GET and POST variables based on the method.
if ($method == "GET") {
    $_GET = $parameters;
} else if ($method == "POST") {
    $_POST = $parameters;
}

// Include the resource_path at the end of the wrapper.
// Now the resource_file has access to all the variables that we set in the wrapper.
include $path;
?>
