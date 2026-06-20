# Qlik Sense Advanced Patterns and Best Practices — Expressions Viz


> Split from `advanced_patterns.md`. Companion files share the `advanced_` prefix.


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
