<?php
// Shared PDO connection. Credentials and host come from environment variables
// injected by the Deployment (see k8s/web.yaml). Inside Kubernetes the MySQL
// Service's DNS name is just "mysql".

function db() {
    static $pdo = null;
    if ($pdo === null) {
        $host = getenv('DB_HOST') ?: 'mysql';
        $name = getenv('DB_NAME') ?: 'shop';
        $user = getenv('DB_USER') ?: 'shop';
        $pass = getenv('DB_PASS') ?: 'shoppass';
        $dsn  = "mysql:host=$host;dbname=$name;charset=utf8mb4";
        $pdo = new PDO($dsn, $user, $pass, [
            PDO::ATTR_ERRMODE    => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ]);
    }
    return $pdo;
}
