<?php
session_start();
include './conn_test.php';

$message = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = $_POST['email'];
    $password = $_POST['password'];

    // Perepare and execute
    $query = "SELECT * FROM userdata WHERE email = '$email' AND password = '$password'";
    $result = mysqli_query($conn, $query);

    if ($result && mysqli_num_rows($result) > 0) {
        $row = mysqli_fetch_assoc($result);
        $_SESSION['email'] = $row['email'];
        $_SESSION['username'] = $row['username'];
        header("Location: dashboard.php");
        exit();
    } else {
        // Error logging
        $check = mysqli_query($conn, "SELECT * FROM userdata WHERE email = '$email'");
        $message = mysqli_num_rows($check) > 0 ? "Incorrect password" : "Email not found";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
</head>
<body class="bg-light">
    <div class="container p-5 d-flex flex-column align-items-center">
        <?php if ($message): ?>
            <div class="alert alert-danger"><?php echo $message; ?></div>
        <?php endif; ?>
        <form method="post" class="form-control mt-5 p-4" style="width:380px;">
            <h5 class="text-center mb-4">Login</h5>
            <div class="mb-2">
                <label>Email</label>
                <input type="text" name="email" class="form-control" required>
            </div>
            <div class="mb-2">
                <label>Password</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-success mt-3">Login</button>
            <p class="text-center mt-3"><a href="./register.php">Create Account</a> | <a href="./resetpassword.php">Forgot Password</a></p>
        </form>
    </div>
</body>
</html>