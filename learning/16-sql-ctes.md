# Module 16: SQL Common Table Expressions (CTEs) & Query Modularity

## 1. What It Is
A **Common Table Expression (CTE)** is a temporary, named result set defined within the execution scope of a single `SELECT`, `INSERT`, `UPDATE`, or `DELETE` statement. Introduced via the `WITH` keyword, a CTE functions like an inline, disposable view that exists only during query execution.

## 2. Why It Exists
Before CTEs, complex multi-step data transformations required deeply nested, unreadable subqueries (derived tables):
```sql
-- UNREADABLE NESTED SUBQUERY (SPAGHETTI SQL):
SELECT sub1.title, sub2.avg_time
FROM (SELECT id, title, created_by FROM cases WHERE status = 'OPEN') sub1
JOIN (SELECT case_id, AVG(hours) AS avg_time FROM (SELECT case_id, ... FROM history) sub3 GROUP BY case_id) sub2
ON sub1.id = sub2.case_id;
```
Reading nested subqueries requires parsing from the inside out. CTEs allow queries to be written top-to-bottom in linear, sequential steps, just like reading standard procedural Python code!

## 3. Why Backend Engineers Use It
- **Code Readability & Maintainability**: Breaks down complex enterprise analytics into small, self-contained logical units with descriptive names.
- **Reusability within the Query**: You can reference the same CTE multiple times in the final query (e.g. self-joining a summary dataset to compute percentages).
- **Recursive Processing**: Enables traversing tree hierarchies (e.g. organizational manager trees, parent-child ticket epics, dependency graphs).

## 4. How It Works: Basic Syntax
```sql
WITH <cte_name> AS (
    -- Subquery definition
    SELECT column1, column2
    FROM table_name
    WHERE condition
)
-- Main query consuming the CTE
SELECT *
FROM <cte_name>;
```

## 5. Real Project CTE Examples (from `sql/queries.sql`)

### Example 1: Case Summary Dashboard (Single CTE)
```sql
WITH case_summary AS (
    SELECT
        status,
        priority,
        COUNT(*)        AS total_cases,
        MIN(created_at) AS earliest_case,
        MAX(created_at) AS latest_case
    FROM cases
    GROUP BY status, priority
)
SELECT
    status,
    priority,
    total_cases,
    earliest_case,
    latest_case
FROM case_summary
ORDER BY total_cases DESC;
```

### Example 2: Chaining Multiple CTEs (Pipeline Architecture)
You can chain multiple CTEs by separating them with commas. Each subsequent CTE can reference any previously declared CTE:

```sql
WITH change_counts AS (
    -- Step 1: Aggregate change counts per case
    SELECT
        case_id,
        COUNT(*) AS total_changes,
        MIN(changed_at) AS first_change,
        MAX(changed_at) AS last_change
    FROM case_history
    GROUP BY case_id
),
case_details AS (
    -- Step 2: Fetch case details with user names
    SELECT
        c.id,
        c.title,
        c.status,
        c.priority,
        creator.full_name AS creator_name
    FROM cases c
    INNER JOIN users creator ON c.created_by = creator.id
)
-- Step 3: Combine both modular abstractions cleanly
SELECT
    cd.title,
    cd.status,
    cd.creator_name,
    COALESCE(cc.total_changes, 0) AS total_changes,
    cc.first_change,
    cc.last_change
FROM case_details cd
LEFT JOIN change_counts cc ON cd.id = cc.case_id
ORDER BY total_changes DESC;
```

### Example 3: Workload Analysis CTE with Business Categorization
```sql
WITH user_workload AS (
    SELECT
        u.id AS user_id,
        u.full_name,
        u.role,
        COUNT(DISTINCT c_created.id) AS cases_created,
        COUNT(DISTINCT c_assigned.id) AS active_assigned_cases
    FROM users u
    LEFT JOIN cases c_created  ON u.id = c_created.created_by
    LEFT JOIN cases c_assigned ON u.id = c_assigned.assigned_to
        AND c_assigned.status IN ('OPEN', 'IN_PROGRESS')
    GROUP BY u.id, u.full_name, u.role
)
SELECT
    full_name,
    role,
    cases_created,
    active_assigned_cases,
    CASE
        WHEN active_assigned_cases >= 3 THEN 'OVERLOADED'
        WHEN active_assigned_cases >= 1 THEN 'OPTIMAL'
        ELSE 'AVAILABLE'
    END AS workload_status
FROM user_workload
ORDER BY active_assigned_cases DESC;
```

## 6. CTEs vs. Temporary Tables vs. Views
| Feature | CTE (`WITH ...`) | Temporary Table (`CREATE TEMP TABLE`) | View (`CREATE VIEW`) |
|---|---|---|---|
| **Lifespan** | Single SQL query execution | Entire database session / connection | Persistent database object |
| **Materialization** | Inlined or ephemeral memory | Written to temp disk/memory with indexes | Stored query definition |
| **Ideal For** | Improving readability of a complex single query | Heavy multi-step batch scripts across queries | Reusable standardized reporting across teams |

## 7. Common Mistakes
1. **Adding `WITH` multiple times**:
   - BAD: `WITH cte1 AS (...) WITH cte2 AS (...)`
   - GOOD: `WITH cte1 AS (...), cte2 AS (...)` (only one `WITH` keyword).
2. **Forgetting that a CTE cannot outlive the query**:
   - Attempting to query `SELECT * FROM cte1;` in a second query will fail with `no such table: cte1`.

## 8. Practical Exercises
1. Execute query 2b from [sql/queries.sql](file:///d:/week1_kpmg/case-management-backend/sql/queries.sql). Verify that cases with zero history changes display `total_changes = 0` via `COALESCE`.
2. Write a CTE that calculates the average number of days cases remain in `OPEN` status before resolution.

## 9. Interview Questions & Model Answers
**Q: What is a CTE in SQL and what advantages does it offer over nested subqueries?**
*Answer:* A Common Table Expression (CTE) is a named temporary result set defined with the `WITH` clause before a primary SQL statement. Compared to nested subqueries, CTEs significantly improve code readability by organizing complex query logic into linear, top-to-bottom steps. They can be referenced multiple times within the same statement, prevent redundant subquery computations, and support recursion for hierarchical data traversal.

## 10. Short Self-Test
1. Which keyword introduces a Common Table Expression? *(Answer: `WITH`).*
2. Can a CTE reference a previously defined CTE within the same query? *(Answer: Yes, by chaining them with commas).*
