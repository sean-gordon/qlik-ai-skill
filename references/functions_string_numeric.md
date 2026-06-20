# Qlik Sense Function Reference (Complete) — String Numeric


> Split from `functions_reference.md`. Companion files share the `functions_` prefix.


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
