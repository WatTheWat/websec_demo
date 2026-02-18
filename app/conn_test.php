<?php

// Create connection
$conn = new mysqli("mariadb", "test", "testpassword", "testdb");

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}
//echo "Connected successfully";