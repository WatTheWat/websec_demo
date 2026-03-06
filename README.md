# COMP - CCDC Web Security Talk

I've dockerized the original proxmox version so it can be easily run locally by anyone interested. 

To run:
1. Clone this git repository `git clone https://github.com/WatTheWat/websec_demo.git`
2. Move into the repository directory `cd websec`
3. Start up the docker container `docker compose up -d`
4. Now, you have the website available on your localhost. I'd recommend opening a browser and navigating to `localhost/login.php`


Give yourself some time to look through the website and identify any possible weakpoints.

To look through the configuration files, and the actual filesystem:
1. List the currently running docker containers`docker ps`
2. Now, we want to execute commands in the docker container like it's our proxmox virtual machine. To do so, run `docker exec -it <pid of container> bash`
3. You're in the container! Some good places to look may be `/var/html/www` for the php files that make up the website, or `/etc/apache2/apache.conf` for apache configuration files

## Vulnerabilities:

### Conn_test.php 
1. Sending connection info in plaintext, displays errors


### Login.php
1. $query is not sanitized, just sending query as it appears - SQL injection
2. Login.php - password compare is in plaintext
3. Login.php - error is printed in verbose

### Dashboard.php
1. Part of the XSS, unsanitized username echo


### Register.php
1. Password is not hashed - SQL injection gives us platintext
2. Register.php username is not sanitzied - XSS scripting part of dashboard

### Index.php
1. Tells us php version, os version, program information, and even services / packages installed

## Fixes:
### conn_test.php 
Instead of including the data in the packet itself, add it as environment variables and send those. If the attacker gets access to the php files, they also get access to the system.
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
### dashboard.php 
Stop echoing the exact same, instead wrap it (good advice)
```
<h2>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?></h2>

```

### login.php

```
<?php
session_start();
include './conn_test.php';

$message = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = $_POST['email'];
    $password = $_POST['password'];

    // FIX 1: prepared statement stops SQL injection
    $stmt = $conn->prepare("SELECT * FROM userdata WHERE email = ?");
    $stmt->bind_param("s", $email);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result && $result->num_rows > 0) {
        $row = $result->fetch_assoc();
        // FIX 2: password_verify stops plaintext compare
        if (password_verify($password, $row['password'])) {
            $_SESSION['email'] = $row['email'];
            $_SESSION['username'] = $row['username'];
            header("Location: dashboard.php");
            exit();
        } else {
            // FIX 3: generic message stops user enumeration
            $message = "Invalid email or password";
        }
    } else {
        $message = "Invalid email or password";
    }
}
?>
```

### register.php
Hash the password instead
```
$password = $_POST['password'];
$hashedPassword = password_hash($password, PASSWORD_DEFAULT);

and

$stmt->bind_param("sss", $username, $email, $hashedPassword);

$stmt = $conn->prepare("SELECT email, username, password FROM userdata WHERE email = ?");
$stmt->bind_param("s", $email);
$stmt->execute();
$stmt->store_result();
$stmt->bind_result($db_email, $db_username, $db_password);
$stmt->fetch();

below the if statement


```

### index.php
Remove index.php or remove the php information from it

