# Qlik Sense Function Reference (Complete) — Inter Record


> Split from `functions_reference.md`. Companion files share the `functions_` prefix.


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
