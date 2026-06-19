# Qlik Sense Advanced Patterns and Best Practices

> Extracted from: *Manage Data* (Qlik Sense April 2020), *Create Apps and Visualisations* (Qlik Sense April 2020), *Qlik Sense Cookbook* (Packt 2015), *Learning Qlik Sense — The Official Guide Second Edition* (Packt 2015), *Collaborate in Qlik Sense* (Qlik Sense April 2020), *Explore, Discover and Analyse* (Qlik Sense April 2020), *Qlik Sense Advanced Data Visualisation* (Dr Christopher Ilacqua).
> Language: South African English.

## Companion references

| Reference | Use when |
|-----------|----------|
| [Scripting Knowledgebase](scripting_knowledgebase.md) | Writing or reviewing backend load scripts, LOAD/SELECT/JOIN patterns |
| [Expression Knowledgebase](expression_knowledgebase.md) | Writing or debugging frontend chart expressions, Set Analysis, Aggr |
| [Functions Reference](functions_reference.md) | Looking up any Qlik function signature, parameters, or examples |
| [Debugging Guide](debugging_guide.md) | Diagnosing script errors, data model issues, or performance problems |
| [Visualisation Guide](visualization_guide.md) | Choosing chart types, applying DAR layout, or styling dashboards |

---

## Table of Contents

