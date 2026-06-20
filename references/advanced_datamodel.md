# Qlik Sense Advanced Patterns and Best Practices — Datamodel


> Split from `advanced_patterns.md`. Companion files share the `advanced_` prefix.


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
