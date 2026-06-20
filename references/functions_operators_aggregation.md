# Qlik Sense Function Reference (Complete) — Operators Aggregation


> Split from `functions_reference.md`. Companion files share the `functions_` prefix.


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
