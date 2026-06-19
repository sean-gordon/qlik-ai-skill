# Qlik Sense Function Reference (Complete)

> Extracted from: *Script syntax and chart functions* (Qlik Sense April 2020), *Qlik Sense Cookbook* (Packt, 2015), and *Qlik Sense Advanced Data Visualisation* (Dr Christopher Ilacqua).
> Language: South African English. Code blocks use `` ```qlik `` for Qlik script, `` ```sql `` for SQL.

## Companion references

| Reference | Use when |
|-----------|----------|
| [Scripting Knowledgebase](scripting_knowledgebase.md) | Writing or reviewing backend load scripts, LOAD/SELECT/JOIN patterns |
| [Expression Knowledgebase](expression_knowledgebase.md) | Writing or debugging frontend chart expressions, Set Analysis, Aggr |
| [Advanced Patterns](advanced_patterns.md) | Implementing incremental loads, link tables, SCD, hierarchy, or complex modelling |
| [Debugging Guide](debugging_guide.md) | Diagnosing script errors, data model issues, or performance problems |
| [Visualisation Guide](visualization_guide.md) | Choosing chart types, applying DAR layout, or styling dashboards |

---

## Table of Contents

1. [Operators](#operators)
2. [Aggregation Functions](#aggregation-functions)
3. [Set Analysis Complete Reference](#set-analysis-complete-reference)
4. [Date and Time Functions](#date-and-time-functions)
5. [String Functions](#string-functions)
6. [Numeric and Mathematical Functions](#numeric-and-mathematical-functions)
7. [Conditional Functions](#conditional-functions)
8. [Counter Functions](#counter-functions)
9. [Inter-Record Functions](#inter-record-functions)
10. [Range Functions](#range-functions)
11. [Financial Functions](#financial-functions)
12. [Formatting Functions](#formatting-functions)
13. [Interpretation Functions](#interpretation-functions)
14. [Colour Functions](#colour-functions)
15. [Mapping Functions](#mapping-functions)
16. [Statistical Distribution Functions](#statistical-distribution-functions)
17. [Ranking Functions](#ranking-functions)
18. [Geospatial Functions](#geospatial-functions)
19. [File Functions](#file-functions)
20. [System Functions](#system-functions)
21. [Table and Field Information Functions](#table-and-field-information-functions)
22. [Trigonometric and Hyperbolic Functions](#trigonometric-and-hyperbolic-functions)
23. [Logical Functions](#logical-functions)
24. [NULL Functions](#null-functions)
25. [Synthetic Dimension Functions](#synthetic-dimension-functions)
26. [Field and Selection Functions (Chart Only)](#field-and-selection-functions-chart-only)
27. [Script Prefixes Reference](#script-prefixes-reference)
28. [Script Control Statements](#script-control-statements)
29. [System Variables Reference](#system-variables-reference)

---

## Operators

### Arithmetic Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `3 + 4` → `7` |
| `-` | Subtraction | `10 - 4` → `6` |
| `*` | Multiplication | `3 * 4` → `12` |
| `/` | Division | `12 / 4` → `3` |

### Relational Operators

| Operator | Description | Notes |
|----------|-------------|-------|
| `<` | Less than | Numeric or string comparison |
| `<=` | Less than or equal | |
| `>` | Greater than | |
| `>=` | Greater than or equal | |
| `=` | Equal | Case insensitive for strings |
| `<>` or `!=` | Not equal | |

**String ordering:** `' 2' follows '1 '` returns `FALSE` (ASCII space < digit). `' 2' follows ' 1'` returns `TRUE`.

### String Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `&` | String concatenation | `'abc' & 'xyz'` → `'abcxyz'` |
| `like` | Wildcard string comparison | `'abcd' like 'a?c*'` → `True (-1)` |

Wild cards: `*` = any number of characters; `?` = one character.

### Bit Operators

| Operator | Description |
|----------|-------------|
| `BitAnd(x, y)` | Bitwise AND |
| `BitOr(x, y)` | Bitwise OR |
| `BitXor(x, y)` | Bitwise XOR |
| `BitNot(x)` | Bitwise NOT |
| `>>` | Arithmetic right shift |
| `<<` | Arithmetic left shift |

### Logical Operators

| Operator | Description |
|----------|-------------|
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |
| `xor` | Exclusive OR |

---

## Aggregation Functions

> Aggregation functions can be used in chart expressions and (most) in data load scripts with a `GROUP BY` clause.
> In chart expressions, use `SetExpression`, `TOTAL`, and `DISTINCT` qualifiers.

### Common Chart Aggregation Syntax

```qlik
FunctionName([{SetExpression}] [DISTINCT] [TOTAL [<fld {,fld}>]] expr [, rank])
```

### Basic Aggregation Functions

#### Sum

Calculates the total of values.

**Script syntax:** `Sum([DISTINCT] expression)`
**Chart syntax:** `Sum([{SetExpression}] [DISTINCT] [TOTAL [<fld{,fld}>]] expr)`
**Return type:** numeric

```qlik
// Script
LOAD ArtNo, Sum(TransAmount) as Total GROUP BY ArtNo;

// Chart
Sum({$<Year={2024}>} Sales)
Sum(TOTAL Sales)
Sum(DISTINCT Amount)
```

#### Count

Counts records.

**Script syntax:** `Count([DISTINCT] expression)` or `Count(*)`
**Chart syntax:** `Count([{SetExpression}] [DISTINCT] [TOTAL [<fld{,fld}>]] expr)`
**Return type:** integer

```qlik
Count(CustomerID)          // count non-null values
Count(DISTINCT CustomerID) // count unique values
Count(*)                   // count all records
```

#### Avg

Returns the arithmetic mean.

**Script syntax:** `Avg([DISTINCT] expression)`
**Chart syntax:** `Avg([{SetExpression}] [DISTINCT] [TOTAL [<fld{,fld}>]] expr)`
**Return type:** numeric

```qlik
Avg(Sales)
Avg(TOTAL Sales)   // average across all rows, ignoring dimension
```

#### Max and Min

Return the highest or lowest value respectively. An optional `rank` argument returns the nth highest/lowest value.

**Script syntax:** `Max(expr [, rank])` / `Min(expr [, rank])`
**Chart syntax:** `Max([{SetExpression}] [TOTAL [<fld{,fld}>]] expr [, rank])`
**Return type:** numeric (dual for text-capable forms)

```qlik
Max(UnitSales)          // highest value
Max(UnitSales, 2)       // second-highest value
Min({1} TOTAL UnitSales)// min ignoring selection and dimension
```

#### Only

Returns a value only when there is exactly one distinct value in the aggregation; otherwise returns NULL.

**Script syntax:** `Only(expression)`
**Chart syntax:** `Only([{SetExpression}] [DISTINCT] [TOTAL [<fld{,fld}>]] expr)`
**Return type:** dual

```qlik
Only(Region)   // returns region name if all rows have same region, else NULL
```

#### Mode

Returns the most commonly occurring value. Returns NULL if two values tie.

**Script syntax:** `Mode(expression)`
**Chart syntax:** `Mode({[SetExpression] [TOTAL [<fld{,fld}>]]} expr)`
**Return type:** dual

```qlik
Mode(Product)  // most frequently sold product
```

#### FirstSortedValue

Returns the value of `expression` corresponding to the lowest `sort_weight`. Prepend a minus sign to get the highest.

**Script syntax:** `FirstSortedValue([DISTINCT] value, sort_weight [, rank])`
**Chart syntax:** `FirstSortedValue([{SetExpression}] [DISTINCT] [TOTAL [<fld{,fld}>]] value, sort_weight [, rank])`
**Return type:** dual

```qlik
// Name of product with lowest unit price
FirstSortedValue(Product, UnitPrice)

// Name of product with highest unit price
FirstSortedValue(Product, -UnitPrice)

// Second-cheapest product
FirstSortedValue(Product, UnitPrice, 2)
```

#### Concat

Aggregates string values with a delimiter.

**Script syntax:** `Concat([DISTINCT] string [, delimiter [, sort_weight]])`
**Chart syntax:** `Concat([{SetExpression}] [DISTINCT] [TOTAL [<fld{,fld}>]] string [, delimiter [, sort_weight]])`
**Return type:** string

```qlik
Concat(ProductName, ', ')           // comma-separated list
Concat(DISTINCT ProductName, ', ')  // unique values only
```

### Counter Aggregation Functions

#### Count (unique variants)

| Function | Description |
|----------|-------------|
| `Count(expr)` | Count non-NULL values |
| `Count(DISTINCT expr)` | Count distinct non-NULL values |
| `Count(*)` | Count all rows including NULLs |
| `NumericCount(expr)` | Count numeric values only |
| `TextCount(expr)` | Count text values only |
| `NullCount(expr)` | Count NULL values |
| `MissingCount(expr)` | Count missing (NULL or blank) values |

```qlik
NumericCount(Value)    // how many numeric entries
TextCount(Value)       // how many text entries
NullCount(Value)       // how many NULLs
```

### Statistical Aggregation Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `Stdev` | `Stdev([DISTINCT] expr)` | Standard deviation (sample) |
| `Skew` | `Skew([DISTINCT] expr)` | Skewness of distribution |
| `Kurtosis` | `Kurtosis([DISTINCT] expr)` | Kurtosis of distribution |
| `Correl` | `Correl(x_expr, y_expr)` | Pearson correlation coefficient |
| `Fractile` | `Fractile(expr, fraction)` | Percentile/fractile value |
| `IRR` | `IRR(expr)` | Internal rate of return |
| `NPV` | `NPV(discount_rate, expr)` | Net present value |
| `XIRR` | `XIRR(value, date)` | IRR for non-periodic cash flows |
| `XNPV` | `XNPV(discount_rate, value, date)` | NPV for non-periodic cash flows |

```qlik
Stdev(Sales)                   // standard deviation of sales
Fractile(Sales, 0.9)           // 90th percentile
Correl(UnitSales, UnitPrice)   // correlation between two fields
```

### String Aggregation Functions

| Function | Description |
|----------|-------------|
| `MaxString(expr)` | Last value in text sort order |
| `MinString(expr)` | First value in text sort order |
| `Concat(string, delim)` | Concatenate values with delimiter |

### Aggr — Nested Aggregation

`Aggr()` creates a virtual table by aggregating an expression over one or more dimensions. This enables nested aggregations.

**Syntax:** `Aggr({[SetExpression]} [DISTINCT] [NODISTINCT] expr, dim1 [, dim2...])`

```qlik
// Average of per-customer totals
Avg(Aggr(Sum(Sales), CustomerID))

// Count customers above threshold
Count(Aggr(If(Sum(Sales) > 10000, CustomerID), CustomerID))

// Rolling 12-month sum using structured parameters (with sort order)
Sum(Aggr(
    RangeSum(Above(Sum(Sales), 0, 12)),
    (Year, (Numeric, Ascending)),
    (Month, (Numeric, Ascending))
))
```

**Structured parameters:** `(FieldName, (SortType, SortOrder))` where SortType is `Numeric` or `Text`, and SortOrder is `Ascending` or `Descending`.

---

## Set Analysis Complete Reference

Set analysis allows expressions to ignore or override current user selections by defining alternative sets of records.

### Set Identifier Reference

| Identifier | Meaning |
|------------|---------|
| `1` | All records (ignore all selections) |
| `$` | Current selection (default) |
| `$N` | Nth previous bookmark/selection state |
| `$_N` | Nth previous selection in field |
| `bookmark_id` | Named or ID-based bookmark |

### Set Operators

| Operator | Meaning |
|----------|---------|
| `+` | Union |
| `-` | Exclusion (difference) |
| `*` | Intersection |
| `/` | Symmetric difference |

### Assignment Operators in Modifiers

| Operator | Meaning |
|----------|---------|
| `=` | Replace selection |
| `+=` | Add to current selection (union) |
| `-=` | Remove from current selection |
| `*=` | Intersect with current selection |
| `/=` | Symmetric difference with current |

### Full Syntax (Backus-Naur Form)

```
set_expression ::= { set_entity { set_operator set_entity } }
set_entity     ::= set_identifier [ set_modifier ]
set_identifier ::= 1 | $ | $N | $_N | bookmark_id | bookmark_name
set_operator   ::= + | - | * | /
set_modifier   ::= < field_selection {, field_selection } >
field_selection::= field_name [ = | += | -= | *= | /= ] element_set_expression
element_set    ::= [ field_name ] | { element_list } | element_function
element_list   ::= element { , element }
element_function::= ( P | E ) ( [ set_expression ] [ field_name ] )
element        ::= field_value | " search_mask "
```

### Common Set Analysis Patterns

```qlik
// All records, ignore selections
Sum({1} Sales)

// Current year only
Sum({$<Year={2024}>} Sales)

// Current selection but remove Year filter
Sum({$<Year=>} Sales)

// Current selection but with new year selection
Sum({$<Year={2023}, Region={'ZA'}>} Sales)

// Previous year relative to selection
Sum({$<Year={$(=Max(Year)-1)}>} Sales)

// Using variable for dynamic year
Sum({$<Year={$(#vLastYear)}>} Sales)

// Union: add specific products to selected
Sum({$<Product += {OurProduct1, OurProduct2}>} Sales)

// Exclude specific year even if selected
Sum({$<Year -= {2000}>} Sales)

// Wildcard: all years starting with 20
Sum({$<Year={"20*"}>} Sales)

// Range search: years 1979 to 2003
Sum({$<Year={">1978<2004"}>} Sales)

// Customers who bought a specific product
Sum({$<Customer = P({1<Product={'Shoe'}>} Customer)>} Sales)

// Customers who never bought that product
Sum({$<Customer = E({1<Product={'Shoe'}>})>} Sales)

// Customers with prior-year sales > 1M
Sum({$<Customer={"=Sum({1<Year={$(=Max(Year)-1)}>} Sales) > 1000000"}>} Sales)

// Set operator: combine two sets
Sum({$<Year={'2022'}> + $<Year={'2023'}>} Sales)

// Intersection: years selected AND in a specific range
Sum({$<Year = Year * {">2019<2025"}>} Sales)
```

### Element Functions: P() and E()

`P(set, field)` — possible (non-excluded) values of `field` given `set`.
`E(set, field)` — excluded values of `field` given `set`.

```qlik
// Suppliers who also appear as customers
Sum({$<Customer = P({1<Product={'Shoe'}>} Supplier)>} Sales)
```

> **Warning:** P() and E() only work on *natural sets* (sets representable by a simple selection). Using them on non-natural sets such as `{1-$}` can return unexpected results.

---

## Date and Time Functions

### Key Date Format Variables (SET in script)

```qlik
SET DateFormat='DD/MM/YYYY';
SET TimeFormat='hh:mm:ss';
SET TimestampFormat='DD/MM/YYYY hh:mm:ss[.fff]';
SET FirstWeekDay=0;      // 0=Monday, 6=Sunday
SET BrokenWeeks=0;       // 0=ISO weeks, 1=non-ISO
SET ReferenceDay=4;      // minimum days in first ISO week
SET FirstMonthOfYear=1;  // fiscal year start month
```

### Date Extraction Functions

| Function | Syntax | Return | Example |
|----------|--------|--------|---------|
| `year` | `year(date)` | integer | `year('2024-06-15')` → `2024` |
| `month` | `month(date)` | dual (name + 1-12) | `month('2024-06-15')` → `Jun` |
| `day` | `day(date)` | integer | `day('2024-06-15')` → `15` |
| `hour` | `hour(timestamp)` | integer | `hour('09:14:36')` → `9` |
| `minute` | `minute(timestamp)` | integer | `minute('09:14:36')` → `14` |
| `second` | `second(timestamp)` | integer | `second('09:14:36')` → `36` |
| `week` | `week(date[, firstweekday[, brokenweeks]])` | integer | `week('2024-01-15')` → `3` |
| `weekday` | `weekday(date)` | integer 0-6 | `weekday('2024-06-15')` → `5` (Sat) |
| `weekyear` | `weekyear(date)` | integer | ISO week year |
| `quarter` | — | use `Ceil(Month(date)/3)` | |

### Date Construction Functions

#### makedate

```qlik
MakeDate(YYYY [, MM [, DD]])
// Returns dual date value
MakeDate(2024)         // 2024-01-01
MakeDate(2024, 6)      // 2024-06-01
MakeDate(2024, 6, 15)  // 2024-06-15
```

#### maketime

```qlik
MakeTime(hh [, mm [, ss]])
MakeTime(22)         // 22:00:00
MakeTime(22, 30)     // 22:30:00
MakeTime(22, 30, 45) // 22:30:45
```

#### makeweekdate

```qlik
MakeWeekDate(YYYY [, WW [, D]])
// D: 0=Monday ... 6=Sunday
MakeWeekDate(2024, 6)    // first day of week 6 of 2024
MakeWeekDate(2024, 6, 6) // Sunday of week 6 of 2024
```

### Period Boundary Functions

All functions below accept an optional `period_no` argument (negative = prior period, positive = future period).

#### Year boundaries

| Function | Syntax | Returns |
|----------|--------|---------|
| `yearstart` | `YearStart(date [, period_no [, first_month_of_year]])` | First millisecond of year |
| `yearend` | `YearEnd(date [, period_no [, first_month_of_year]])` | Last millisecond of year |
| `yearname` | `YearName(date [, period_no [, first_month_of_year]])` | Display year string |

```qlik
YearStart('15/06/2024')        // returns 01/01/2024
YearEnd('15/06/2024')          // returns 31/12/2024 23:59:59
YearEnd('15/06/2024', -1)      // returns 31/12/2023 23:59:59
YearStart('15/06/2024', 0, 4)  // fiscal year starting April → 01/04/2024
```

#### Quarter boundaries

| Function | Syntax | Returns |
|----------|--------|---------|
| `quarterstart` | `QuarterStart(date [, period_no [, first_month_of_year]])` | Start of quarter |
| `quarterend` | `QuarterEnd(date [, period_no [, first_month_of_year]])` | End of quarter |
| `quartername` | `QuarterName(date [, period_no [, first_month_of_year]])` | Display e.g. "Q2 2024" |

#### Month boundaries

| Function | Syntax | Returns |
|----------|--------|---------|
| `monthstart` | `MonthStart(date [, period_no])` | First millisecond of month |
| `monthend` | `MonthEnd(date [, period_no])` | Last millisecond of month |
| `monthname` | `MonthName(date [, period_no])` | Display e.g. "Jun 2024" |

```qlik
MonthEnd('19/02/2024')      // 29/02/2024 23:59:59
MonthEnd('19/02/2024', -1)  // 31/01/2024 23:59:59
MonthEnd('19/02/2024', 4)   // 30/06/2024 23:59:59
```

#### Multi-month periods (bi-month, quarter, tertial, half-year)

```qlik
MonthsStart(n_months, date [, period_no [, first_month_of_year]])
MonthsEnd(n_months, date [, period_no [, first_month_of_year]])
MonthsName(n_months, date [, period_no [, first_month_of_year]])
```

`n_months` must be 1, 2, 3, 4, or 6.

```qlik
MonthsEnd(3, '15/06/2024')       // end of Q2 → 30/06/2024 23:59:59
MonthsEnd(6, '15/06/2024')       // end of H1 → 30/06/2024 23:59:59
MonthsName(3, '15/06/2024')      // 'Apr-Jun 2024'
MonthsName(4, '19/10/2024', -1)  // 'May-Aug 2024'
```

#### Week boundaries

| Function | Syntax | Returns |
|----------|--------|---------|
| `weekstart` | `WeekStart(date [, period_no [, first_week_day]])` | First millisecond of week |
| `weekend` | `WeekEnd(date [, period_no [, first_week_day]])` | Last millisecond of week |
| `weekname` | `WeekName(date [, period_no [, first_week_day]])` | Display e.g. "2024/24" |

#### Day boundaries

| Function | Syntax | Returns |
|----------|--------|---------|
| `daystart` | `DayStart(timestamp [, period_no [, day_fraction]])` | Midnight start of day |
| `dayend` | `DayEnd(timestamp [, period_no [, day_fraction]])` | End of day |
| `dayname` | `DayName(timestamp [, period_no [, day_fraction]])` | Display date string |

#### Lunar week functions (Qlik proprietary — 7-day weeks from Jan 1)

| Function | Syntax |
|----------|--------|
| `lunarweekstart` | `LunarWeekStart(date [, period_no [, first_week_day]])` |
| `lunarweekend` | `LunarWeekEnd(date [, period_no [, first_week_day]])` |
| `lunarweekname` | `LunarWeekName(date [, period_no [, first_week_day]])` |

```qlik
LunarWeekEnd('12/01/2024')     // 14/01/2024 23:59:59
LunarWeekEnd('12/01/2024', -1) // 07/01/2024 23:59:59
```

### In-Period Functions

Return `-1` (True) or `0` (False).

| Function | Syntax | Checks |
|----------|--------|--------|
| `inyear` | `InYear(date, base_date, period_no [, first_month])` | Same year |
| `inyeartodate` | `InYearToDate(date, base_date, period_no [, first_month])` | Year-to-date |
| `inquarter` | `InQuarter(date, base_date, period_no [, first_month])` | Same quarter |
| `inquartertodate` | `InQuarterToDate(date, base_date, period_no [, first_month])` | QTD |
| `inmonth` | `InMonth(date, base_date, period_no)` | Same month |
| `inmonths` | `InMonths(n_months, date, base_date, period_no [, first_month])` | Same n-month period |
| `inmonthtodate` | `InMonthToDate(date, base_date, period_no)` | MTD |
| `inweek` | `InWeek(date, base_date, period_no [, first_week_day])` | Same ISO week |
| `inweektodate` | `InWeekToDate(date, base_date, period_no [, first_week_day])` | Week-to-date |
| `inday` | `InDay(timestamp, base_timestamp, period_no [, day_start])` | Same day |
| `indaytotime` | `InDayToTime(timestamp, base_timestamp, period_no [, day_start])` | Day-to-time |
| `inlunarweek` | `InLunarWeek(date, base_date, period_no [, first_week_day])` | Same lunar week |
| `inlunarweektodate` | `InLunarWeekToDate(date, base_date, period_no [, first_week_day])` | Lunar WTD |

```qlik
// Load only records from current year
LOAD * FROM data.csv WHERE InYear(TransDate, Today(), 0);

// YTD sales (in chart)
Sum({$<Date = {"=InYearToDate(Date, Today(), 0)"}>} Sales)
```

### Date Arithmetic Functions

#### addmonths

```qlik
AddMonths(startdate, n [, mode])
// Adds n months; mode=0 (default) end-of-month-aware
AddMonths('31/01/2024', 1)   // 29/02/2024
AddMonths('31/01/2024', -1)  // 31/12/2023
```

#### addyears

```qlik
AddYears(startdate, n)
AddYears('28/02/2024', 1)  // 28/02/2025
```

#### networkdays

```qlik
NetworkDays(start_date, end_date [, holiday])
// Returns working days between dates (Mon-Fri), excluding holidays
NetworkDays('01/06/2024', '30/06/2024')
NetworkDays('01/06/2024', '30/06/2024', '10/06/2024')
```

#### age

```qlik
Age(timestamp, date_of_birth)
// Returns completed years of age
Age(Today(), '15/06/1990')
```

#### daystart / dayend

```qlik
DayStart('2024-06-15 14:30:00')  // 2024-06-15 00:00:00
DayEnd('2024-06-15 14:30:00')    // 2024-06-15 23:59:59
```

#### firstworkdate / lastworkdate

```qlik
FirstWorkDate(end_date, no_of_workdays [, holiday])
LastWorkDate(start_date, no_of_workdays [, holiday])
```

#### setdateyear / setdateyearmonth

```qlik
SetDateYear(date, year)       // replace year in date
SetDateYearMonth(date, year, month) // replace year and month
```

#### now / today / GMT / UTC / localtime

```qlik
Now([timer_mode])      // current timestamp, timer_mode: 0=reload time, 1=current
Today([timer_mode])    // current date
GMT()                  // Greenwich Mean Time
UTC()                  // UTC timestamp
LocalTime([timezone [, ignoreDST]])
```

#### DayLightSaving

```qlik
DayLightSaving()   // returns True if daylight saving is active
```

#### timezone

```qlik
TimeZone()   // returns name of local timezone
```

#### converttolocaltime

```qlik
ConvertToLocalTime(timestamp [, place [, ignore_dst]])
```

#### daynumberofquarter / daynumberofyear

```qlik
DayNumberOfQuarter(date [, first_month_of_year])
DayNumberOfYear(date [, first_month_of_year])
```

---

## String Functions

All string functions work in both script and chart expressions unless noted otherwise.

### Overview Table

| Function | Syntax | Returns | Example |
|----------|--------|---------|---------|
| `Capitalize` | `Capitalize(text)` | string | `Capitalize('hello world')` → `'Hello World'` |
| `Chr` | `Chr(int)` | string | `Chr(65)` → `'A'` |
| `Evaluate` | `Evaluate(expr_text)` | dual | Script only. `Evaluate('5*8')` → `'40'` |
| `FindOneOf` | `FindOneOf(text, char_set [, count])` | integer | `FindOneOf('my text','et')` → `4` |
| `Hash128` | `Hash128(expr {, expr})` | 22-char string | `Hash128('abc','xyz')` |
| `Hash160` | `Hash160(expr {, expr})` | 27-char string | |
| `Hash256` | `Hash256(expr {, expr})` | 43-char string | |
| `Index` | `Index(text, substring [, count])` | integer | `Index('abcabc','b',2)` → `5` |
| `KeepChar` | `KeepChar(text, keep_chars)` | string | `KeepChar('a1b2c3','123')` → `'123'` |
| `Left` | `Left(text, count)` | string | `Left('abcdef',3)` → `'abc'` |
| `Len` | `Len(text)` | integer | `Len('Peter')` → `5` |
| `Lower` | `Lower(text)` | string | `Lower('HELLO')` → `'hello'` |
| `LTrim` | `LTrim(text)` | string | `LTrim(' abc')` → `'abc'` |
| `Mid` | `Mid(text, start [, count])` | string | `Mid('abcdef',3,2)` → `'cd'` |
| `Ord` | `Ord(text)` | integer | `Ord('A')` → `65` |
| `PurgeChar` | `PurgeChar(text, remove_chars)` | string | `PurgeChar('a1b2','12')` → `'ab'` |
| `Repeat` | `Repeat(text [, count])` | string | `Repeat('*',4)` → `'****'` |
| `Replace` | `Replace(text, from_str, to_str)` | string | `Replace('abccde','cc','xyz')` → `'abxyzde'` |
| `Right` | `Right(text, count)` | string | `Right('abcdef',3)` → `'def'` |
| `RTrim` | `RTrim(text)` | string | `RTrim('abc ')` → `'abc'` |
| `SubField` | `SubField(text, delimiter [, field_no])` | string | `SubField('a;b;c',';',2)` → `'b'` |
| `SubStringCount` | `SubStringCount(text, substring)` | integer | `SubStringCount('abcabc','ab')` → `2` |
| `TextBetween` | `TextBetween(text, delim1, delim2 [, n])` | string | `TextBetween('<abc>','<','>')` → `'abc'` |
| `Trim` | `Trim(text)` | string | `Trim(' abc ')` → `'abc'` |
| `Upper` | `Upper(text)` | string | `Upper('hello')` → `'HELLO'` |

### SubField — Key Behaviour

When `field_no` is omitted in a LOAD statement, **one full record is generated per substring**. If multiple SubField calls exist in the same LOAD, the Cartesian product of all combinations is created.

```qlik
// Split full name into first and surname
LOAD
    Name,
    SubField(Name, ' ', 1) as FirstName,
    SubField(Name, ' ', -1) as Surname
FROM names.csv;

// Generate multiple rows from comma-separated list
LOAD DISTINCT
    Instrument,
    SubField(Player, ',') as Player,
    SubField(Project, ',') as Project
FROM instruments.csv;
```

### Index — Practical Patterns

```qlik
// Extract year from date string '1997-07-14'
Left(Date, Index(Date, '-') - 1)             // → '1997'

// Extract month part
Mid(Date, Index(Date, '-', 2) - 2, 2)        // → '07'

// Check if string contains substring
Index(ProductName, 'Export') > 0              // True if found
```

---

## Numeric and Mathematical Functions

### General Numeric Functions

| Function | Syntax | Description | Example |
|----------|--------|-------------|---------|
| `Abs` | `Abs(x)` | Absolute value | `Abs(-5)` → `5` |
| `BitCount` | `BitCount(n)` | Count set bits | `BitCount(255)` → `8` |
| `Ceil` | `Ceil(x [, step [, offset]])` | Round up | `Ceil(1.1)` → `2` |
| `Combin` | `Combin(n, k)` | Combinations (n choose k) | `Combin(5,2)` → `10` |
| `Div` | `Div(x, y)` | Integer division | `Div(7,2)` → `3` |
| `Even` | `Even(x)` | Round to nearest even | `Even(3)` → `4` |
| `Fabs` | `Fabs(x)` | Floating-point absolute value | |
| `Fact` | `Fact(n)` | Factorial | `Fact(5)` → `120` |
| `Floor` | `Floor(x [, step [, offset]])` | Round down | `Floor(1.9)` → `1` |
| `Fmod` | `Fmod(x, y)` | Floating-point modulo | `Fmod(7.5, 2)` → `1.5` |
| `Frac` | `Frac(x)` | Fractional part | `Frac(2.7)` → `0.7` |
| `Mod` | `Mod(x, y)` | Integer modulo (always non-negative) | `Mod(7,3)` → `1` |
| `Odd` | `Odd(x)` | Round to nearest odd | `Odd(4)` → `5` |
| `Permut` | `Permut(n, k)` | Permutations | `Permut(5,2)` → `20` |
| `Round` | `Round(x [, step [, offset]])` | Round to nearest step | `Round(1.1,1,0.5)` → `1.5` |
| `Sign` | `Sign(x)` | Returns -1, 0, or 1 | `Sign(-5)` → `-1` |

### Exponential and Logarithmic

| Function | Syntax | Description |
|----------|--------|-------------|
| `Exp` | `Exp(x)` | e raised to the power x |
| `Log` | `Log(x)` | Natural logarithm |
| `Log10` | `Log10(x)` | Base-10 logarithm |
| `Pow` | `Pow(x, y)` | x raised to power y |
| `Sqrt` | `Sqrt(x)` | Square root |
| `Sqr` | `Sqr(x)` | Square (x²) |

### Random

```qlik
Rand()   // random number between 0 and 1
```

---

## Conditional Functions

### alt

Returns the first parameter with a valid numeric representation; otherwise returns the last parameter. Useful for handling NULLs and trying multiple date formats.

```qlik
alt(expr1 [, expr2, expr3, ...], else)

// Try multiple date formats
alt(
    date#(dat, 'YYYY/MM/DD'),
    date#(dat, 'MM/DD/YYYY'),
    date#(dat, 'MM/DD/YY'),
    'No valid date'
)

// Replace NULL with zero
alt(Sales, 0)
```

### if

```qlik
if(condition, then [, else])

if(Amount >= 0, 'OK', 'Alarm')
if(Incidents >= 10, 'Critical', if(Incidents >= 1, 'Warning', 'OK'))
```

### class

Assigns a value to a class interval. Returns a dual value with `a<=x<b` as text.

```qlik
class(expression, interval [, label [, offset]])

class(var, 10)         // '0<=x<10', '10<=x<20', etc.
class(var, 5, 'value') // '0<= value <5', etc.
class(var, 10, 'x', 5) // offset by 5: '5<=x<15', etc.

// Useful for age groupings
LOAD *, class(Age, 10, 'age') as AgeGroup FROM data.csv;
```

### match

Case-sensitive comparison, returns position number of match (1-based), or 0.

```qlik
match(str, expr1 [, expr2, ...])
match(M, 'Jan', 'Feb', 'Mar')  // returns 2 if M='Feb', 0 if not found
```

### mixmatch

Same as `match` but case-insensitive.

```qlik
mixmatch(str, expr1 [, expr2, ...])
mixmatch(M, 'Jan', 'Feb', 'Mar')  // returns 1 if M='jan'
```

### pick

Returns the nth expression from a list.

```qlik
pick(n, expr1 [, expr2, ...])
pick(IterNo(), 'Math', 'English', 'Science', 'History')
```

### wildmatch

Case-insensitive comparison with wildcard support (`*` and `?`).

```qlik
wildmatch(str, expr1 [, expr2, ...])
wildmatch(Product, '*Export*', 'Local?')
```

---

## Counter Functions

### autonumber

Generates a sequential integer for each unique value of `expression`. Optionally scoped to `auto_number_key`.

```qlik
autonumber(expression [, auto_number_key])
autonumber(CustomerID)
autonumber(CustomerID & '-' & Year, 'CustomerYear')
```

### autonumberhash128 / autonumberhash256

Same as `autonumber` but takes a hash of the combined arguments.

```qlik
autonumberhash128(field1, field2 [, ...])
autonumberhash256(field1, field2 [, ...])
```

### IterNo

Returns the iteration number in a `WHILE` loop (starts at 1).

```qlik
IterNo()
// Used to read one record multiple times
LOAD mid(Grades, IterNo(), 1) as Grade
FROM Grades.csv
WHILE IsNum(mid(Grades, IterNo(), 1));
```

### RecNo

Returns the current record number within the current data source (resets per source).

```qlik
RecNo()
LOAD RecNo() as RowID, * FROM data.csv;
```

### RowNo

**Script:** Returns the row number of the current record in the current internal Qlik table (does not reset between sources).
**Chart:** Returns the row number of the current row in a table chart.

```qlik
RowNo()          // script context
RowNo([TOTAL])   // chart context
```

---

## Inter-Record Functions

### Script: Peek

Looks up a value from a previously loaded row. `row_no = -1` means the last loaded row, `-2` the second-last, etc. Positive `row_no` is 0-indexed from the start.

```qlik
Peek(field_name [, row_no [, table_name]])

// Running balance example
LOAD
    Date,
    Amount,
    Peek('Balance') + Amount as Balance
FROM transactions.csv;
```

### Script: Previous

Returns the value of an expression from the previous input record (before any WHERE filter discarded it).

```qlik
Previous(expr)

// Day-on-day change
LOAD Date, Amount, Amount - Previous(Amount) as DayChange FROM data.csv;
```

### Script: Exists

Returns `TRUE` if a field value has already been loaded into the field. Used for deduplication and conditional loading.

```qlik
Exists(field_name [, expr])

// Load only new customers
LOAD * FROM new_customers.csv WHERE NOT Exists(CustomerID);

// Check value in a specific field
LOAD * FROM data.csv WHERE Exists(ProductID, RelatedProductID);
```

### Script: LookUp

Looks up a value from any previously loaded table.

```qlik
LookUp(field_name, match_field_name, match_field_value [, table_name])

// Get country name from customer ID
LookUp('CountryName', 'CustomerID', CustomerID, 'Customers')
```

### Chart: Above / Below

`Above()` returns expression value from the row above (in column sort order).
`Below()` returns expression value from the row below.

```qlik
Above([TOTAL] expr [, offset [, count]])
Below([TOTAL] expr [, offset [, count]])

// Period-on-period change
Sum(Sales) - Above(Sum(Sales))

// Moving average (3 rows including current)
RangeAvg(Above(Sum(Sales), 0, 3))

// Rolling 12-month sum
RangeSum(Above(Sum(Sales), 0, 12))
```

### Chart: Top / Bottom

`Top()` evaluates expression at the first row of the column segment.
`Bottom()` evaluates at the last row.

```qlik
Top([TOTAL] expr [, offset [, count]])
Bottom([TOTAL] expr [, offset [, count]])

// Percentage of total column
Sum(Sales) / Bottom(Sum(Sales))

// First value in segment
Top(Sum(Sales))
```

### Chart: Column

Returns value from a specific numbered measure column in a straight table.

```qlik
Column(ColumnNo)
Column(2)  // value of the second measure column
```

### Chart: Dimensionality / SecondaryDimensionality

```qlik
Dimensionality()            // count of dimension columns with non-aggregation content
SecondaryDimensionality()   // horizontal equivalent (pivot tables)
```

### Field Functions (Script and Chart)

```qlik
FieldIndex(field_name, value)    // position of value in field (load order)
FieldValue(field_name, elem_no)  // value at position elem_no (1-indexed)
FieldValueCount(field_name)      // count of distinct values in field
```

---

## Range Functions

Range functions operate on a list of values (often combined with `Above()`).

### Basic Range Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `RangeSum` | `RangeSum(first_expr [, expr...])` | Sum; treats non-numeric as 0 |
| `RangeAvg` | `RangeAvg(first_expr [, expr...])` | Arithmetic mean |
| `RangeMax` | `RangeMax(first_expr [, expr...])` | Maximum value |
| `RangeMin` | `RangeMin(first_expr [, expr...])` | Minimum value |
| `RangeMaxString` | `RangeMaxString(first_expr [, expr...])` | Last text in sort order |
| `RangeMinString` | `RangeMinString(first_expr [, expr...])` | First text in sort order |
| `RangeCount` | `RangeCount(first_expr [, expr...])` | Count of non-NULL values |
| `RangeNullCount` | `RangeNullCount(first_expr [, expr...])` | Count of NULL values |
| `RangeNumericCount` | `RangeNumericCount(first_expr [, expr...])` | Count of numeric values |
| `RangeTextCount` | `RangeTextCount(first_expr [, expr...])` | Count of text values |
| `RangeMissingCount` | `RangeMissingCount(first_expr [, expr...])` | Count of missing values |
| `RangeMode` | `RangeMode(first_expr [, expr...])` | Most common value |
| `RangeOnly` | `RangeOnly(first_expr [, expr...])` | Value if unique, else NULL |

### Statistical Range Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `RangeStdev` | `RangeStdev(first_expr [, expr...])` | Standard deviation |
| `RangeSkew` | `RangeSkew(first_expr [, expr...])` | Skewness |
| `RangeKurtosis` | `RangeKurtosis(first_expr [, expr...])` | Kurtosis |
| `RangeCorrel` | `RangeCorrel(x, y {, x, y})` | Correlation |
| `RangeFractile` | `RangeFractile(fraction, first_expr [, expr...])` | Percentile/fractile |

### Financial Range Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `RangeIRR` | `RangeIRR(first_expr [, expr...])` | Internal rate of return |
| `RangeNPV` | `RangeNPV(discount_rate, first_expr [, expr...])` | Net present value |
| `RangeXIRR` | `RangeXIRR(value, date {, value, date})` | XIRR non-periodic |
| `RangeXNPV` | `RangeXNPV(discount_rate, values, dates)` | XNPV non-periodic |

### Common Range Patterns with Above()

```qlik
// Rolling 3-period average
RangeAvg(Above(Sum(Sales), 0, 3))

// Rolling 12-month sum (YTD-style)
RangeSum(Above(Sum(Sales), 0, 12))

// Period-over-period comparison
Sum(Sales) - RangeSum(Above(Sum(Sales), 12, 1))

// Count numeric values in prior 3 rows
RangeNumericCount(Above(MyField, 0, 3))
```

---

## Financial Functions

For all financial functions: cash paid out = negative; cash received = positive. Use consistent units for `rate` and `nper`.

| Function | Syntax | Description |
|----------|--------|-------------|
| `FV` | `FV(rate, nper, pmt [, pv [, type]])` | Future value of an investment |
| `PV` | `PV(rate, nper, pmt [, fv [, type]])` | Present value |
| `Pmt` | `Pmt(rate, nper, pv [, fv [, type]])` | Payment per period |
| `nPer` | `nPer(rate, pmt, pv [, fv [, type]])` | Number of periods |
| `Rate` | `Rate(nper, pmt, pv [, fv [, type]])` | Interest rate per period |
| `BlackAndSchole` | `BlackAndSchole(strike, time_left, underlying_price, vol, risk_free_rate, type)` | European option price |

**Arguments:**

| Argument | Description |
|----------|-------------|
| `rate` | Interest rate per period |
| `nper` | Total number of periods |
| `pmt` | Payment per period (negative for payments made) |
| `pv` | Present value / initial amount |
| `fv` | Future value / target balance |
| `type` | `0` = end of period payments; `1` = beginning of period |

```qlik
// Monthly payment on $20,000 loan at 10% annual over 8 months
Pmt(0.1/12, 8, 20000)           // → -$2,594.66

// Future value of $20/month at 6%/year for 36 months
FV(0.005, 36, -20)              // → $786.72

// Number of periods to reach $800 at $20/month at 6%/year
nPer(0.005, -20, 0, 800)        // → 36.56

// Monthly interest rate on $10,000 loan, $300/month, 5 years
Rate(60, -300, 10000)           // → 2.00%

// Black-Scholes option value
BlackAndSchole(130, 4, 68.5, 0.4, 0.04, 'call')  // → 11.245
```

---

## Formatting Functions

These functions create a dual value (numeric + string) from a number.

| Function | Syntax | Description |
|----------|--------|-------------|
| `Date` | `Date(number [, format])` | Format as date |
| `Time` | `Time(number [, format])` | Format as time |
| `Timestamp` | `Timestamp(number [, format])` | Format as timestamp |
| `Interval` | `Interval(number [, format])` | Format as duration |
| `Money` | `Money(number [, format [, dec_sep [, thou_sep]]])` | Format as currency |
| `Num` | `Num(number [, format [, dec_sep [, thou_sep]]])` | Format as number |
| `Dual` | `Dual(text, number)` | Combine text and number into dual value |
| `ApplyCodepage` | `ApplyCodepage(text, codepage)` | Apply character encoding |

```qlik
Date(Today(), 'YYYY-MM-DD')               // '2024-06-15'
Time(Now(), 'hh:mm')                       // '14:30'
Timestamp(Now(), 'YYYY-MM-DD hh:mm:ss')   // '2024-06-15 14:30:00'
Money(35648.50, '#,##0.00 R', '.', ',')   // '35,648.50 R'
Num(12345.678, '###0.00', '.', ',')       // '12345.68'
Interval(1.5, 'D hh:mm')                  // '1 12:00'

// Dual: show month name but sort numerically
Dual('June', 6)

// Practical: sortable week display
Dual(WeekYear(Date) & 'W' & Week(Date), WeekStart(Date)) as YearWeek

// Practical: quarter with sort order
Dual('Q' & Ceil(Month(Date)/3), Ceil(Month(Date)/3)) as Quarter
```

---

## Interpretation Functions

These convert strings to dual values (string + number) using explicit format patterns.

| Function | Syntax | Description |
|----------|--------|-------------|
| `Date#` | `Date#(text [, format])` | Interpret string as date |
| `Time#` | `Time#(text [, format])` | Interpret string as time |
| `Timestamp#` | `Timestamp#(text [, format])` | Interpret string as timestamp |
| `Interval#` | `Interval#(text [, format])` | Interpret string as interval |
| `Money#` | `Money#(text [, format [, dec_sep [, thou_sep]]])` | Interpret string as money |
| `Num#` | `Num#(text [, format [, dec_sep [, thou_sep]]])` | Interpret string as number |
| `Text` | `Text(expr)` | Force expression to be treated as text |

```qlik
// Convert stored date string to date value
Date#('15/06/2024', 'DD/MM/YYYY')

// Convert ISO timestamp
Timestamp#('2024-06-15T14:30:00', 'YYYY-MM-DDTHH:mm:ss')

// Convert European number format
Num#('1.234,56', '###0,00', ',', '.')  // → 1234.56

// Use alt() to try multiple date formats
alt(
    Date#(RawDate, 'YYYY-MM-DD'),
    Date#(RawDate, 'DD/MM/YYYY'),
    Date#(RawDate, 'MM/DD/YY'),
    'Invalid'
)
```

---

## Colour Functions

### Pre-defined Colour Functions

Each returns an RGB colour representation. An optional `alpha` parameter (0-255) makes it ARGB.

| Function | RGB Value | Function | RGB Value |
|----------|-----------|----------|-----------|
| `black([alpha])` | (0,0,0) | `white([alpha])` | (255,255,255) |
| `blue([alpha])` | (0,0,128) | `yellow([alpha])` | (255,255,0) |
| `red([alpha])` | (128,0,0) | `green([alpha])` | (0,128,0) |
| `cyan([alpha])` | (0,128,128) | `magenta([alpha])` | (128,0,128) |
| `brown([alpha])` | (128,128,0) | `darkgray([alpha])` | (128,128,128) |
| `lightblue([alpha])` | (0,0,255) | `lightgreen([alpha])` | (0,255,0) |
| `lightcyan([alpha])` | (0,255,255) | `lightgray([alpha])` | (192,192,192) |
| `lightred([alpha])` | (255,0,0) | `lightmagenta([alpha])` | (255,0,255) |

```qlik
blue()        // RGB(0,0,128)
blue(128)     // ARGB(128,0,0,128) — semi-transparent blue
```

### ARGB — Alpha + RGB

```qlik
ARGB(alpha, r, g, b)
// alpha 0=transparent, 255=opaque; r/g/b: 0-255
ARGB(255, 0, 128, 0)    // fully opaque green
ARGB(128, 255, 0, 0)    // semi-transparent red
```

### RGB

```qlik
RGB(r, g, b)
RGB(255, 128, 0)  // orange
```

### HSL

```qlik
HSL(hue, saturation, luminosity)
// All values between 0 and 1
HSL(0.33, 1, 0.5)  // green (equivalent to RGB(0,255,0))
```

### Gradient and Palette Functions

```qlik
// Two-colour gradient (value 0 to 1)
Colormix1(value, ColorZero, ColorOne)
Colormix1(0.5, red(), blue())  // purple at midpoint

// Two-colour gradient with midpoint (value -1 to 1)
Colormix2(value, ColorMinusOne, ColorOne [, ColorZero])

// Colour by palette index
Color(n)  // returns colour n from chart palette

// Hue-cycle colourmap (x: 0-1, red→yellow→green→cyan→blue→magenta→red)
ColorMapHue(x)

// Jet colourmap (x: 0-1, blue→cyan→yellow→orange→red)
ColorMapJet(x)

// Windows system colour
SysColor(nr)
```

---

## Mapping Functions

Mapping tables provide an efficient lookup alternative to joins.

### Creating a Mapping Table

```qlik
// Mapping prefix: creates a two-column lookup table
CountryMap:
Mapping LOAD CustomerID, CountryName FROM customers.csv;
```

### ApplyMap

Applies a mapping table to a field. Optional default value if no match.

```qlik
ApplyMap('MappingTableName', field_value [, default_value])

// Apply country mapping
LOAD
    OrderID,
    CustomerID,
    ApplyMap('CountryMap', CustomerID, 'Unknown') as Country
FROM orders.csv;
```

### MapSubstring

Replaces all occurrences of mapping keys in a string.

```qlik
MapSubstring('MappingTableName', text)

// Replace abbreviations
AbbrevMap: Mapping LOAD * INLINE [from, to US, United States UK, United Kingdom];
LOAD MapSubstring('AbbrevMap', CountryCode) as Country FROM data.csv;
```

---

## Statistical Distribution Functions

All implemented using the Cephes function library.

### CHIDIST / CHIINV

```qlik
CHIDIST(value, degrees_freedom)   // one-tailed chi-squared probability
CHIINV(prob, degrees_freedom)     // inverse: given prob, find value

CHIDIST(8, 15)    // → 0.9238
CHIINV(0.9238, 15) // → 8.0000
```

### FDIST / FINV

```qlik
FDIST(value, degrees_freedom1, degrees_freedom2)
FINV(prob, degrees_freedom1, degrees_freedom2)
```

### NORMDIST / NORMINV

```qlik
NORMDIST(value, mean, standard_dev)  // cumulative normal distribution
NORMINV(prob, mean, standard_dev)     // inverse

NORMDIST(0.5, 0, 1)       // standard normal CDF at 0.5
NORMINV(0.6915, 0, 1)     // → 0.5000
```

### TDIST / TINV

```qlik
TDIST(value, degrees_freedom, tails)  // Student's t probability; tails=1 or 2
TINV(prob, degrees_freedom)           // inverse (two-tailed)

TDIST(1, 30, 2)      // → 0.3253
TINV(0.3253, 30)     // → 1.0000
```

---

## Ranking Functions

### Rank (Chart Only)

Evaluates rows within a column segment and returns rank position.

```qlik
Rank([TOTAL] expr [, mode [, fmt]])
```

**mode parameter:**

| Value | Description |
|-------|-------------|
| `0` (default) | Standard competition ranking (1,2,2,4) with grouping based on midpoint |
| `1` | Lowest rank in sharing group |
| `2` | Average rank |
| `3` | Highest rank |
| `4` | Dense ranking (consecutive) |

**fmt parameter:**

| Value | Description |
|-------|-------------|
| `0` (default) | Range display: `'1-2'` for ties |
| `1` | Low value only |
| `2` | Low value on first row, blank on rest |

```qlik
Rank(Sum(Sales))          // standard rank
Rank(Sum(Sales), 1, 2)    // lowest rank, show only first tied row
```

### HRank (Pivot Tables Only)

Horizontal rank within a row segment of a pivot table.

```qlik
HRank([TOTAL] expr [, mode [, fmt]])
HRank(Sum(Sales))
```

---

## Geospatial Functions

### Aggregation Geospatial Functions

```qlik
GeoAggrGeometry(field_name)    // aggregate multiple areas into one
GeoBoundingBox(field_name)     // minimum bounding box of aggregated geometries
```

### Non-Aggregation Geospatial Functions

```qlik
GeoGetBoundingBox(geometry)       // bounding box of single geometry
GeoGetPolygonCenter(geometry)     // centroid point of polygon
GeoCountVertex(geometry)          // number of vertices in geometry
GeoMakePoint(longitude, latitude) // create point geometry from coordinates
GeoInvProjectGeometry(geometry, projection)  // inverse projection
GeoProjectGeometry(geometry, projection)     // project geometry
GeoReduceGeometry(geometry, tolerance)       // simplify geometry
```

---

## File Functions

Script-only functions for working with files during load.

| Function | Syntax | Returns |
|----------|--------|---------|
| `Attribute` | `Attribute(filename, attribute_name)` | File attribute value |
| `ConnectString` | `ConnectString()` | Current connect string |
| `FileBaseName` | `FileBaseName()` | Filename without extension |
| `FileDir` | `FileDir()` | Directory of current file |
| `FileExtension` | `FileExtension()` | File extension of current file |
| `FileName` | `FileName()` | Current file name |
| `FilePath` | `FilePath()` | Full path to current file |
| `FileSize` | `FileSize([filename])` | File size in bytes |
| `FileTime` | `FileTime([filename])` | File modification timestamp |
| `GetFolderPath` | `GetFolderPath(VirtualFolderName)` | Windows virtual folder path |

### QVD File Information Functions

| Function | Syntax | Returns |
|----------|--------|---------|
| `QvdCreateTime` | `QvdCreateTime(filename)` | Timestamp QVD was created |
| `QvdFieldName` | `QvdFieldName(filename, field_no)` | Name of field at position |
| `QvdNoOfFields` | `QvdNoOfFields(filename)` | Number of fields in QVD |
| `QvdNoOfRecords` | `QvdNoOfRecords(filename)` | Number of records in QVD |
| `QvdTableName` | `QvdTableName(filename)` | Table name stored in QVD |

```qlik
// Check QVD metadata before loading
LET vFields = QvdNoOfFields('lib://Data/Sales.qvd');
LET vRows   = QvdNoOfRecords('lib://Data/Sales.qvd');
LET vCreated = QvdCreateTime('lib://Data/Sales.qvd');
```

---

## System Functions

| Function | Context | Description |
|----------|---------|-------------|
| `Author()` | Both | App author property |
| `ClientPlatform()` | Both | User agent string of client browser |
| `ComputerName()` | Both | Computer/server name (max 15 chars) |
| `DocumentName()` | Both | App filename with extension, no path |
| `DocumentPath()` | Both | Full path to app |
| `DocumentTitle()` | Both | App title |
| `EngineVersion()` | Both | Full engine version string |
| `GetCollationLocale()` | Script | Collation locale culture name |
| `GetObjectField([index])` | Chart | Name of dimension at index |
| `GetRegistryString(path, key)` | Both | Windows registry value (not standard mode) |
| `IsPartialReload()` | Both | `-1` if partial reload, else `0` |
| `OSUser()` | Both | Current logged-in user |
| `ProductVersion()` | Both | Deprecated; use `EngineVersion()` |
| `ReloadTime()` | Both | Timestamp of last completed reload |
| `StateName()` | Chart | Name of current alternate state |

```qlik
// Dynamic title based on alternate state
='Region - ' & if(StateName() = '$', 'Default', StateName())

// Conditional colour by state
if(StateName() = 'Group 1', rgb(152,171,206),
   if(StateName() = 'Group 2', rgb(187,200,179),
      rgb(210,210,210)))
```

---

## Table and Field Information Functions

Script-only (except `NoOfRows` which is available in charts).

| Function | Syntax | Returns |
|----------|--------|---------|
| `FieldName` | `FieldName(field_number, table_name)` | Field name at position |
| `FieldNumber` | `FieldNumber(field_name, table_name)` | Position of named field |
| `NoOfFields` | `NoOfFields(table_name)` | Number of fields in table |
| `NoOfRows` | `NoOfRows(table_name)` | Number of rows in table |
| `NoOfTables` | `NoOfTables()` | Number of loaded tables |
| `TableName` | `TableName(table_number)` | Name of table at position |
| `TableNumber` | `TableNumber(table_name)` | Position number of named table |

```qlik
// Iterate all loaded tables and their fields
For t = 0 to NoOfTables() - 1
    For f = 1 to NoOfFields(TableName($(t)))
        TableInfo: LOAD
            TableName($(t)) as TableName,
            FieldName($(f), TableName($(t))) as FieldName
        Autogenerate 1;
    Next f
Next t;
```

---

## Trigonometric and Hyperbolic Functions

All angles are in **radians**. All functions work in both script and chart expressions.

| Function | Description |
|----------|-------------|
| `cos(x)` | Cosine; result in [-1, 1] |
| `acos(x)` | Inverse cosine; defined for x in [-1, 1]; result in [0, π] |
| `sin(x)` | Sine; result in [-1, 1] |
| `asin(x)` | Inverse sine; defined for x in [-1, 1]; result in [-π/2, π/2] |
| `tan(x)` | Tangent |
| `atan(x)` | Inverse tangent; result in [-π/2, π/2] |
| `atan2(y, x)` | Two-dimensional inverse tangent; result in [-π, +π] |
| `cosh(x)` | Hyperbolic cosine; result is positive real |
| `sinh(x)` | Hyperbolic sine |
| `tanh(x)` | Hyperbolic tangent |

---

## Logical Functions

```qlik
IsNull(expr)    // returns True if expr is NULL
IsNum(expr)     // returns True if expr has a numeric value
IsText(expr)    // returns True if expr is text-only
```

---

## NULL Functions

```qlik
NULL()      // explicitly returns NULL
IsNull(x)   // True if x is NULL
```

---

## Synthetic Dimension Functions

These chart-only functions create virtual dimension values not based on loaded fields.

### ValueList

Returns a set of listed static values as a synthetic dimension.

```qlik
ValueList(v1 {, v2, ...})

// Create a three-row measure summary table
ValueList('Number of Orders', 'Average Order Size', 'Total Amount')

// Reference in expression
=if(ValueList('Sales','Cost','Margin') = 'Sales', Sum(Sales),
   if(ValueList('Sales','Cost','Margin') = 'Cost', Sum(Cost),
      Sum(Sales) - Sum(Cost)))
```

### ValueLoop

Returns an iterated sequence of numbers as a synthetic dimension.

```qlik
ValueLoop(from [, to [, step]])

ValueLoop(1, 10)    // generates 1, 2, 3, ..., 10
ValueLoop(2, 10, 2) // generates 2, 4, 6, 8, 10
```

---

## Field and Selection Functions (Chart Only)

| Function | Syntax | Returns |
|----------|--------|---------|
| `GetAlternativeCount` | `GetAlternativeCount(field_name)` | Count of alternative (light grey) values |
| `GetCurrentSelections` | `GetCurrentSelections([record_sep [, tag_sep [, value_sep [, max_values]]]])` | Formatted string of current selections |
| `GetExcludedCount` | `GetExcludedCount(field_name)` | Count of excluded values |
| `GetFieldSelections` | `GetFieldSelections(field_name [, value_sep [, max_values]])` | Selected values as string |
| `GetNotSelectedCount` | `GetNotSelectedCount(field_name)` | Count of non-selected non-excluded values |
| `GetObjectDimension` | `GetObjectDimension([n])` | Dimension name(s) of object |
| `GetObjectField` | `GetObjectField([n])` | Field name(s) of object dimension |
| `GetObjectMeasure` | `GetObjectMeasure([n])` | Measure name(s) of object |
| `GetPossibleCount` | `GetPossibleCount(field_name)` | Count of possible (white/selected) values |
| `GetSelectedCount` | `GetSelectedCount(field_name [, include_excluded])` | Count of selected values |

```qlik
// Show current selections in a text box
GetCurrentSelections(chr(13), '=', ', ', 6)

// Check how many distinct customers are selected
GetSelectedCount(CustomerID)
```

---

## Script Prefixes Reference

| Prefix | Syntax | Purpose |
|--------|--------|---------|
| `Add` | `Add [only] (load\|select\|map)` | Partial reload — append without duplicate check |
| `Buffer` | `Buffer[(incremental\|stale after n days)] (load\|select)` | Cache result as QVD |
| `Concatenate` | `Concatenate [(tablename)] (load\|select)` | Force concatenation of tables |
| `Crosstable` | `Crosstable (attr, data [, n]) (load\|select)` | Unpivot wide table |
| `First` | `First n (load\|select)` | Load only first n records |
| `Generic` | `Generic (load\|select)` | Load generic (attribute-value) table |
| `Hierarchy` | `Hierarchy(NodeID, ParentID, NodeName, ...)` | Expand adjacent node hierarchy |
| `HierarchyBelongsTo` | `HierarchyBelongsTo(NodeID, ParentID, NodeName, AncestorID, AncestorName)` | All ancestor relationships |
| `Inner Join/Keep` | `Inner (Join\|Keep) [(tbl)] (load\|select)` | Inner join/keep |
| `IntervalMatch` | `IntervalMatch(matchfield) (load\|select)` | Match discrete values to intervals |
| `Join` | `[Inner\|Outer\|Left\|Right] Join [(tbl)] (load\|select)` | Join tables |
| `Keep` | `(Inner\|Left\|Right) Keep [(tbl)] (load\|select)` | Reduce tables without joining |
| `Left Join/Keep` | `Left (Join\|Keep) [(tbl)] (load\|select)` | Left join/keep |
| `Mapping` | `Mapping (load\|select)` | Create two-column lookup table |
| `NoConcatenate` | `NoConcatenate (load\|select)` | Prevent auto-concatenation |
| `Outer Join` | `Outer Join [(tbl)] (load\|select)` | Full outer join |
| `Replace` | `Replace [only] (load\|select\|map)` | Drop and reload table |
| `Right Join/Keep` | `Right (Join\|Keep) [(tbl)] (load\|select)` | Right join/keep |
| `Sample` | `Sample p (load\|select)` | Random sample (probability p per record) |
| `Semantic` | `Semantic (load\|select)` | Self-referencing relationship table |
| `Unless` | `Unless condition statement` | Conditional execution (compact if) |
| `When` | `When condition statement` | Conditional execution (compact if) |

---

## Script Control Statements

### if...elseif...else...end if

```qlik
IF condition THEN
    statements
[ELSEIF condition2 THEN
    statements]
[ELSE
    statements]
END IF
```

### for...next

```qlik
FOR variable = startval TO endval [STEP stepval]
    statements
NEXT [variable]
```

### for each...next

```qlik
FOR EACH var IN list
    statements
NEXT [var]

// Iterate field values
FOR EACH file IN FileList('lib://Data/*.qvd')
    LOAD * FROM [$(file)] (qvd);
NEXT file
```

### while...wend

```qlik
WHILE condition
    statements
WEND
```

### do...loop

```qlik
DO [WHILE|UNTIL condition]
    statements
LOOP [WHILE|UNTIL condition]
```

### switch...case...default...end switch

```qlik
SWITCH expression
CASE valuelist
    statements
[CASE valuelist2
    statements]
[DEFAULT
    statements]
END SWITCH
```

### exit...

```qlik
EXIT SCRIPT [WHEN condition]
EXIT DO [WHEN condition]
EXIT FOR [WHEN condition]
EXIT SUB [WHEN condition]
```

### sub...end sub / call

```qlik
SUB SubroutineName [(param1, param2, ...)]
    statements
END SUB

CALL SubroutineName [(arg1, arg2, ...)]
```

### Variables in Script

```qlik
SET variable = value;       // literal string assignment
LET variable = expression;  // calculated assignment

SET vYear = 2024;
LET vLastYear = $(vYear) - 1;
LET vCount = NoOfRows('Sales');
```

---

## System Variables Reference

### Number Interpretation Variables

```qlik
SET DecimalSep='.';
SET ThousandSep=',';
SET MoneyDecimalSep='.';
SET MoneyThousandSep=',';
SET MoneyFormat='R #,##0.00';
SET NumericalAbbreviation='3:k;6:M;9:G;12:T;15:P;18:E;21:Z;24:Y;-3:m;-6:µ;-9:n;-12:p;-15:f;-18:a;-21:z;-24:y';
```

### Date and Time Variables

```qlik
SET DateFormat='DD/MM/YYYY';
SET TimeFormat='hh:mm:ss';
SET TimestampFormat='DD/MM/YYYY hh:mm:ss[.fff]';
SET MonthNames='Jan;Feb;Mar;Apr;May;Jun;Jul;Aug;Sep;Oct;Nov;Dec';
SET LongMonthNames='January;February;March;April;May;June;July;August;September;October;November;December';
SET DayNames='Mon;Tue;Wed;Thu;Fri;Sat;Sun';
SET LongDayNames='Monday;Tuesday;Wednesday;Thursday;Friday;Saturday;Sunday';
SET FirstWeekDay=0;         // 0=Monday (ISO default)
SET BrokenWeeks=0;          // 0=ISO weeks (no broken weeks)
SET ReferenceDay=4;         // min days for ISO week 1 (ISO: 4)
SET FirstMonthOfYear=1;     // fiscal year start (1=January)
```

### Error Variables

```qlik
ScriptError        // error code of last script error
ScriptErrorCount   // number of errors since last reload
ScriptErrorList    // list of errors
ScriptErrorDetails // detailed error info
```

### Value Handling Variables

```qlik
SET NullInterpretation='';   // string that maps to NULL on load
SET OtherSymbol='';          // field value that matches all others
```

### Direct Discovery Variables

```qlik
DirectQuery DIMENSION ...
DirectQuery MEASURE ...
DirectQuery DETAIL ...
```

---

*Document compiled from Qlik Sense April 2020 official documentation and Qlik Sense Cookbook (Packt 2015). For the most current function list, consult help.qlik.com.*