1. [Advanced Data Modelling](#advanced-data-modelling)
2. [QVD Strategy and Incremental Load](#qvd-strategy-and-incremental-load)
3. [Advanced Scripting Patterns](#advanced-scripting-patterns)
4. [Script Prefixes: Hierarchy, Crosstable, IntervalMatch](#script-prefixes-hierarchy-crosstable-intervalmatch)
5. [Mapping Tables: Alternative to Joins](#mapping-tables-alternative-to-joins)
6. [Join and Keep — When and How](#join-and-keep--when-and-how)
7. [Optimisation Techniques](#optimisation-techniques)
8. [Advanced Set Analysis Patterns](#advanced-set-analysis-patterns)
9. [Advanced Visualisation Techniques](#advanced-visualisation-techniques)
10. [Master Library Best Practices](#master-library-best-practices)
11. [Alternate States for Comparative Analysis](#alternate-states-for-comparative-analysis)
12. [App Architecture and Design](#app-architecture-and-design)
13. [Section Access and Security](#section-access-and-security)
14. [Data Manager vs Data Load Editor](#data-manager-vs-data-load-editor)
15. [Data Cleansing Patterns](#data-cleansing-patterns)
16. [Publishing, Streams, and Distribution](#publishing-streams-and-distribution)
17. [Storytelling and Snapshots](#storytelling-and-snapshots)
18. [On-Demand Apps](#on-demand-apps)
19. [Direct Discovery](#direct-discovery)
20. [Analytic Connections (SSE)](#analytic-connections-sse)
21. [Administration and Governance](#administration-and-governance)
22. [Debugging and Troubleshooting](#debugging-and-troubleshooting)
23. [Cookbook Recipes](#cookbook-recipes)

---

## Advanced Data Modelling

### The Associative Data Model

Qlik Sense uses an **in-memory associative model** rather than a traditional OLAP cube or relational query model. Tables are linked automatically when they share field names. The engine tracks associations between ALL loaded tables simultaneously, enabling the green/white/grey selection experience.

**Key principles:**
- Two tables with the same field name are automatically associated.
- The association is bi-directional — selections in any table propagate through all associations.
- Field names are case-sensitive.
- Field *values* matching is case-insensitive by default.

### Star Schema and Snowflake Schema

The **star schema** is the most efficient structure for Qlik Sense:

```
          DimDate
             |
DimProduct—FactSales—DimCustomer
             |
         DimRegion
```

Rules for a clean star schema:
- One fact table at the centre.
- Dimension tables linked to the fact table on a single key field.
- Dimension tables do NOT link to each other (avoid chasm traps).
- Key fields have identical names in both tables.

**Snowflake schemas** (where dimension tables link to other dimension tables) are acceptable but create more complex association paths. Flatten where possible for performance.

### Synthetic Keys — Identifying and Resolving

Qlik Sense creates a **synthetic key** when more than one field is shared between two tables. Synthetic keys appear as `$Syn` tables in the Data Model Viewer and degrade performance.

**Causes:**
- Two tables sharing multiple fields (e.g., both `OrderID` and `Date`).
- Forgot to rename common but non-linking fields (e.g., both tables have a `Name` field).

**Resolution strategies:**

```qlik
// Option 1: Rename the non-linking duplicate field
LOAD
    OrderID,
    Date as OrderDate,  // rename to avoid clash
    Amount
FROM orders.csv;

// Option 2: Concatenate key fields into a composite key
LOAD
    OrderID & '|' & LineID as OrderLineKey,
    OrderID,
    LineID,
    Amount
FROM order_lines.csv;

// Option 3: Drop the duplicate field
LOAD
    OrderID,
    Amount
FROM orders.csv;
// Then JOIN with the other table
```

### Circular References — Identifying and Breaking

A **circular reference** exists when a chain of associations forms a loop. Qlik Sense will flag this with a warning and one of the links will be shown as a "loosely coupled" table (dashed border in Data Model Viewer).

**Resolution — use a Link Table:**

```qlik
// Problem: Customer, Orders, and Products all share keys creating a loop

// Solution: Create a link table
LinkTable:
LOAD DISTINCT
    CustomerID,
    ProductID,
    OrderID
FROM orders.csv;

CustomerTable:
LOAD CustomerID, CustomerName FROM customers.csv;

ProductTable:
LOAD ProductID, ProductName FROM products.csv;

OrderTable:
LOAD OrderID, OrderDate, Amount FROM orders.csv;
// Drop original key fields from individual tables to remove direct associations
```

### Avoiding Chasm Traps

A **chasm trap** occurs when two fact tables are linked through a dimension, causing double-counting. Example: Sales and Budget both link to DimCustomer.

```qlik
// Solution: use separate Qlik Sense associations (natural join)
// Do NOT join the two fact tables — keep them as separate tables.
// Qlik's associative model handles this correctly at query time.

// If double-counting persists, use Set Analysis to scope expressions:
Sum({$} Sales)    // from Sales table
Sum({$} Budget)   // from Budget table
```

### Fan Traps

A **fan trap** occurs when a many-to-many relationship exists. Example: one Customer has many Orders, and one Order has many Lines.

```qlik
// The correct structure already handles this:
// DimCustomer → FactOrders → FactOrderLines (chain, not star)
// Aggregations at each level work correctly.

// Avoid joining Order-level and Line-level into one table — this multiplies rows.
```

---

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

## Advanced Scripting Patterns

### Dollar-Sign Expansion

Variables and expressions can be expanded inside script statements using `$(variable)` or `$(=expression)`.

```qlik
// Variable expansion
SET vTable = 'Sales';
LOAD * FROM 'lib://Data/$(vTable).qvd' (qvd);

// Expression expansion (evaluated at runtime)
SET vCurrentYear = $(=Year(Today()));
LOAD * FROM data.csv WHERE Year = $(vCurrentYear);

// Numeric expansion (preserves decimal format)
SET vRate = 0.15;
LOAD Amount * $(#vRate) as Tax FROM data.csv;

// Dollar-sign in set analysis
Sum({$<Year={$(=Max(Year)-1)}>} Sales)
Sum({$<Year={$(#vLastYear)}>} Sales)
```

### File Inclusion

Store common script code in `.qvs` text files and include them.

```qlik
$(include=lib://Scripts/common_variables.qvs);
$(include=lib://Scripts/date_table.qvs);
```

### Subroutines

```qlik
SUB LoadTable(vTableName, vPath)
    [$(vTableName)]:
    LOAD * FROM '$(vPath)/$(vTableName).qvd' (qvd);
END SUB

CALL LoadTable('Sales', 'lib://QVDs')
CALL LoadTable('Customers', 'lib://QVDs')
```

**Parameter passing note:** Parameters are passed by reference for variables, but by value for expressions. Only variables are copied back on exit.

```qlik
SUB Increment(X, Y)
    X = X + 1
    Y = Y + 1
END SUB

A = 1
X = 1
CALL Increment(A, (X+1)*2)
// A = 2 (copied back); second parameter not copied (it's an expression)
```

### Loading Multiple Files with For Each

```qlik
// Load all QVDs in a folder
FOR EACH file IN FileList('lib://QVDs/Sales/*.qvd')
    LOAD * FROM [$(file)] (qvd);
NEXT file

// Load all CSV files from a folder
FOR EACH file IN FileList('lib://Data/*.csv')
    LOAD *, '$(file)' as SourceFile FROM [$(file)] (txt, delimiter is ',', embedded labels);
NEXT file
```

### Reading Records Repeatedly with While / IterNo

```qlik
// Unpack multiple values from a single field
MyTab: LOAD
    Student,
    mid(Grades, IterNo(), 1) as Grade,
    pick(IterNo(), 'Math', 'English', 'Science', 'History') as Subject
FROM Grades.csv
WHILE IsNum(mid(Grades, IterNo(), 1));
```

### Preceding Load Pattern

Applies transformations to the result of a subsequent LOAD/SELECT without creating a temporary table. Extremely powerful for staged transformations.

```qlik
// Double preceding load: apply transforms in two stages
FinalTable:
LOAD
    CustomerID,
    Upper(CustomerName) as CustomerName,
    if(Status = 'A', 'Active', 'Inactive') as StatusLabel
;
LOAD
    CustomerID,
    Trim(CustomerName) as CustomerName,
    Status
;
SQL SELECT CustomerID, CustomerName, Status FROM Customers;
```

### Concatenation Strategies

```qlik
// Auto-concatenation: same fields, different files (automatic)
LOAD * FROM file1.csv;
LOAD * FROM file2.csv;  // auto-concatenated if same field names

// Forced concatenation: different field sets
Concatenate LOAD * FROM file2.csv;

// Named concatenation target
Concatenate (Tab1) LOAD * FROM file3.csv;

// Prevent auto-concatenation
NoConcatenate LOAD * FROM file2.csv;

// Crosstable to normalise wide tables
Crosstable(Month, Sales, 1) LOAD * FROM sales_wide.csv;
// Column: Year, Jan, Feb, ..., Dec → Year, Month, Sales (normalised)
```

### Working with Inline Data

```qlik
// Quick reference table
Currencies: LOAD * INLINE [
CurrencyCode, CurrencyName, Symbol
ZAR, South African Rand, R
USD, US Dollar, $
EUR, Euro, €
GBP, British Pound, £
];

// Calendar skeleton
CalendarTemplate: LOAD * INLINE [
Period, SortOrder
YTD, 1
QTD, 2
MTD, 3
Last 12 Months, 4
];
```

---

## Script Prefixes: Hierarchy, Crosstable, IntervalMatch

### Hierarchy — Expanding Parent-Child Tables

Transforms an adjacent nodes table into an expanded nodes table with one column per hierarchy level.

```qlik
Hierarchy(
    NodeID,           // field containing node identifier
    ParentID,         // field containing parent identifier
    NodeName,         // field containing node name
    [ParentName],     // output: name of parent (optional)
    [PathSource],     // field to use for path (optional, default=NodeName)
    [PathName],       // output: full path field (optional)
    [PathDelimiter],  // path separator (optional, default='/')
    [Depth]           // output: depth level field (optional)
)(loadstatement | selectstatement)
```

```qlik
Hierarchy(NodeID, ParentID, NodeName, ParentName, NodeName, PathName, '\', Depth)
LOAD * INLINE [
NodeID, ParentID, NodeName
1, 4, London
2, 3, Munich
3, 5, Germany
4, 5, UK
5, , Europe
];
// Result adds: NodeName1(Europe), NodeName2(UK/Germany), NodeName3(London/Munich),
//              ParentName, PathName (Europe\UK\London), Depth (3)
```

### HierarchyBelongsTo — All Ancestor Relationships

Creates a table with every ancestor-descendant pair, enabling "select a node to include all descendants" functionality.

```qlik
HierarchyBelongsTo(
    NodeID,        // node identifier field
    ParentID,      // parent identifier field
    NodeName,      // node name field
    AncestorID,    // output: ancestor ID field name
    AncestorName,  // output: ancestor name field name
    [DepthDiff]    // output: depth difference (optional)
)(loadstatement | selectstatement)
```

```qlik
HierarchyBelongsTo(NodeID, ParentID, NodeName, AncestorID, AncestorName, DepthDiff)
LOAD * FROM OrgChart.qvd (qvd);
// Each node appears once for each ancestor (including itself at depth 0)
// Selecting an ancestor in a filter selects all descendants
```

### Crosstable — Unpivoting Wide Tables

Converts a wide cross-table format into a normalised tall format.

```qlik
Crosstable(
    attribute_field_name,  // new field for column headers
    data_field_name,       // new field for cell values
    [n]                    // number of qualifier columns before pivot columns (default 1)
)(loadstatement)
```

```qlik
// Before: Year, Q1, Q2, Q3, Q4
// After:  Year, Quarter, Sales
Crosstable(Quarter, Sales, 1)
LOAD * FROM quarterly_sales.csv;

// Multiple qualifier columns (n=2)
Crosstable(Month, Sales, 2)
LOAD * FROM sales_year_region.csv;
// Before: Year, Region, Jan, Feb, ..., Dec
// After:  Year, Region, Month, Sales
```

### Generic Load — Attribute-Value Tables

Unpacks a generic attribute-value table into separate tables per attribute.

```qlik
// Input: Object, Attribute, Value
Generic LOAD * FROM attributes.csv;
// Creates separate tables: ball.color, ball.diameter, ball.weight, etc.
```

### IntervalMatch — Matching Values to Intervals

Links discrete values to intervals. Essential for slowly changing dimensions and order-to-event matching.

```qlik
// Basic: match Time to intervals defined by Start and End
IntervalMatch(Time)
LOAD Start, End FROM intervals.qvd (qvd);

// Extended: match Time AND a key field
IntervalMatch(Time, ProductID)
LOAD Start, End, ProductID, Price FROM price_history.qvd (qvd);
```

**Full pattern for slowly changing dimensions:**

```qlik
// Step 1: Load the transaction table
Transactions:
LOAD TransDate, ProductID, Quantity FROM transactions.qvd (qvd);

// Step 2: Load the price history (intervals)
PriceHistory:
LOAD
    ProductID,
    ValidFrom as Start,
    ValidTo as End,
    Price
FROM price_history.qvd (qvd);

// Step 3: Create the interval match
Inner Join (Transactions)
IntervalMatch(TransDate, ProductID)
LOAD Start, End, ProductID
Resident PriceHistory;
```

**Creating intervals from single-date change records:**

```qlik
// Source has: ProductID, ChangeDate, Price
// Need: ProductID, ValidFrom, ValidTo, Price

PriceHistory:
LOAD
    ProductID,
    ChangeDate as ValidFrom,
    Price
FROM price_changes.qvd (qvd);

// Add ValidTo by looking at the next ChangeDate for same ProductID
Left Join (PriceHistory)
LOAD
    ProductID,
    Peek('ChangeDate') as ValidTo
Resident PriceHistory
ORDER BY ProductID, ChangeDate ASC;

// Fill in maximum date for the latest record
LOAD
    ProductID,
    ValidFrom,
    if(IsNull(ValidTo), '31/12/2099', ValidTo) as ValidTo,
    Price
Resident PriceHistory;
```

---

## Mapping Tables: Alternative to Joins

Mapping tables are two-column lookup tables that provide an efficient alternative to `JOIN` when only one field needs to be looked up.

**Advantages over JOIN:**
- Does not increase the number of rows in the main table.
- Does not require the lookup field to be a key in the Qlik data model.
- Lower memory usage.

```qlik
// Create mapping table (always two columns: input, output)
CountryMap:
Mapping LOAD CustomerID, CountryName FROM customers.csv;

// Apply in LOAD
Sales:
LOAD
    OrderID,
    CustomerID,
    ApplyMap('CountryMap', CustomerID, 'Unknown') as Country,
    Amount
FROM orders.csv;
```

**MapSubstring:** Replaces all occurrences of keys in a string with mapped values.

```qlik
AbbrevMap:
Mapping LOAD * INLINE [
from, to
'S.A.', 'South Africa'
'U.S.', 'United States'
'U.K.', 'United Kingdom'
];

LOAD MapSubstring('AbbrevMap', CountryText) as Country FROM data.csv;
```

---

## Join and Keep — When and How

### Join

Produces a single merged table. Use sparingly — it can inflate table sizes and hide row counts.

```qlik
// Default = outer join (all combinations)
LOAD a, b, c FROM table1.csv;
JOIN LOAD a, d FROM table2.csv;

// Inner join
LOAD * FROM table1.csv;
INNER JOIN LOAD * FROM table2.csv;

// Left join
LOAD * FROM table1.csv;
LEFT JOIN LOAD * FROM table2.csv;

// Right join
LOAD * FROM table1.csv;
RIGHT JOIN LOAD * FROM table2.csv;
```

### Keep

Same as Join but keeps the two tables as separate tables in the data model (no merging). Preferred over Join in most cases.

```qlik
// Left keep: reduce table2 to its intersection with table1
Tab1: LOAD * FROM table1.csv;
Tab2: LEFT KEEP LOAD * FROM table2.csv;

// Inner keep: reduce both tables to their intersection
Tab1: LOAD * FROM table1.csv;
Tab2: INNER KEEP LOAD * FROM table2.csv;
```

### When to Use Each

| Scenario | Recommendation |
|----------|---------------|
| Need a single merged table for a calculation | `JOIN` |
| Need to restrict one table based on another | `KEEP` |
| Need a simple field lookup | `Mapping` + `ApplyMap` |
| Need complex multi-field lookup | `JOIN` or `LookUp()` |
| Need to prevent automatic association | `RENAME` the shared field |

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

## Advanced Set Analysis Patterns

### Year-to-Date (YTD)

```qlik
// YTD based on maximum available year
Sum({$<Year={$(=Max(Year))}, Date={"<=$(=Max(Date))"}>} Sales)

// YTD using InYearToDate
Sum({$<Date={"=InYearToDate(Date, Max({1} Date), 0)"}>} Sales)

// Previous YTD
Sum({$<Year={$(=Max(Year)-1)}, Date={"<=$(=AddYears(Max(Date),-1))"}>} Sales)
```

### Same Period Last Year

```qlik
Sum({$<Year={$(=Max(Year)-1)}>} Sales)

// Preserve other selections
Sum({$<Year = {$(=Only(Year)-1)}>} Sales)
```

### Dynamic Rolling Period

```qlik
// Last N months (rolling)
Sum({$<YearMonth={"$(='>=' & Num(AddMonths(Today(),-12),'YYYYMM') & '<=' & Num(Today(),'YYYYMM'))"}>} Sales)

// Last 12 months using InMonths
Sum({$<Date={"=InMonths(12, Date, Today(), -1)"}>} Sales)
```

### Comparing Across Alternate States

```qlik
// State A measure
Sum({[Group1]} Sales)

// State B measure
Sum({[Group2]} Sales)

// Ratio
Sum({[Group1]} Sales) / Sum({[Group2]} Sales)
```

### Top N Analysis

```qlik
// Top 10 customers by sales
Sum({$<Customer={"=Aggr(Rank(Sum(Sales)), Customer) <= 10"}>} Sales)

// Exclude top 10 (everyone else)
Sum({$<Customer={"=Aggr(Rank(Sum(Sales)), Customer) > 10"}>} Sales)
```

### Proportional Analysis (Running Total as % of Grand Total)

```qlik
Sum(Sales) / Sum(TOTAL Sales)

// As percentage with set analysis (ignores selections for denominator)
Sum(Sales) / Sum({1} Sales)
```

### Complex Customer Segmentation

```qlik
// Customers who bought Product A but not Product B
Sum({$<Customer = P({1<Product={'ProductA'}>} Customer)
                - P({1<Product={'ProductB'}>} Customer)>} Sales)

// New customers (first purchase in current year)
Sum({$<Customer = {"=Min({1<Year={$(=Max(Year))}>} Year) = Max(Year)"}>} Sales)
```

---

## Advanced Visualisation Techniques

### Colour Expressions

Colours can be controlled via expressions in chart properties under "Colour by expression".

```qlik
// Traffic light by threshold
if(Sum(Sales)/Sum(Target) >= 1, green(), if(Sum(Sales)/Sum(Target) >= 0.8, yellow(), red()))

// Gradient by value
Colormix1(Sum(Sales)/Max(TOTAL Sum(Sales)), white(), green())

// Dimension-based consistent colour
RGB(
    128 + 127 * cos(FieldIndex('Region', Region) * 2.4),
    128 + 127 * sin(FieldIndex('Region', Region) * 2.4),
    180
)
```

### Reference Lines

Reference lines can be defined as expressions:

```qlik
// Average line
Avg(TOTAL Sum(Sales))

// Target line from data
Sum({$} Target)

// Constant threshold
100000
```

### KPI Best Practices

```qlik
// KPI with conditional colour
// Expression:
Sum(Sales)

// Background colour expression:
if(Sum(Sales) >= Sum(Target), rgb(0,128,0), rgb(200,0,0))

// Trend indicator
if(Sum(Sales) > Sum({$<Year={$(=Max(Year)-1)}>} Sales), '▲', '▼')
```

### Dynamic Chart Titles

Titles, subtitles, and tooltips accept expressions.

```qlik
// Dynamic title showing selection
='Sales for ' & GetCurrentSelections(', ', '=', ', ', 3)

// With period
='Sales — ' & Only(Year) & ' YTD'

// Default text when no selection
=if(GetSelectedCount(Region) = 0, 'All Regions', Concat(Region, ', '))
```

### Waterfall Chart Patterns

Use a straight table with `Accumulation` and a calculated dimension to simulate a waterfall:

```qlik
// Dimension: category (Opening, Sales, Costs, Closing)
// Measure: value
// Sort dimension: ValueList('Opening', 'Sales', 'Costs', 'Closing')

if(ValueList('Opening','Sales','Costs','Closing') = 'Opening', OpeningBalance,
   if(ValueList('Opening','Sales','Costs','Closing') = 'Sales', Sum(Sales),
      if(ValueList('Opening','Sales','Costs','Closing') = 'Costs', -Sum(Costs),
         OpeningBalance + Sum(Sales) - Sum(Costs))))
```

### Dimensionless Bar Chart

Create a bar chart without a dimension but with multiple calculated measures using `ValueList()`:

```qlik
// Dimension (calculated):
ValueList('Sales', 'Target', 'Variance')

// Measure:
if(ValueList('Sales', 'Target', 'Variance') = 'Sales', Sum(Sales),
   if(ValueList('Sales', 'Target', 'Variance') = 'Target', Sum(Target),
      Sum(Sales) - Sum(Target)))
```

### Scatter Chart: Navigating Many Data Points

- Enable zoom/pan in chart properties.
- Use calculated colour expressions to highlight clusters.
- Use `Class()` as a dimension to group dense areas.

### Treemap Composition Patterns

```qlik
// Treemap with two levels
// Dimension 1: Region
// Dimension 2: Product category
// Measure: Sum(Sales)
// Colour by: Sum(Sales)/Sum(TOTAL Sales)  — shows relative size
```

### Combo Chart: Actual vs Target

```qlik
// Bar: Sum(Sales) — left axis
// Line: Sum(Target) — right axis (separate axis)
// Reference line: =Avg(Sum(Sales))
```

---

## Master Library Best Practices

The Master Library stores reusable dimensions, measures, and visualisations.

### Creating Master Dimensions

```qlik
// Drill-down dimension (from UI)
// Add as a group: Country > Region > City

// Calculated dimension
=Upper(Country)

// With conditional display label
=if(Len(CustomerName) > 20, Left(CustomerName,17) & '...', CustomerName)
```

### Creating Master Measures

Always use an aggregation function:

```qlik
// Basic
Sum(Sales)

// Formatted
Num(Sum(Sales), '#,##0.00', '.', ',') & ' ZAR'

// Conditional
if(Sum(Sales) > 0, Sum(Sales), 0)
```

### Tagging for Organisation

Use consistent tags to help users find master items:

- `#financial` — financial KPIs
- `#geo` — geography dimensions
- `#time` — date/period dimensions
- `#operational` — operational metrics
- `#ratio` — percentages and ratios

### Global Changes via Master Library

Changing a master measure or dimension automatically updates all visualisations that use it. This is the primary benefit: one change propagates everywhere.

---

## Alternate States for Comparative Analysis

Alternate states allow multiple independent selection contexts within the same app.

### Creating Alternate States

In the UI: App properties → Alternate states → Add state.

Or via script (not recommended for runtime use).

### Using Alternate States

```qlik
// Default state (user's current selection)
Sum(Sales)

// Named state
Sum({[Group 1]} Sales)

// Compare two states
Sum({[Group 1]} Sales) - Sum({[Group 2]} Sales)

// Ratio
Sum({[Group 1]} Sales) / nullif(Sum({[Group 2]} Sales), 0)
```

### Assigning Objects to States

In the object's properties → State → select from the dropdown.

### StateName() for Dynamic Labels

```qlik
// Dynamic text in a text box or chart title
='Comparing: ' &
  if(StateName() = '$', 'Default', StateName())

// Colour by state
if(StateName() = 'Group 1', rgb(70,130,180),
   if(StateName() = 'Group 2', rgb(60,179,113),
      lightgray()))
```

---

## App Architecture and Design

### Three-Sheet Pattern

A well-designed Qlik Sense app typically uses three tiers of sheets:

1. **Overview / Executive Sheet** — KPIs, summary charts, trends. High-level. Decision-makers.
2. **Analysis Sheets** — Drill-down charts, filters, comparative analysis. Analysts.
3. **Detail / Data Sheets** — Tables, raw data, export-ready. Power users.

### Global Filters / Selections Panel

- Place filter panes for the most common dimensions (Date, Region, Product) on a collapsible sidebar or at the top of key sheets.
- Use a "Clear All Selections" button on every sheet.

### Bookmarks for Common Contexts

Encourage users to create bookmarks for:
- Current YTD with default filters
- Prior year comparative view
- Key market/region selections
- "All data" (cleared selections) starting point

### Sheet Navigation and Actions

Buttons can navigate to other sheets and simultaneously set selections:

```qlik
// Button action: Navigate to sheet + Set field value
// Action 1: Set field value — Year = 2024
// Action 2: Navigate to sheet — Analysis Sheet
```

### Naming Conventions

| Object | Convention | Example |
|--------|-----------|---------|
| Tables | PascalCase | `FactSales`, `DimCustomer` |
| Fields | PascalCase | `CustomerID`, `OrderDate` |
| Variables | camelCase with `v` prefix | `vCurrentYear`, `vLastYear` |
| Measures | Title Case | `Total Sales`, `Gross Margin %` |
| Dimensions | Title Case | `Customer Name`, `Product Category` |
| QVD files | PascalCase + `.qvd` | `FactSales.qvd`, `DimCustomer.qvd` |
| Script tabs | Descriptive names | `01_Init`, `02_Extract`, `03_Transform` |

### Script Tab Organisation

```
Tab 01: Initialisation (SET variables, common settings)
Tab 02: Date Calendar (master date table)
Tab 03: Dimension Tables (customers, products, etc.)
Tab 04: Fact Tables (transactions, events)
Tab 05: Derived Fields and Aggregations
Tab 06: Data Quality Checks
```

### Date Calendar Pattern

A proper calendar table is essential for time intelligence.

```qlik
// Generate a complete date calendar
MinDate:
LOAD Min(TransDate) as MinDate FROM transactions.qvd (qvd);

MaxDate:
LOAD Max(TransDate) as MaxDate FROM transactions.qvd (qvd);

LET vMinDate = Peek('MinDate', 0, 'MinDate');
LET vMaxDate = Peek('MaxDate', 0, 'MaxDate');
DROP TABLES MinDate, MaxDate;

Calendar:
LOAD
    Date(Date, 'DD/MM/YYYY') as Date,
    Year(Date) as Year,
    Month(Date) as Month,
    Day(Date) as Day,
    Week(Date) as Week,
    WeekYear(Date) as WeekYear,
    WeekDay(Date) as WeekDay,
    Dual('Q' & Ceil(Month(Date)/3), Ceil(Month(Date)/3)) as Quarter,
    Dual(WeekYear(Date) & 'W' & Week(Date), WeekStart(Date)) as YearWeek,
    MonthName(Date) as MonthYear,
    Year(Date) * 100 + Month(Date) as YearMonth,
    InYearToDate(Date, Today(), 0) as IsYTD,
    InQuarterToDate(Date, Today(), 0) as IsQTD,
    InMonthToDate(Date, Today(), 0) as IsMTD,
    InYear(Date, Today(), -1) as IsPriorYear,
    InYearToDate(Date, Today(), -1) as IsPriorYTD
;
LOAD Date($(vMinDate) + RowNo() - 1) as Date
AUTOGENERATE $(vMaxDate) - $(vMinDate) + 1;
```

---

## Section Access and Security

Section Access controls which users see which data within an app. It is defined in the script.

### Basic Structure

```qlik
Section Access;
LOAD * INLINE [
ACCESS, USERID, PASSWORD, [FIELD_NAME]
ADMIN, ADMIN_USER, admin123,
USER, john.doe@company.co.za, pass123, ZA
USER, jane.smith@company.co.za, pass456, UK
USER, *,, *
];

Section Application;
// Normal data load below
```

### Access Levels

| ACCESS value | Permissions |
|--------------|-------------|
| `ADMIN` | Full access, all data, can manage app |
| `USER` | Standard access, subject to data reduction |

### Data Reduction (Row-Level Security)

The field name in Section Access must match a field name in the app data. Qlik automatically filters rows so each user only sees their own data.

```qlik
Section Access;
LOAD * INLINE [
ACCESS, USERID, REGION
ADMIN, admin@company.co.za,
USER, john.doe@company.co.za, ZA
USER, jane.smith@company.co.za, UK
];

Section Application;
Transactions:
LOAD *, Region FROM transactions.qvd (qvd);
// User john.doe will only see rows where Region='ZA'
```

### Dynamic Data Reduction

Use a separate table for access control (loaded from a secure source):

```qlik
Section Access;
UserAccess:
SQL SELECT ACCESS, USERID, REGION FROM security_db.dbo.UserAccessRights;

Section Application;
```

### OMIT Fields

Fields listed in `OMIT` column are hidden from that user:

```qlik
Section Access;
LOAD * INLINE [
ACCESS, USERID, OMIT
USER, standard_user, Salary; CostPrice
ADMIN, admin_user,
];
```

### Inherited Access Restrictions

When publishing or exporting apps, Section Access restrictions are inherited. Users cannot bypass them through direct export.

---

## Data Manager vs Data Load Editor

| Feature | Data Manager | Data Load Editor |
|---------|-------------|-----------------|
| Target user | Non-developers, analysts | Developers |
| Interface | GUI drag-and-drop | Script editor |
| Capabilities | Basic transformations, associations | Full script power |
| Suitable for | Small-medium apps | Enterprise apps |
| QVD support | Limited | Full |
| Scripted logic | No | Yes |
| Recommended for production | No | Yes |

### Synchronising Managed Tables

When both are used together, sync scripted tables via Data Manager → "Synchronise scripted tables".

### Calculated Fields in Data Manager

Data Manager supports calculated fields using a subset of Qlik functions:

```qlik
// In Data Manager calculated field:
Upper([CustomerName])
Left([ProductName], 10)
Year([OrderDate])
```

---

## Data Cleansing Patterns

### Handling Inconsistent Capitalisation

```qlik
// Using Lower() in a calculated field
Lower(CustomerType) as CustomerType

// Using mapping table
CapMap: Mapping LOAD * INLINE [
from, to
single, Single
SINGLE, Single
double, Double
DOUBLE, Double
];
LOAD ApplyMap('CapMap', Type) as Type FROM data.csv;

// Or simply use Upper() or Capitalize() consistently
Upper(CustomerType) as CustomerType
```

### Handling Inconsistent Values

```qlik
// Mapping to standardise country names
CountryMap: Mapping LOAD * INLINE [
from, to
US, United States
USA, United States
U.S., United States
UK, United Kingdom
U.K., United Kingdom
SA, South Africa
ZA, South Africa
'South Africa', South Africa
];

LOAD ApplyMap('CountryMap', Country, Country) as Country FROM data.csv;
```

### NULL Handling

```qlik
// Replace NULL with default value
if(IsNull(Revenue), 0, Revenue) as Revenue

// Using alt()
alt(Revenue, 0)

// NullInterpretation variable (treats empty string as NULL)
SET NullInterpretation='';

// In range functions, RangeSum treats NULLs as 0
RangeSum(Above(Sum(Sales), 0, 3))
```

### Deduplication

```qlik
// Load only unique combinations
LOAD DISTINCT CustomerID, Region FROM data.csv;

// Load only first occurrence of each CustomerID
LOAD CustomerID, CustomerName
FROM data.csv
WHERE NOT Exists(CustomerID);
```

### String Cleaning

```qlik
// Remove specific characters
PurgeChar(PhoneNumber, ' ()-') as PhoneNumber

// Keep only digits
KeepChar(PhoneNumber, '0123456789') as PhoneDigits

// Standardise whitespace
Trim(Replace(Replace(Name, chr(9), ' '), chr(10), ' ')) as Name
```

---

## Publishing, Streams, and Distribution

### Streams

Streams are the primary container for published apps in Qlik Sense Enterprise. Apps in a stream are visible to users with access to that stream.

**Types of content in streams:**
- Published apps (read-only for users)
- Community sheets (shared by non-owners)

**Stream hierarchy:**
- Streams are flat (not hierarchical).
- Access is controlled by security rules.
- The "Published" state is separate from the "Development" working copy.

### Publishing Workflow

1. Develop app in personal "My Work" space (Qlik Sense Desktop or server personal space).
2. Test and validate.
3. Publish to a stream via: App menu → Publish → Select stream.
4. Once published, users can see the app but cannot edit the base version.

### Duplicate vs Publish

- **Duplicate**: creates a personal copy you can edit.
- **Publish**: shares the original (or a copy) to a stream. Owner retains edit rights.

### Community Sheets

Regular users (not app owners) can create **private sheets** and optionally **publish them** to the community area of the app for other users to see without the owner needing to do anything.

```
Private sheet → Published (community) sheet → Approved (owner adds to app) sheet
```

### Reload Scheduling

Apps in Qlik Sense Enterprise are reloaded via **Tasks** in the QMC:
- Sequential tasks
- Trigger-based (on completion of another task)
- Time-based schedule
- Event-based

---

## Storytelling and Snapshots

### Snapshots

A snapshot is a static image of a visualisation at a point in time. Snapshots do NOT update when data reloads.

**Uses:**
- Preserve a state before selections change.
- Use in a data story to illustrate a finding.
- Annotate with text overlays.

### Creating a Story

1. Navigate to "Storytelling" mode.
2. Add slides.
3. Drag snapshots or live sheets (embedded sheets) onto slides.
4. Add text boxes, shapes, and images.
5. Annotate key findings with callouts.

### Embedded Sheets in Stories

Unlike snapshots, embedded sheets in a story remain live (connected to current data). Useful when the story is presented with fresh data each time.

---

## On-Demand Apps

On-demand apps enable analysis of large datasets without loading all data into memory. Users make selections in a "selection app" to define a subset, then generate an "on-demand app" containing only that subset.

### Components

1. **Selection App**: Regular Qlik Sense app with aggregated data. User makes selections to narrow scope.
2. **Template App**: Contains the detailed data load script with binding expressions.
3. **On-Demand App**: Generated dynamically when user triggers creation.

### Binding Expressions in Template Apps

```qlik
// Template app script uses binding expressions
// These are substituted with actual selected values when the app is generated
SELECT * FROM Orders
WHERE CustomerID IN ($(ods_CustomerID))
  AND Year = $(ods_Year);
```

---

## Direct Discovery

Direct Discovery allows Qlik Sense to query large databases on-demand rather than loading all data into memory.

### Field Types

| Type | Description |
|------|-------------|
| `DIMENSION` | Fields used as dimensions; loaded into memory |
| `MEASURE` | Fields used in aggregations; queried from source |
| `DETAIL` | Additional fields accessible in detail tables |

### Differences from In-Memory

- Slower for interactive use (each selection triggers a database query).
- Suitable for very large datasets that cannot fit in RAM.
- Limited chart type support.
- No offline access.
- Sorting and chart inter-record functions not available for MEASURE fields.

```qlik
DIRECT QUERY
    DIMENSION CustomerID, CustomerName, Region
    MEASURE Sales, Quantity
    DETAIL OrderDate, ProductID
FROM large_transactions;
```

---

## Analytic Connections (SSE)

Server-Side Extensions (SSE) allow Qlik Sense to call external calculation engines (Python, R, etc.) from both the data load script and chart expressions.

### Script Usage

```qlik
// Call external function from script
Values: LOAD Rand() as A, Rand() as B AUTOGENERATE 50;

// Call function P.Calculate in plugin, passing fields A and C
Load * Extension P.Calculate(Values{A, C});

// Evaluate an R script
Load A as A_echo, B as B_echo
Extension R.ScriptEval('q;', Values{A, B});

// Use a variable for the script
Load * Extension R.ScriptEval('$(My_R_Script)', Values{A, B});
```

### Chart Usage

```qlik
// In a chart measure
P.PredictSales(Sum(Sales), Count(Orders))
```

---

## Administration and Governance

### Qlik Sense Architecture (Enterprise)

| Component | Role |
|-----------|------|
| QRS (Repository Service) | Central configuration, security rules, app metadata |
| QES (Engine Service) | In-memory analytics engine; handles calculations |
| QPS (Proxy Service) | Authentication, session management, load balancing |
| QSS (Scheduler Service) | Task scheduling and reload execution |
| QDS (Data Connector Service) | Manages data connections |
| NPrinting | Pixel-perfect reporting and distribution |

### Nodes and Deployment

- **Central node**: primary; runs all services.
- **Worker/rim nodes**: additional computation; scale-out for more apps or users.
- **Single-node**: development/small deployments.
- **Multi-node**: production enterprise deployments.

### Licensing

| Type | Description |
|------|-------------|
| Professional | Full access: create, edit, publish, reload |
| Analyser | View and interact only (no editing) |
| Analyser Capacity | Concurrent session-based (not per user) |
| Core | QIX engine API access |

**Tokens**: older licensing model; each user access pass consumes tokens from a pool.

### Security Rules

Security rules govern access to streams, apps, data connections, and other resources. Written in the QMC using the Security Rules editor.

```
// Allow all users access to Published stream
resource.stream.name = "Published" and user.@IsActive = "True"

// Allow group members to publish
resource.hasPrivilege("publish") and user.group = "Publishers"
```

### Managing Data Connections

- Data connections are stored in the QRS.
- Shared connections are available to all apps on the node.
- Personal connections (Desktop) are stored locally.
- Connection security: users need explicit permission to use each connection.

### Tasks and Reload Monitoring

- Schedule reloads via QMC → Tasks → Create task.
- Chain tasks: configure sequential dependencies.
- Monitor via QMC → Tasks → Status.
- Reload logs: QMC → Apps → [App] → Reload history.

### Extensions and Custom Objects

- Extensions are uploaded via QMC → Extensions.
- Only administrators can upload extensions.
- Extensions appear in the chart type picker for all users.

---

## Debugging and Troubleshooting

### Script Debugging

Use the Debug pane in the Data Load Editor:

```
1. Set a breakpoint by clicking the gutter next to the line.
2. Click "Debug script" button.
3. Step through with Step In, Step Over, Step Out.
4. Inspect variable values in the Variables panel.
5. View log output in the Log panel.
```

### Common Script Errors

| Error | Likely Cause |
|-------|-------------|
| "Invalid path" | Missing `lib://` prefix or incorrect connection name |
| "Table not found" | Table referenced before it was loaded, or wrong name |
| "Circular reference" | Two tables create a loop of associations |
| "Synthetic key" | Two tables share more than one field name |
| Statement not terminated | Missing semicolon at end of LOAD or SQL |
| Single quote inside string | Use `''` (double single quote) inside a quoted string |

### Data Model Viewer Diagnostics

In the Data Model Viewer:
- **Orange highlighted tables**: tables associated to the selected table.
- **Dashed border**: loosely coupled table (circular reference detected).
- **`$Syn` tables**: synthetic key tables (should be avoided).

Field statistics in the Preview pane:
- **Density**: percentage of non-NULL values.
- **Subset ratio**: percentage of dimension values that exist in fact table.
- **Has duplicates**: flag for non-unique values.
- **Total distinct values vs Present distinct values**: useful for detecting bad keys.

### Performance Profiling

```qlik
// Log timing of each section
LET vStart = Now();
// ... load operations ...
TRACE Section completed in $(=Interval(Now()-vStart, 'hh:mm:ss'));
```

### Checking for Circular References

```qlik
// Script will warn: "Circular reference detected"
// Look for the loosely coupled table (dashed line) in Data Model Viewer
// Resolution: rename fields or use a link table
```

### Validating Data After Load

```qlik
// After loading, verify counts
LET vSalesRows = NoOfRows('FactSales');
LET vCustRows  = NoOfRows('DimCustomer');
TRACE FactSales has $(vSalesRows) rows;
TRACE DimCustomer has $(vCustRows) rows;

// Verify expected fields exist
LET vFieldCount = NoOfFields('FactSales');
IF vFieldCount < 10 THEN
    TRACE WARNING: FactSales has fewer fields than expected;
END IF;
```

---

## Cookbook Recipes

### Recipe 1: Subroutine for Reusable Table Loading

```qlik
// Define reusable subroutine
SUB LoadQVD(vName)
    [$(vName)]:
    LOAD * FROM 'lib://QVDs/$(vName).qvd' (qvd);
END SUB

// Call for each table
CALL LoadQVD('FactSales')
CALL LoadQVD('DimCustomer')
CALL LoadQVD('DimProduct')
CALL LoadQVD('DimDate')
```

### Recipe 2: Efficient Conditional Script Loading

```qlik
// Use a flag variable to control which sections run
SET vLoadFull = 1;
SET vLoadIncremental = 0;

IF $(vLoadFull) = 1 THEN
    LOAD * FROM 'lib://Source/Sales.csv';
ELSE
    LOAD * FROM 'lib://QVDs/Sales.qvd' (qvd);
END IF;
```

### Recipe 3: Dynamic Date Ranges

```qlik
// Set variables for rolling 13-month window
LET vStartDate = MakeDate(Year(AddMonths(Today(),-13)), Month(AddMonths(Today(),-13)), 1);
LET vEndDate   = Today();

LOAD * FROM transactions.qvd (qvd)
WHERE TransDate >= '$(vStartDate)'
  AND TransDate <= '$(vEndDate)';
```

### Recipe 4: Slowly Changing Dimension via IntervalMatch

```qlik
// Step 1: Load transactions with date
Trans: LOAD TransID, CustomerID, ProductID, TransDate, Qty, Price FROM transactions.qvd (qvd);

// Step 2: Load historical cost rates with intervals
CostHistory:
LOAD ProductID, ValidFrom, ValidTo, CostRate FROM cost_history.qvd (qvd);

// Step 3: Link transaction date to applicable cost interval
Inner Join (Trans)
IntervalMatch(TransDate, ProductID)
LOAD ValidFrom, ValidTo, ProductID
Resident CostHistory;

// Step 4: Join in the rate
Left Join (Trans)
LOAD ProductID, ValidFrom, CostRate
Resident CostHistory;

DROP TABLE CostHistory;
```

### Recipe 5: Loading Data from Multiple CSV Files

```qlik
// Dynamic loading from folder
FOR EACH vFile IN FileList('lib://DataFiles/Sales*.csv')
    LET vYear = SubField(SubField('$(vFile)', '/', -1), '.', 1);
    Sales:
    LOAD *, '$(vYear)' as SourceYear FROM [$(vFile)]
    (txt, delimiter is ',', embedded labels);
NEXT vFile
```

### Recipe 6: Using Concat() to Store Multiple Values in One Cell

```qlik
// In script: concatenate child records into parent
Orders: LOAD OrderID, CustomerID FROM orders.qvd (qvd);

OrderLines:
LOAD OrderID, Concat(ProductName, ', ') as Products
FROM order_lines.qvd (qvd)
GROUP BY OrderID;

LEFT JOIN (Orders) LOAD * Resident OrderLines;
DROP TABLE OrderLines;
```

### Recipe 7: KPI with RAG Status and Conditional Colour

```qlik
// KPI Measure:
Sum(Sales)

// KPI conditional colour (background):
if(Sum(Sales) / Sum(Target) >= 1,
    rgb(0, 160, 0),              // Green — on target
    if(Sum(Sales) / Sum(Target) >= 0.8,
        rgb(255, 165, 0),        // Amber — within 20% of target
        rgb(200, 0, 0)           // Red — more than 20% below target
    )
)

// Label colour (white for readability on dark backgrounds):
white()
```

### Recipe 8: Reference Lines in Gauge Chart

```qlik
// Gauge chart setup:
// Measure: Sum(Sales)
// Under Add-ons → Reference lines:
//   Expression: =Sum(Target)
//   Label: Target
//   Colour: red()
//
// Under Appearance → Presentation:
//   Max: =Sum(Target) * 1.2  (20% above target)
//
// Segments:
//   Segment 1 limit: =Sum(Target)*0.30  — colour: grey
//   Segment 2 limit: =Sum(Target)*0.60  — colour: red
//   Segment 3 limit: =Sum(Target)       — colour: yellow
//   Final segment   — colour: green (with gradient)
```

### Recipe 9: Extended IntervalMatch for Slowly Changing Products

```qlik
// Goal: assign the correct product price to each transaction
// even though prices changed over time

PriceHistory:
LOAD
    ProductID,
    Date(ValidFrom) as ValidFrom,
    Date(if(IsNull(ValidTo), Today(), ValidTo)) as ValidTo,
    Price
FROM price_history.qvd (qvd);

Transactions:
LOAD TransID, ProductID, TransDate, Quantity FROM transactions.qvd (qvd);

// Extended interval match: matches on TransDate AND ProductID
IntervalMatch(TransDate, ProductID)
LOAD ValidFrom, ValidTo, ProductID
Resident PriceHistory;

// Now each transaction has ValidFrom and ValidTo
// Join back to get the Price
Left Join (Transactions)
LOAD ProductID, ValidFrom, Price Resident PriceHistory;
```

### Recipe 10: Associating Persistent Colours to Field Values

```qlik
// In chart: Colour → By dimension → Custom
// For each dimension value, assign a colour:
// In the colour picker, map:
//   'ZA'  → green
//   'UK'  → blue
//   'US'  → red

// Or via expression:
pick(
    match(Country, 'ZA', 'UK', 'US', 'DE'),
    green(), blue(), red(), darkgray()
)
```

### Recipe 11: Smart Search Filter Pattern

```qlik
// Use GetCurrentSelections() in a text box to show active filters
='Active filters: ' & GetCurrentSelections(chr(10), ': ', ', ', 5)

// Button to clear all selections
// Action: Clear selections (all fields)
```

### Recipe 12: Creating a Geo Map from Coordinates

```qlik
// Script: load latitude/longitude
Stores:
LOAD
    StoreID,
    StoreName,
    Latitude,
    Longitude,
    GeoMakePoint(Longitude, Latitude) as Coordinates
FROM stores.csv;

// In chart: Map visualisation
// Layer → Point layer
// Location field: Coordinates
// Size by: Sum(Sales)
// Colour by: Sum(Sales)/Sum(TOTAL Sales)
```

---

*Document compiled from Qlik Sense April 2020 official documentation, Qlik Sense Cookbook (Packt 2015), Learning Qlik Sense — The Official Guide Second Edition (Packt 2015), and Qlik Sense Advanced Data Visualisation (Dr Christopher Ilacqua, Packt 2015). For the most current guidance, consult help.qlik.com.*
