## Vulnerabilities:

1. Conn_test.php sending connection info in plaintext, displays errors



2. Login.php $query is not sanitized, just sending query as it appears - SQL injection
3. Login.php - password compare is in plaintext
4. Login.php - error is printed in verbose


4. Dashboard.php - part of the XSS, unsanitized username echo


5. register.php password is not hashed - SQL injection gives us platintext
6. register.php username is not sanitzied - XSS scripting part of dashboard

7. index.php - tells us php version, os version, program information, and even services / packages installed. REALLY BAD

## Fixes:
1. conn_test.php - instead of including the data in the packet itself, add it as environment variables and send those. If the attacker gets access to the php files, they also get access to the system.
```
DB_HOST=mariadb
DB_USER=test
DB_PASSWORD=testpassword
DB_NAME=testdb
$conn = new mysqli(getenv(DB_HOST), $username, $password, $dbname);

AND 

Error sppression fix:

error_log("Connection failed: " . $conn->connect_error);
die("Database connection error.");

Now we won't leak databse information on a wrong error
```
2. 


5. 
Hash the password instead
```
$password = $_POST['password'];
$hashedPassword = password_hash($password, PASSWORD_DEFAULT);

and

$stmt->bind_param("sss", $username, $email, $hashedPassword);
```

7. Remove index.php or remove the php information from it

