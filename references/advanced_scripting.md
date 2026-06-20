# Qlik Sense Advanced Patterns and Best Practices — Scripting


> Split from `advanced_patterns.md`. Companion files share the `advanced_` prefix.


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
