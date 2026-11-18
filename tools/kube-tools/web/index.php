<?php
require_once __DIR__ . '/db.php';
$pdo = db();
$customers = $pdo->query(
    'SELECT id, name, email FROM customers ORDER BY name'
)->fetchAll();
?>
<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8">
  <title>Customers</title>
  <style>
    body  { font-family: sans-serif; max-width: 720px; margin: 40px auto; color: #222; }
    h1    { border-bottom: 2px solid #06c; padding-bottom: 4px; }
    table { border-collapse: collapse; width: 100%; }
    th, td{ border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
    th    { background: #eef; }
    a     { color: #06c; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .note { color: #666; font-size: 90%; margin-top: 24px; }
  </style>
</head>
<body>
<h1>Customers (master)</h1>
<table>
  <thead>
    <tr><th>Name</th><th>Email</th><th>Orders</th></tr>
  </thead>
  <tbody>
  <?php foreach ($customers as $c): ?>
    <tr>
      <td><?= htmlspecialchars($c['name']) ?></td>
      <td><?= htmlspecialchars($c['email']) ?></td>
      <td><a href="orders.php?id=<?= (int)$c['id'] ?>">View orders &rarr;</a></td>
    </tr>
  <?php endforeach; ?>
  </tbody>
</table>
<p class="note">
  MySQL runs in a separate Pod; the web container reads from it via the
  <code>mysql</code> Service. Click a customer for the detail page.
</p>
</body>
</html>
