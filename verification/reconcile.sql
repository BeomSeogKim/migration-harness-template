-- Generic reconciliation templates. Replace every <placeholder> and run them against
-- a copy of the data, never against production from an agent session. Written in
-- plain SQL; where a function differs by database, the comment says so.

-- 1. Row counts, source vs target. The difference should be explained, not just small.
SELECT
  (SELECT COUNT(*) FROM <source_table>)                        AS source_rows,
  (SELECT COUNT(*) FROM <target_table>)                        AS target_rows,
  (SELECT COUNT(*) FROM <source_table>)
    - (SELECT COUNT(*) FROM <target_table>)                    AS missing;

-- 2. Orphaned foreign keys in the target.
SELECT c.id, c.<parent_id>
FROM <target_table> c
LEFT JOIN <target_parent_table> p ON p.id = c.<parent_id>
WHERE c.<parent_id> IS NOT NULL AND p.id IS NULL;

-- 3. Required columns that arrived empty.
SELECT COUNT(*) AS empty_values
FROM <target_table>
WHERE <required_column> IS NULL;

-- 4. Status or enum values the new system does not define.
SELECT t.<status_column>, COUNT(*) AS rows_with_value
FROM <target_table> t
WHERE t.<status_column> NOT IN (<'every', 'value', 'the', 'new', 'code', 'defines'>)
GROUP BY t.<status_column>;

-- 5. Amount totals, source vs target, by a stable grouping such as a month.
--    <period>: MySQL DATE_FORMAT(created_at, '%Y-%m'), PostgreSQL and Oracle
--    TO_CHAR(created_at, 'YYYY-MM'), SQL Server FORMAT(created_at, 'yyyy-MM'),
--    SQLite strftime('%Y-%m', created_at).
SELECT s.period, s.total AS source_total, t.total AS target_total,
       s.total - COALESCE(t.total, 0) AS difference
FROM (SELECT <period> AS period, SUM(<amount_column>) AS total
      FROM <source_table> GROUP BY <period>) s
LEFT JOIN (SELECT <period> AS period, SUM(<amount_column>) AS total
           FROM <target_table> GROUP BY <period>) t ON t.period = s.period
WHERE s.total <> COALESCE(t.total, 0);

-- 6. Against a source outside the code (a ledger or export loaded as <truth_table>).
--    Rows where the migrated value differs from the recorded real value.
SELECT t.id, t.<amount_column> AS migrated, r.<amount_column> AS recorded
FROM <target_table> t
JOIN <truth_table> r ON r.<record_ref> = t.<source_id>
WHERE t.<amount_column> <> r.<amount_column>;
