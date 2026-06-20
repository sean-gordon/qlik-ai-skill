# Qlik Sense Advanced Patterns and Best Practices — Qvd Incremental


> Split from `advanced_patterns.md`. Companion files share the `advanced_` prefix.


## QVD Strategy and Incremental Load

### What is a QVD File?

A QVD (Qlik View Data) file is a proprietary binary format that stores exactly one Qlik Sense internal table. It is the most efficient format for inter-app data sharing.

**Benefits:**
- Reading from QVD is approximately 10× faster than standard mode, and 100× faster than reading from source database.
- QVD files can be shared across apps without re-querying the source.
- They enable a layered ETL architecture.

**Two read modes:**
- **Optimised mode** (fastest): automatically used when the LOAD statement is a simple `SELECT *` with no transformations.
- **Standard mode**: used when WHERE clauses, transformations, or JOIN operations are applied. Still much faster than database.

```qlik
// Optimised mode (no WHERE clause, no transforms)
LOAD * FROM 'lib://QVDs/Sales.qvd' (qvd);

// Standard mode (WHERE clause forces standard mode)
LOAD * FROM 'lib://QVDs/Sales.qvd' (qvd) WHERE Year = 2024;
```

### Creating QVD Files

```qlik
// Create/overwrite a QVD
STORE TableName INTO 'lib://QVDs/TableName.qvd' (qvd);

// Create from inline or transformed data
Sales2024:
LOAD * FROM source.csv WHERE Year = 2024;
STORE Sales2024 INTO 'lib://QVDs/Sales2024.qvd' (qvd);
DROP TABLE Sales2024;
```

### QVD Metadata Functions

```qlik
QvdCreateTime('lib://QVDs/Sales.qvd')   // when was it created
QvdNoOfRecords('lib://QVDs/Sales.qvd')  // how many rows
QvdNoOfFields('lib://QVDs/Sales.qvd')   // how many fields
QvdTableName('lib://QVDs/Sales.qvd')    // stored table name
QvdFieldName('lib://QVDs/Sales.qvd', 1) // name of field 1
```

### Buffer Prefix (Automatic QVD Caching)

The `Buffer` prefix automatically creates and manages a QVD cache for a LOAD or SELECT statement.

```qlik
// Cache indefinitely (until app changes)
Buffer SELECT * FROM MyTable;

// Refresh after 7 days
Buffer (stale after 7 days) SELECT * FROM MyTable;

// Incremental — append only new records from log files
Buffer (incremental) LOAD * FROM LogFile.txt
(ansi, txt, delimiter is '\t', embedded labels);
```

### Incremental Load Architecture

#### Pattern 1: Append Only (Log Files)

```qlik
// Conditions: text files, records only appended, never updated
Buffer (incremental) LOAD * FROM LogFile.txt
(ansi, txt, delimiter is '\t', embedded labels);
```

#### Pattern 2: Insert Only (Database)

```qlik
// Conditions: database source, new records identifiable by timestamp
// No updates or deletes

QV_Table:
SQL SELECT PrimaryKey, X, Y
FROM DB_TABLE
WHERE ModificationTime >= #$(LastExecTime)#
  AND ModificationTime < #$(BeginningThisExecTime)#;

Concatenate LOAD PrimaryKey, X, Y FROM 'lib://QVDs/QV_Table.qvd' (qvd);
STORE QV_Table INTO 'lib://QVDs/QV_Table.qvd' (qvd);
```

#### Pattern 3: Insert and Update (No Delete)

```qlik
// Conditions: records can be updated, primary key available
// Forces standard mode QVD read

QV_Table:
SQL SELECT PrimaryKey, X, Y
FROM DB_TABLE
WHERE ModificationTime >= #$(LastExecTime)#;

// Load from QVD excluding already-loaded keys (deduplication)
Concatenate LOAD PrimaryKey, X, Y
FROM 'lib://QVDs/QV_Table.qvd' (qvd)
WHERE NOT Exists(PrimaryKey);

STORE QV_Table INTO 'lib://QVDs/QV_Table.qvd' (qvd);
```

#### Pattern 4: Insert, Update and Delete

