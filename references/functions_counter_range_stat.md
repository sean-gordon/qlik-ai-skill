# Qlik Sense Function Reference (Complete) — Counter Range Stat


> Split from `functions_reference.md`. Companion files share the `functions_` prefix.


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
