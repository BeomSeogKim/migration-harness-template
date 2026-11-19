-- Generic reconciliation templates. Replace the placeholder names and run them
-- against a copy of the data, never against production from an agent session.

-- 1. Row counts, source vs target. The difference should be explained, not just small.
SELECT
  (SELECT COUNT(*) FROM source_orders)                         AS source_rows,
  (SELECT COUNT(*) FROM target_orders)                         AS target_rows,
  (SELECT COUNT(*) FROM source_orders)
    - (SELECT COUNT(*) FROM target_orders)                     AS missing;

-- 2. Orphaned foreign keys in the target.
SELECT o.id, o.customer_id
FROM target_orders o
LEFT JOIN target_customers c ON c.id = o.customer_id
WHERE c.id IS NULL;

-- 3. NOT NULL columns that arrived empty.
SELECT COUNT(*) AS empty_amounts
FROM target_orders
WHERE amount IS NULL;

-- 4. Amount totals, source vs target, by a stable grouping.
SELECT s.month, s.total AS source_total, t.total AS target_total,
       s.total - COALESCE(t.total, 0) AS difference
FROM (SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, SUM(amount) AS total
      FROM source_orders GROUP BY 1) s
LEFT JOIN (SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, SUM(amount) AS total
           FROM target_orders GROUP BY 1) t USING (month)
WHERE s.total <> COALESCE(t.total, 0);

-- 5. Against a source outside the code (a ledger or export loaded as `ledger`).
--    Rows where the migrated value differs from the recorded real value.
SELECT t.id, t.amount AS migrated, l.amount AS recorded
FROM target_orders t
JOIN ledger l ON l.order_ref = t.source_id
WHERE t.amount <> l.amount;
