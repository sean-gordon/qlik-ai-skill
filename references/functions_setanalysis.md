# Qlik Sense Function Reference (Complete) — Setanalysis


> Split from `functions_reference.md`. Companion files share the `functions_` prefix.


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
