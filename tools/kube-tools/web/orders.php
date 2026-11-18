<?php
require_once __DIR__ . '/db.php';
$pdo = db();

$id = (int)($_GET['id'] ?? 0);

$stmt = $pdo->prepare('SELECT id, name, email FROM customers WHERE id = :id');
$stmt->execute(['id' => $id]);
$customer = $stmt->fetch();

if (!$customer) {
    http_response_code(404);
    echo 'No such customer.';
    exit;
}

$stmt = $pdo->prepare(
    'SELECT id, order_date, total
       FROM orders
      WHERE customer_id = :id
      ORDER BY order_date'
);
$stmt->execute(['id' => $id]);
$orders = $stmt->fetchAll();

$sum = 0.0;
foreach ($orders as $o) { $sum += (float)$o['total']; }
?>
<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8">
  <title>Orders — <?= htmlspecialchars($customer['name']) ?></title>
  <style>
    body  { font-family: sans-serif; max-width: 720px; margin: 40px auto; color: #222; }
    h1    { border-bottom: 2px solid #06c; padding-bottom: 4px; }
    table { border-collapse: collapse; width: 100%; }
    th, td{ border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
    th    { background: #eef; }
    td.num, th.num { text-align: right; }
    tfoot td      { font-weight: bold; background: #fafafa; }
    a     { color: #06c; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
<p><a href="index.php">&larr; Back to customers</a></p>
<h1>Orders for <?= htmlspecialchars($customer['name']) ?> (detail)</h1>
<p>Email: <?= htmlspecialchars($customer['email']) ?></p>

<?php if (!$orders): ?>
  <p><em>No orders yet.</em></p>
<?php else: ?>
  <table>
    <thead>
      <tr><th>Order ID</th><th>Date</th><th class="num">Total</th></tr>
    </thead>
    <tbody>
    <?php foreach ($orders as $o): ?>
      <tr>
        <td><?= (int)$o['id'] ?></td>
        <td><?= htmlspecialchars($o['order_date']) ?></td>
        <td class="num"><?= number_format((float)$o['total'], 2, ',', ' ') ?> Kc</td>
      </tr>
    <?php endforeach; ?>
    </tbody>
    <tfoot>
      <tr>
        <td colspan="2">Sum</td>
        <td class="num"><?= number_format($sum, 2, ',', ' ') ?> Kc</td>
      </tr>
    </tfoot>
  </table>
<?php endif; ?>
</body>
</html>
