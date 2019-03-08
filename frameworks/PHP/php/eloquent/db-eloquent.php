<?php

require_once __DIR__ . '/boot-eloquent.php';

// Read number of queries to run from URL parameter
$query_count = 1;
$query_param = isset($_GET['queries']);
if ($query_param && $_GET['queries'] > 0) {
    $query_count = $_GET['queries'] > 500 ? 500 : $_GET['queries'];
}

// Create an array with the response string.
$arr = array();

// For each query, store the result set values in the response array
$query_counter = $query_count;
while (0 < $query_counter--) {
    // Choose a random row
    // http://www.php.net/mt_rand
    $id = mt_rand(1, 10000);

    $world = World::find($id);

    // Store result in array.
    $arr[] = $world->toArray();
}

if ($query_count === 1 && !$query_param) {
    $arr = $arr[0];
}

// Set content type
header("Content-type: application/json");

// Use the PHP standard JSON encoder.
// http://www.php.net/manual/en/function.json-encode.php
echo json_encode($arr);