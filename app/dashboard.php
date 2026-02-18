<?php
session_start();
if (!isset($_SESSION['email'])) {
    header("Location: login.php");
    exit();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-sm bg-success">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="#">Dashboard</a>
            <a href="./logout.php" class="btn btn-light fw-bold text-success">Logout</a>
        </div>
    </nav>
    <div class="p-4 mt-5">
        <h2>Welcome, <?php echo $_SESSION['username']; ?></h2>
        <img src="./cutecat.jpeg" alt="Cutecat">
    </div>
</body>
</html>