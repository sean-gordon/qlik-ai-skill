# Qlik Sense Scripting Reference (Backend)

Use this guide to review, write, and validate backend reload scripts in Qlik Sense. All code here runs in the Data Load Editor during a reload — never in chart expressions.

## Companion references

| Reference | Use when |
|-----------|----------|
| [Expression Knowledgebase](expression_knowledgebase.md) | Writing or debugging frontend chart expressions, Set Analysis, Aggr |
| [Functions Reference](functions_reference.md) | Looking up any Qlik function signature, parameters, or examples |
| [Advanced Patterns](advanced_patterns.md) | Implementing incremental loads, link tables, SCD, hierarchy, or complex modelling |
| [Debugging Guide](debugging_guide.md) | Diagnosing script errors, data model issues, or performance problems |
| [Visualisation Guide](visualization_guide.md) | Choosing chart types, applying DAR layout, or styling dashboards |

## Table of Contents

1. [Load Statement Patterns](#1-load-statement-patterns)
2. [Lookups and Mapping (ApplyMap)](#2-lookups-and-mapping-applymap)
3. [Joining and Concatenation](#3-joining-and-concatenation)
4. [Key Scripting Functions](#4-key-scripting-functions)
5. [Date & Time Functions](#5-date--time-functions)
6. [String Functions](#6-string-functions)
7. [Numeric & Mathematical Functions](#7-numeric--mathematical-functions)
8. [Null Handling](#8-null-handling)
9. [Flow Control & Variables](#9-flow-control--variables)
10. [Incremental Reload Patterns](#10-incremental-reload-patterns)
11. [IntervalMatch](#11-intervalmatch)
12. [CrossTable](#12-crosstable)
13. [Section Access (Row-Level Security)](#13-section-access-row-level-security)
14. [Advanced Patterns & Subroutines](#14-advanced-patterns--subroutines)
15. [QVD Optimisation Strategies](#15-qvd-optimisation-strategies)
16. [Data Model Best Practices](#16-data-model-best-practices)

---

## 1. Load Statement Patterns

### Preceding LOAD
Processes the result of the statement below it without creating an intermediate table. Execution order is **bottom to top**.
```qlik
LOAD *,
     Year(OrderDate)    as OrderYear,
     Month(OrderDate)   as OrderMonth,
     Day(OrderDate)     as OrderDay;
LOAD OrderID,
     Date(DateID)       as OrderDate,
     CustomerID,
     SalesAmount
FROM [lib://SourceFiles/Sales.qvd] (qvd);
```

### Resident LOAD
Loads from a table already in Qlik memory. Always drop the source table afterwards to free RAM.
```qlik
TempTable:
LOAD CustomerID, CustomerName, Country
FROM [lib://SourceFiles/Customers.qvd] (qvd);

CustomersZA:
LOAD CustomerID, CustomerName
RESIDENT TempTable
WHERE Country = 'South Africa';

DROP TABLE TempTable;
```

### Autogenerate LOAD
Generates rows programmatically without a data source. Use `IterNo()` as the row counter.
```qlik
LET vStart = Today() - 365;
LET vToday = Today();

Calendar:
LOAD Date($(vStart) + IterNo() - 1, 'YYYY-MM-DD') as DateKey
AUTOGENERATE 1
WHILE $(vStart) + IterNo() - 1 <= $(vToday);
```

### Inline LOAD
Hardcodes data directly in the script. Use for lookup tables, status codes, or mock data.
```qlik
StatusMapping:
LOAD * INLINE [
    StatusCode, StatusLabel, SortOrder
    A,          Active,       1
    I,          Inactive,     2
    P,          Pending,      3
    C,          Cancelled,    4
];
```

### Load From QVD
QVD files are Qlik's native optimised binary format. A pure QVD load (no transforms, WHERE, or JOIN in the same LOAD statement) runs in **optimised mode** — 10–100x faster than SQL.
```qlik
// Optimised mode — Qlik reads QVD directly into RAM
Sales:
LOAD *
FROM [lib://QVDs/Transform/Sales.qvd] (qvd);

// Non-optimised (WHERE clause forces row-by-row evaluation)
SalesZA:
LOAD *
FROM [lib://QVDs/Transform/Sales.qvd] (qvd)
WHERE Country = 'ZA';
```

### Load From SQL Database
```qlik
LIB CONNECT TO 'SQL_Server_DataConnection';

SalesFromDB:
SQL SELECT
    s.OrderID,
    s.CustomerID,
    c.CustomerName,
    s.SalesAmount,
    s.OrderDate
FROM dbo.Sales s
    INNER JOIN dbo.Customers c ON s.CustomerID = c.CustomerID
WHERE s.OrderDate >= '2025-01-01';
```

### Binary Load
Loads the data model from another Qlik app without re-running its script. The `Binary` statement must be the **very first** statement in the script.
```qlik
Binary [lib://Apps/MasterDataApp.qvf];

// Now extend the model from the imported data
ExtendedTable:
LOAD *,
     ApplyMap('Map_Region', CountryCode, 'Unknown') as Region
RESIDENT ImportedSalesTable;
```

---

## 2. Lookups and Mapping (ApplyMap)

Mapping is the fastest lookup mechanism in Qlik. Always prefer it over `JOIN` or `Lookup()`.

**Rules:**
1. Load the mapping table first using the `Mapping` prefix (or `Mapping LOAD`).
2. The mapping table must have **exactly two columns**: key first, value second.
3. Mapping tables are automatically discarded at end of reload — they never appear in the data model.

```qlik
// Step 1: Load mapping table
Map_CustToCountry:
Mapping LOAD
    CustomerID,
    Country
FROM [lib://QVDs/Extract/Customers.qvd] (qvd);

// Step 2: Apply during main load
Orders:
LOAD
    OrderID,
    CustomerID,
    ApplyMap('Map_CustToCountry', CustomerID, 'Unknown') as CustomerCountry,
    SalesAmount
FROM [lib://QVDs/Extract/Orders.qvd] (qvd);
```

> **Warning:** Never assign the ApplyMap output the same name as the key field in the same LOAD statement. `ApplyMap('Map', CustomerID) as CustomerID` causes evaluation conflicts.

### Multi-Column Mapping (Composite Key)
```qlik
// Concatenate to create a composite key string for the map
Map_ProductRegionPrice:
Mapping LOAD
    ProductID & '|' & RegionCode,
    ListPrice
FROM [lib://QVDs/Pricing.qvd] (qvd);

Sales:
LOAD
    OrderID,
    ProductID,
    RegionCode,
    ApplyMap('Map_ProductRegionPrice', ProductID & '|' & RegionCode, 0) as ListPrice
FROM [lib://QVDs/Orders.qvd] (qvd);
```

---

## 3. Joining and Concatenation

### Table Joins
Merges two tables horizontally on a key field. Qlik supports `LEFT JOIN`, `RIGHT JOIN`, `INNER JOIN`, and `OUTER JOIN` (default).

> **Warning:** Joins can cause row multiplication with many-to-many key relationships. Validate row counts after every JOIN.

```qlik
// Extend CustomerTable with email addresses
Left Join (CustomerTable)
LOAD CustomerID,
     ContactEmail
FROM [lib://SourceFiles/Emails.qvd] (qvd);
```

### Table KEEP
Like a JOIN but preserves the star schema — tables remain separate. Rows are filtered based on key intersection without merging columns.
```qlik
LEFT KEEP (Orders)
LOAD CustomerID, CustomerName
RESIDENT Customers;
```

### Concatenation (Vertical Union)
```qlik
// Auto-concatenation: happens automatically when field names match exactly
Sales_2024: LOAD OrderID, SalesAmount FROM [lib://2024/Sales.qvd] (qvd);
Sales_2025: LOAD OrderID, SalesAmount FROM [lib://2025/Sales.qvd] (qvd);
// Result: both load into a single Sales_2024 table automatically

// Forced concatenation: use Concatenate prefix when fields differ
AllSales:
LOAD OrderID, SalesAmount, NULL() as ReturnAmount FROM [lib://2024/Sales.qvd] (qvd);

Concatenate(AllSales)
LOAD OrderID, NULL() as SalesAmount, ReturnAmount FROM [lib://2024/Returns.qvd] (qvd);

// Prevent concatenation with NoConcatenate
NewTable:
NoConcatenate
LOAD OrderID, SalesAmount FROM [lib://2025/Sales.qvd] (qvd);
```

---

## 4. Key Scripting Functions

### Exists(field_name [, expression])
Returns TRUE if the expression value has already been loaded into the specified field in the current reload. Runs during the LOAD's WHERE evaluation.
```qlik
// Load orders only for customers already in the Customers table
Orders:
LOAD OrderID, CustomerID, SalesAmount
FROM [lib://Source/Orders.qvd] (qvd)
WHERE Exists(CustomerID);

// Check against a different value (the expression parameter)
LOAD ProductID, ProductName
FROM [lib://Source/Products.qvd] (qvd)
WHERE Exists(ValidProductID, ProductID); // Check ProductID in ValidProductID field
```

### Peek(field_name [, row_number [, table_name]])
Returns a field value from a previously loaded row. Default row is -1 (last row). Row 0 is the first row.
```qlik
// Running total per customer (requires ORDER BY)
RunningTotal:
LOAD *,
     If(CustomerID = Peek('CustomerID'),
        SalesAmount + Peek('RunningTotal'),
        SalesAmount) as RunningTotal
RESIDENT SourceOrders
ORDER BY CustomerID, OrderDate ASC;
```

### Lookup(field_name, search_field, search_value, table_name)
Searches a loaded table for a value. Slower than `ApplyMap()` — use only when you need to retrieve more context or the mapping table pattern doesn't fit.
```qlik
// Lookup the sales manager for a region from a loaded table
LOAD
    OrderID,
    RegionCode,
    Lookup('ManagerName', 'RegionCode', RegionCode, 'RegionManagerTable') as SalesManager
RESIDENT Orders;
```

### AutoNumber(expression [, sequence_name])
Maps a composite or string key to a unique sequential integer (1, 2, 3…). Dramatically reduces memory usage for composite keys.
```qlik
Sales:
LOAD
    CustomerID,
    DateKey,
    AutoNumber(CustomerID & '|' & DateKey, 'CustomerDate') as CustomerDateKey,
    SalesAmount
FROM [lib://QVDs/Sales.qvd] (qvd);
```

### RecNo() vs RowNo()
| Function | What It Counts | Resets? |
| :--- | :--- | :--- |
| `RecNo()` | Rows from the raw source (before WHERE filter) | Yes, on auto-concatenation |
| `RowNo()` | Rows in the resulting Qlik table (after WHERE filter) | No |

### FieldValue(field_name, row_number)
Returns the nth distinct value of a field already loaded in the data model.
```qlik
// Iterate all distinct values of a field without a Resident load
FOR i = 1 TO FieldValueCount('CountryCode')
    LET vCountry = FieldValue('CountryCode', $(i));
    Trace Processing country: $(vCountry);
NEXT i
```

### FieldValueCount(field_name)
Returns the total count of distinct values for a loaded field. Useful for calibrating `Autogenerate` and loops.

### NoOfTables(), TableName(index), TableFields(table_name), NoOfFields(table_name)
Metadata functions that return information about the current in-memory data model.
```qlik
LET vTotalTables = NoOfTables();
FOR i = 0 TO $(vTotalTables) - 1
    Trace Table $(i): $(=TableName($(i)));
NEXT i
```

### Null() and IsNull()
`Null()` generates an explicit NULL value. `IsNull(expression)` returns TRUE if the expression evaluates to NULL.
```qlik
LOAD
    OrderID,
    If(IsNull(ShippedDate), 'Pending', Text(ShippedDate)) as ShipStatus
FROM [lib://Orders.qvd] (qvd);
```

---

## 5. Date & Time Functions

### Date Interpretation
`Date#(string, format)` interprets a string as a date using the specified format. Always use this when loading dates from text files or non-standard sources.
```qlik
LOAD
    Date#(RawDate, 'DD/MM/YYYY') as OrderDate,
    Timestamp#(RawTimestamp, 'YYYY-MM-DD hh:mm:ss') as CreatedAt
FROM [lib://Source/Orders.csv] (txt);
```

### Date Formatting
`Date(date_number, format)` converts a date serial number back to a formatted string for display.
```qlik
Date(OrderDate, 'DD MMM YYYY')      // "18 Jun 2026"
Date(OrderDate, 'YYYY-MM-DD')       // "2026-06-18"
Month(OrderDate)                    // "Jun"
MonthName(OrderDate)                // "2026-06" (for sorting months correctly)
```

### Date Arithmetic
```qlik
// Days between two dates
DaysBetween(StartDate, EndDate)     as DaysOpen

// Add/subtract time periods
AddMonths(InvoiceDate, 3)           as DueDate
AddYears(ContractStart, 1)          as ContractEnd

// Period boundaries
MonthStart(OrderDate)               as MonthStartDate
MonthEnd(OrderDate)                 as MonthEndDate
QuarterStart(OrderDate)             as QuarterStartDate
YearStart(OrderDate)                as YearStartDate
WeekStart(OrderDate, 1)             as WeekStartMonday  // 1 = Monday start
```

### Comprehensive Date Field Generation (for Calendar tables)
```qlik
LOAD
    DateKey,
    Date(DateKey, 'YYYY-MM-DD')                              as DateLabel,
    Year(DateKey)                                            as Year,
    Month(DateKey)                                           as MonthNum,
    Text(Date(DateKey, 'MMM'))                               as MonthShort,
    Text(Date(DateKey, 'MMMM'))                              as MonthLong,
    Ceil(Month(DateKey) / 3)                                 as QuarterNum,
    'Q' & Ceil(Month(DateKey) / 3)                           as QuarterLabel,
    Year(DateKey) & '-Q' & Ceil(Month(DateKey) / 3)          as YearQuarterLabel,
    (Year(DateKey) * 100) + Month(DateKey)                   as YearMonthSort,
    (Year(DateKey) * 10) + Ceil(Month(DateKey) / 3)          as YearQuarterSort,
    Week(DateKey)                                            as WeekNum,
    WeekYear(DateKey)                                        as WeekYear,
    Weekday(DateKey)                                         as WeekdayNum,      // 0=Mon
    Text(Date(DateKey, 'ddd'))                               as WeekdayShort,
    Text(Date(DateKey, 'dddd'))                              as WeekdayLong,
    If(Weekday(DateKey) >= 5, 1, 0)                          as IsWeekend,
    Day(DateKey)                                             as DayOfMonth,
    DayNumberOfYear(DateKey)                                 as DayOfYear,
    If(DateKey = Today(), 1, 0)                              as IsToday,
    If(Year(DateKey) = Year(Today()), 1, 0)                  as IsCurrentYear,
    If(YearMonthSort = Year(Today())*100+Month(Today()), 1, 0) as IsCurrentMonth
FROM [lib://QVDs/DimDate.qvd] (qvd);
```

### Fiscal Year Handling
```qlik
// Fiscal year starting April 1
LET vFiscalYearStartMonth = 4;

LOAD
    DateKey,
    If(Month(DateKey) >= $(vFiscalYearStartMonth),
       Year(DateKey),
       Year(DateKey) - 1)                                    as FiscalYear,
    Mod(Month(DateKey) - $(vFiscalYearStartMonth) + 12, 12) + 1 as FiscalMonth,
    'Q' & Ceil((Mod(Month(DateKey) - $(vFiscalYearStartMonth) + 12, 12) + 1) / 3)
                                                             as FiscalQuarter
FROM [lib://QVDs/DimDate.qvd] (qvd);
```

---

## 6. String Functions

### Text Manipulation
```qlik
Left(string, n)                     // Left n characters
Right(string, n)                    // Right n characters
Mid(string, start [, length])       // Substring from position
Len(string)                         // Length of string
Upper(string)                       // Uppercase
Lower(string)                       // Lowercase
Proper(string)                      // Title Case
Trim(string)                        // Strip leading/trailing spaces
LTrim(string)                       // Left trim
RTrim(string)                       // Right trim

// Concatenation
string1 & string2                   // Concatenation operator (not +)
string1 & Chr(10) & string2         // With newline (Chr(10))

// Padding
Repeat('0', 5 - Len(Code)) & Code  // Left-pad with zeros to 5 chars (manual)

// Replace / Remove
Replace(string, find, with)         // Replace all occurrences
PurgeChar(string, chars_to_remove)  // Remove all instances of listed chars
KeepChar(string, chars_to_keep)     // Keep only listed chars
SubField(string, delimiter [, n])   // Split delimited string, return nth token
```

### Search & Pattern Matching
```qlik
Index(string, find [, occurrence])  // Position of nth occurrence (0 = not found)
FindOneOf(string, chars)            // Position of first matching character

// Pattern matching (returns 1/0)
WildMatch(string, pattern)          // Case-insensitive wildcard (* and ?)
Match(string, value1, value2, ...)  // Exact match against a list
Mixmatch(string, val1, val2, ...)   // Case-insensitive exact match

// Example: Flag records containing specific patterns
IF WildMatch(ProductCode, 'SA-*', 'ZA-*') THEN ... END IF
```

### Text Interpretation
```qlik
Num(string)                         // Interpret string as number
Num#(string, format)                // Interpret with specific format
Text(expression)                    // Force to text (avoid dual-value issues)
Dual(text_repr, numeric_repr)       // Create dual value (text + sort number)

// Example: Months sort correctly as dual values
Dual(MonthName, MonthNum) as Month  // Displays "Jan" but sorts as 1
```

---

## 7. Numeric & Mathematical Functions

```qlik
// Rounding
Round(number, step)                 // Round to nearest step (e.g., Round(3.7, 1) = 4)
Floor(number [, step])              // Round down
Ceil(number [, step])               // Round up
Frac(number)                        // Fractional part (e.g., Frac(3.7) = 0.7)
Int(number)                         // Integer part (truncate, not round)

// Arithmetic
Abs(number)                         // Absolute value
Mod(dividend, divisor)              // Modulo (remainder)
Power(base, exponent)               // Exponentiation
Sqrt(number)                        // Square root
Log(number)                         // Natural logarithm
Log10(number)                       // Base-10 logarithm
Exp(number)                         // e^number

// Range (across multiple arguments, not aggregation)
RangeMax(v1, v2, ...)               // Maximum of listed values
RangeMin(v1, v2, ...)               // Minimum of listed values
RangeSum(v1, v2, ...)               // Sum of listed values (treats NULL as 0)
RangeAvg(v1, v2, ...)               // Average of listed values

// Statistical
Fractile(expression, percentile)    // Percentile value

// Division safety
Div(numerator, denominator)         // Safe integer division (returns NULL instead of error)
```

---

## 8. Null Handling

Qlik treats NULLs carefully — they do not associate across tables and can break models.

```qlik
// NullAsValue: treat NULLs as a literal value for a field
NullAsValue CustomerID;

// NullAsNull: revert to default NULL behavior (after NullAsValue)
NullAsNull CustomerID;

// Replace NULLs during load
LOAD
    OrderID,
    If(IsNull(Discount), 0, Discount) as Discount,
    Coalesce(ShipDate, OrderDate)      as EffectiveShipDate   // First non-null
FROM ...;
```

---

## 9. Flow Control & Variables

### SET vs. LET
```qlik
SET vText   = Today();      // Stores the literal string "Today()"
LET vValue  = Today();      // Evaluates and stores "2026-06-18"
LET vCalc   = 5 * 3;        // Stores 15
LET vIf     = If(1=1, 'Yes', 'No');  // Stores "Yes"
```

### Loops
```qlik
// FOR / NEXT loop
FOR i = 1 TO 12
    Trace Processing month $(i);
NEXT i

// FOR EACH / NEXT — iterate list values
FOR EACH vFile in FileList('lib://QVDs/Extract/*.qvd')
    LOAD * FROM [$(vFile)] (qvd);
NEXT vFile

// FOR EACH with a static list
FOR EACH vCountry in 'ZA', 'US', 'UK', 'AU'
    LOAD *, '$(vCountry)' as Country
    FROM [lib://Source/$(vCountry)_Sales.qvd] (qvd);
NEXT vCountry

// WHILE loop using Autogenerate
LOAD IterNo() as RowNumber
AUTOGENERATE 1
WHILE IterNo() <= 100;
```

### Conditional Execution
```qlik
IF vReloadType = 'Full' THEN
    LOAD * FROM [lib://QVDs/Full/Sales.qvd] (qvd);
ELSEIF vReloadType = 'Incremental' THEN
    LOAD * FROM [lib://QVDs/Delta/Sales.qvd] (qvd);
ELSE
    Trace Unknown reload type: $(vReloadType);
    EXIT SCRIPT;
END IF
```

### Subroutines (Sub / Call)
```qlik
Sub LogMessage (msg)
    LET _LogTime = Now();
    Trace [$(_LogTime)] $(msg);
    LET _LogTime = Null();
End Sub

Call LogMessage('Starting data load');
```

---

## 10. Incremental Reload Patterns

Incremental reloads only load new or changed records since the last reload. This dramatically reduces reload time for large datasets.

### QVD-Based Incremental Load
```qlik
LET vLastReloadDate = Null();

// Check if QVD exists and read the max date already stored
IF NOT IsNull(QvdCreateTime('lib://QVDs/Transform/Sales.qvd')) THEN
    TempMaxDate:
    LOAD Max(OrderDate) as MaxDate
    FROM [lib://QVDs/Transform/Sales.qvd] (qvd);
    LET vLastReloadDate = Peek('MaxDate', 0, 'TempMaxDate');
    DROP TABLE TempMaxDate;
END IF

// Load new records from source
NewSales:
IF IsNull('$(vLastReloadDate)') THEN
    // First-time full load
    SQL SELECT * FROM dbo.Sales;
ELSE
    SQL SELECT * FROM dbo.Sales WHERE OrderDate > '$(vLastReloadDate)';
END IF

// Reload existing QVD excluding the last day (to catch late arrivals)
OldSales:
LOAD *
FROM [lib://QVDs/Transform/Sales.qvd] (qvd)
WHERE OrderDate < '$(vLastReloadDate)';

// Concatenate — auto-concatenation will merge if fields match
Concatenate(NewSales)
LOAD * RESIDENT OldSales;
DROP TABLE OldSales;

// Store combined result back as the QVD
STORE NewSales INTO [lib://QVDs/Transform/Sales.qvd] (qvd);
DROP TABLE NewSales;
```

### STORE Statement
```qlik
// Store table as QVD (native binary, fastest)
STORE TableName INTO [lib://QVDs/Transform/MyTable.qvd] (qvd);

// Store as CSV
STORE TableName INTO [lib://Exports/Output.csv] (txt);

// Store as TXT with tab delimiter
STORE TableName INTO [lib://Exports/Output.txt] (txt, delimiter is '\t');
```

---

## 11. IntervalMatch

Maps point-in-time values to overlapping intervals. Classic use case: mapping a transaction date to a price period or contract validity window.

```qlik
// Load price periods (intervals)
PricePeriods:
LOAD
    ProductID,
    StartDate,
    EndDate,
    ListPrice
FROM [lib://Source/PricePeriods.qvd] (qvd);

// Load transactions with dates
Transactions:
LOAD OrderID, ProductID, TransactionDate, Quantity
FROM [lib://Source/Orders.qvd] (qvd);

// IntervalMatch: link TransactionDate to StartDate/EndDate intervals
IntervalMatch (TransactionDate, ProductID)
LOAD StartDate, EndDate, ProductID
RESIDENT PricePeriods;
```

---

## 12. CrossTable

Transforms a wide (pivoted) table with multiple column-per-category into a tall (unpivoted) format.

```qlik
// Source: columns Jan, Feb, Mar represent monthly sales
// CrossTable(AttributeField, ValueField, HeaderColumns)
CrossTable(Month, Sales, 1)
LOAD
    ProductID,
    Jan,
    Feb,
    Mar,
    Apr,
    May,
    Jun
FROM [lib://Source/MonthlySales.xlsx] (ooxml, embedded labels, table is Sheet1);
```

---

## 13. Section Access (Row-Level Security)

Controls which data rows each user can see. Must be the first section of any app using security.

**Critical rules:**
1. All keywords and comparison values in Section Access must be **UPPERCASE**.
2. The reduction key field must exist in the main data model (also uppercase).
3. `*` in the reduction field means "access to all values".
4. `OMIT` hides entire columns (fields) from specified users.

```qlik
SECTION ACCESS;
LOAD * INLINE [
    ACCESS, USERID,              REDUCTION_KEY, OMIT
    ADMIN,  INTERNAL\SA_SCHED,   *,
    USER,   DOMAIN\SEAN_GORDON,  ZA,
    USER,   DOMAIN\USER_A,       US,            SALARY
    USER,   DOMAIN\USER_B,       US,
    USER,   DOMAIN\USER_C,       GB,
];

SECTION APPLICATION;

// The reduction key must be capitalized to match Section Access
Sales:
LOAD
    OrderID,
    Upper(Country) as REDUCTION_KEY,
    CustomerName,
    Salary         as SALARY,
    SalesAmount
FROM [lib://QVDs/Sales.qvd] (qvd);
```

### Group-Based Section Access (from a database)
```qlik
SECTION ACCESS;
LIB CONNECT TO 'Security_DB';
SQL SELECT
    UPPER(ACCESS)        as ACCESS,
    UPPER(DOMAIN_USER)   as USERID,
    UPPER(REGION_CODE)   as REDUCTION_KEY
FROM dbo.AppSecurityMatrix
WHERE AppName = 'SalesApp';

SECTION APPLICATION;
```

---

## 14. Advanced Patterns & Subroutines

### Drop All In-Memory Tables
```qlik
LET numTables = NoOfTables();
FOR i = 1 TO $(numTables)
    LET tN = TableName(0);
    DROP TABLE [$(tN)];
NEXT i
```

### Dynamic Calendar Subroutine
```qlik
Sub Calendar (_DateField, _CalendarName, _CalendarPrefix, _CalendarSuffix, _FullCalendar)
    Let _StartTime = Now();
    Let _CalendarName   = If(Len('$(_CalendarName)')=0,   'Calendar',       '$(_CalendarName)');
    Let _CalendarPrefix = If(Len('$(_CalendarPrefix)')=0, '',               '$(_CalendarPrefix)');
    Let _CalendarSuffix = If(Len('$(_CalendarSuffix)')=0, '',               '$(_CalendarSuffix)');
    Let _FullCalendar   = If(Len('$(_FullCalendar)')=0,   1,                0);
    Let _DateField      = PurgeChar(_DateField, '"[]');

    "$(_CalendarName)":
    LOAD
        Distinct [$(_DateField)]                                                         as [$(_DateField)],
        Text(Date([$(_DateField)]))                                                      as [$(_CalendarPrefix)DateText$(_CalendarSuffix)],
        Year([$(_DateField)])                                                             as [$(_CalendarPrefix)Year$(_CalendarSuffix)],
        Week([$(_DateField)]) & '-' & Year([$(_DateField)])                              as [$(_CalendarPrefix)WeekYear$(_CalendarSuffix)],
        Week([$(_DateField)])                                                             as [$(_CalendarPrefix)Week$(_CalendarSuffix)],
        Dual(Date(WeekStart(Date([$(_DateField)])), 'dd MMM') & '-' &
             Date(WeekEnd(Date([$(_DateField)])), 'dd MMM'),
             (Year([$(_DateField)]) * 100) + Week([$(_DateField)]))                      as [$(_CalendarPrefix)WeekText$(_CalendarSuffix)],
        Num(Month([$(_DateField)]))                                                      as [$(_CalendarPrefix)Month$(_CalendarSuffix)],
        Text(Month([$(_DateField)]))                                                     as [$(_CalendarPrefix)MonthTxt$(_CalendarSuffix)],
        Year([$(_DateField)]) & ' ' & Text(Date([$(_DateField)], 'MM'))                 as [$(_CalendarPrefix)Year Month$(_CalendarSuffix)],
        (Year([$(_DateField)]) * 100) + Month(Date([$(_DateField)]))                    as [$(_CalendarPrefix)YearMonth$(_CalendarSuffix)],
        (Year([$(_DateField)]) * 100) + Ceil(Month([$(_DateField)]) / 3)               as [$(_CalendarPrefix)YearQuarter$(_CalendarSuffix)],
        'Q' & Ceil(Month([$(_DateField)]) / 3)                                          as [$(_CalendarPrefix)Quarter$(_CalendarSuffix)],
        (Year([$(_DateField)]) * 100) + Week([$(_DateField)])                           as [$(_CalendarPrefix)YearWeek$(_CalendarSuffix)],
        AutoNumber(MonthStart([$(_DateField)]),        '_MonthSerial')                   as [$(_CalendarPrefix)MonthSerial$(_CalendarSuffix)],
        AutoNumber(QuarterStart([$(_DateField)]),      '_QuarterSerial')                 as [$(_CalendarPrefix)QuarterSerial$(_CalendarSuffix)],
        AutoNumber(WeekYear([$(_DateField)]) & '|' & Week([$(_DateField)]), '_WeekSerial')
                                                                                         as [$(_CalendarPrefix)WeekSerial$(_CalendarSuffix)],
        If(Weekday([$(_DateField)]) >= 5, 1, 0)                                          as [$(_CalendarPrefix)IsWeekend$(_CalendarSuffix)],
        If([$(_DateField)] = Today(), 1, 0)                                              as [$(_CalendarPrefix)IsToday$(_CalendarSuffix)],
        If(Year([$(_DateField)]) = Year(Today()), 1, 0)                                  as [$(_CalendarPrefix)IsCurrentYear$(_CalendarSuffix)]
    ;
    If _FullCalendar = 1 Then
        Load Date(_DateStart + (IterNo()-1), 'YYYY-MM-DD') as [$(_DateField)]
        While (_DateStart + (IterNo()-1) <= _DateStop);
        LOAD
            Floor(Min(FieldValue('$(_DateField)', RecNo()))) as _DateStart,
            Floor(Max(FieldValue('$(_DateField)', RecNo()))) as _DateStop
        AUTOGENERATE FieldValueCount('$(_DateField)');
    Else
        LOAD Num(FieldValue('$(_DateField)', RecNo())) as [$(_DateField)]
        AUTOGENERATE FieldValueCount('$(_DateField)');
    End If

    Let _TotalTime = Round((Now()-_StartTime)*60*60*24, 0.00000000001);
    Trace Calendar created in: $(_TotalTime) seconds;
    Let _StartTime = Null();
    Let _TotalTime = Null();
End Sub

// Call:
Call Calendar('InvoiceDate', 'MasterCalendar', 'Inv_', '', '1');
```

### Generic Load (EAV Pivot)
```qlik
original:
LOAD * INLINE [
    EntityID, Attribute, Value
    A,        Revenue,   1034
    A,        Cost,      4076
    B,        Revenue,   2345
    B,        Cost,      243
];

temp1:
GENERIC LOAD * RESIDENT original;

result:
LOAD Distinct EntityID RESIDENT original;
DROP TABLE original;

TableList:
LOAD TableName($(i)) as Tablename AUTOGENERATE 1
WHERE WildMatch(TableName($(i)), 'temp1.*');

FOR i = 1 TO FieldValueCount('Tablename')
    LET vTable = FieldValue('Tablename', $(i));
    LEFT JOIN (result) LOAD * RESIDENT $(vTable);
    DROP TABLE $(vTable);
NEXT i
DROP TABLE TableList;
```

### Public Holiday Scraper
```qlik
LET vHolidayURL = 'https://www.timeanddate.com/holidays/south-africa';
LET zYearMin = Year(Today()) - 2;
LET zYearMax = Year(Today());

For k = $(zYearMin) to $(zYearMax)
    Holidays:
    LOAD
        Num(Date#("Date" & ' ' & $(k), 'DD MMM YYYY')) as DateKey,
        "Holiday Name",
        "Holiday Type",
        1 as IsHolidayFlag
    FROM [$(vHolidayURL)/$(k)] (html, utf8, embedded labels, table is @1)
    WHERE "Holiday Type" = 'Public Holiday';
Next k
```

### SQL Metadata / Column Discovery
```qlik
SQL SELECT c.name AS ColName, t.name AS TableName
FROM sys.columns c
    JOIN sys.tables t ON c.object_id = t.object_id
WHERE c.name LIKE '%$(vTargetFieldName)%';
```

---

## 15. QVD Optimisation Strategies

| Strategy | Technique |
| :--- | :--- |
| **Optimised mode** | Pure LOAD * FROM file.qvd (no WHERE, no JOIN in same statement) |
| **Key compression** | Use `AutoNumber()` on composite keys before storing |
| **Field reduction** | Only LOAD the fields you need, not `*` from large QVDs |
| **Partition by period** | Separate QVDs per year/month; only reload current period |
| **QVD metadata** | `QvdCreateTime()`, `QvdNoOfRecords()`, `QvdFieldName()` for validation |
| **Avoid redundancy** | Drop helper tables immediately after use |

```qlik
// Validate QVD before loading
IF NOT IsNull(QvdCreateTime('lib://QVDs/Sales.qvd')) THEN
    Trace QVD created: $(=QvdCreateTime('lib://QVDs/Sales.qvd'));
    Trace Records: $(=QvdNoOfRecords('lib://QVDs/Sales.qvd'));
    LOAD * FROM [lib://QVDs/Sales.qvd] (qvd);
ELSE
    Trace QVD not found — running full DB load;
    SQL SELECT * FROM dbo.Sales;
END IF
```

---

## 16. Data Model Best Practices

### 3-Tier QVD Architecture
```
Layer 1 — Extract:     Raw data → Extract QVDs (no transforms)
Layer 2 — Transform:   Business logic, joins, calendar, clean keys → Transform QVDs
Layer 3 — Application: Load transform QVDs directly into app
```

### Synthetic Key Resolution
Synthetic keys (`$Syn` tables in the Data Model Viewer) occur when two tables share more than one common field. Always resolve:

| Resolution | When to Use |
| :--- | :--- |
| Drop/rename one field | The shared field serves no association purpose in one table |
| Composite key with `AutoNumber()` | Both fields must link the tables — combine into a single key |
| Link Table | Complex many-to-many with multiple shared fields |

```qlik
// Option A: Rename to avoid synthetic key
LOAD
    OrderID,
    CustomerID,
    Date(OrderDate) as OrderInvoiceDate  // Renamed from "OrderDate" to clarify role
FROM ...;

// Option B: Composite AutoNumber key
LOAD
    AutoNumber(CustomerID & '|' & ProductID) as CustomerProductKey,
    CustomerID,
    ProductID,
    SalesAmount
FROM ...;
```

### Link Table Pattern (for complex many-to-many schemas)
```qlik
// Instead of linking FactSales directly to both DimCustomer and DimProduct
// through multiple shared fields, create a Link Table

LinkTable:
LOAD DISTINCT
    AutoNumber(CustomerID & '|' & ProductID) as LinkKey,
    CustomerID,
    ProductID
RESIDENT FactSales;

// Now FactSales carries LinkKey only (remove CustomerID, ProductID from Fact)
// DimCustomer links on CustomerID, DimProduct links on ProductID
// through the LinkTable bridge
```