```qlik
// Most complex: handles all three operations
LET ThisExecTime = Now();

QV_Table:
SQL SELECT PrimaryKey, X, Y
FROM DB_TABLE
WHERE ModificationTime >= #$(LastExecTime)#
  AND ModificationTime < #$(ThisExecTime)#;

// Load from QVD excluding updated keys
Concatenate LOAD PrimaryKey, X, Y
FROM 'lib://QVDs/QV_Table.qvd' (qvd)
WHERE NOT EXISTS(PrimaryKey);

// Remove deleted records by inner join on all current PKs from source
Inner Join SQL SELECT PrimaryKey FROM DB_TABLE;

// Only save if no errors occurred
IF ScriptErrorCount = 0 THEN
    STORE QV_Table INTO 'lib://QVDs/QV_Table.qvd' (qvd);
    LET LastExecTime = ThisExecTime;
END IF;
```

### Three-Tier QVD Architecture

The recommended enterprise pattern for large deployments:

```
Tier 1: Extract (QVD Layer)
    Source databases → Raw QVDs (one per source table)
    Purpose: isolate source systems; fast refresh

Tier 2: Transform (QVD Layer)
    Raw QVDs → Transformed QVDs (business logic applied)
    Purpose: joins, data cleansing, derived fields, master data

Tier 3: Presentation (App Layer)
    Transformed QVDs → Qlik Sense Apps
    Purpose: final model, UI measures, visualisations
```

Each tier runs on a separate reload schedule. Apps can share Tier 2 QVDs without duplicating transformation logic.

---

## Optimisation Techniques

### Reducing Reload Time

1. **Use QVD files** as an extraction layer. Re-reading QVDs is 10-100× faster than querying source systems.

2. **Push transformation to SQL** where the database is more efficient:

```sql
-- Aggregate before loading
SELECT ProductID, SUM(Amount) as TotalAmount
FROM Orders
GROUP BY ProductID
```

3. **Load only required fields** — never use `SELECT *` in production:

```qlik
LOAD CustomerID, CustomerName, Region FROM customers.csv;
// Not: LOAD * FROM customers.csv;
```

4. **Use WHERE clauses** to limit loaded records:

```qlik
LOAD * FROM orders.csv WHERE Year(OrderDate) >= 2020;
```

5. **Drop temporary tables** after use:

```qlik
TempTable: LOAD * FROM raw.csv;
// ... transformations ...
FinalTable: LOAD [...] Resident TempTable;
DROP TABLE TempTable;
```

6. **Use `First n`** prefix during development:

```qlik
First 1000 LOAD * FROM large_table.csv;
```

### Reducing App Memory Usage

1. **Remove unused fields** — unused fields consume RAM and clutter the data model.

2. **Avoid high-cardinality text fields** in dimension tables — store numeric keys and use mapping for display labels.

3. **Use `Distinct`** to load only unique values where appropriate:

```qlik
LOAD DISTINCT CustomerID, Region FROM orders.csv;
```

4. **Avoid storing timestamps in transaction tables** if only date granularity is needed — truncate to date.

5. **Use `DROP FIELD`** after joining:

```qlik
DROP FIELD TempKey;
DROP FIELDS Field1, Field2;
```

### Improving Chart Expression Performance

1. **Avoid heavy expressions in dimensions** — calculated dimensions are evaluated per row, not cached.

2. **Minimise use of `If()` inside aggregations** — use Set Analysis instead:

```qlik
// Slower
Sum(If(Region = 'ZA', Sales))

// Faster
Sum({$<Region={'ZA'}>} Sales)
```

3. **Avoid nested If() chains** — use `Match()`, `Pick()` or `Class()`.

4. **Limit `Aggr()` depth** — each level of `Aggr()` creates a virtual table; more than two levels degrades performance noticeably.

5. **Optimise UI calculation speed** by caching expensive measures as fields during reload:

```qlik
// Calculate in script instead of chart
LOAD
    SalesID,
    Quantity * UnitPrice * (1 - Discount) as NetRevenue
FROM sales.csv;
```

### Data Model Performance

- **Key fields should be integers** where possible — smaller memory footprint, faster joins.
- **Avoid synthetic keys** (see earlier section).
- **Star schema outperforms snowflake** for Qlik's in-memory model.
- **Normalise only to the level needed** — fully normalised databases are often a poor fit for Qlik without some de-normalisation.

---
