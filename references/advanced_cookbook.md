# Qlik Sense Advanced Patterns and Best Practices — Cookbook


> Split from `advanced_patterns.md`. Companion files share the `advanced_` prefix.


## Cookbook Recipes

### Recipe 1: Subroutine for Reusable Table Loading

```qlik
// Define reusable subroutine
SUB LoadQVD(vName)
    [$(vName)]:
    LOAD * FROM 'lib://QVDs/$(vName).qvd' (qvd);
END SUB

// Call for each table
CALL LoadQVD('FactSales')
CALL LoadQVD('DimCustomer')
CALL LoadQVD('DimProduct')
CALL LoadQVD('DimDate')
```

### Recipe 2: Efficient Conditional Script Loading

```qlik
// Use a flag variable to control which sections run
SET vLoadFull = 1;
SET vLoadIncremental = 0;

IF $(vLoadFull) = 1 THEN
    LOAD * FROM 'lib://Source/Sales.csv';
ELSE
    LOAD * FROM 'lib://QVDs/Sales.qvd' (qvd);
END IF;
```

### Recipe 3: Dynamic Date Ranges

```qlik
// Set variables for rolling 13-month window
LET vStartDate = MakeDate(Year(AddMonths(Today(),-13)), Month(AddMonths(Today(),-13)), 1);
LET vEndDate   = Today();

LOAD * FROM transactions.qvd (qvd)
WHERE TransDate >= '$(vStartDate)'
  AND TransDate <= '$(vEndDate)';
```

### Recipe 4: Slowly Changing Dimension via IntervalMatch

```qlik
// Step 1: Load transactions with date
Trans: LOAD TransID, CustomerID, ProductID, TransDate, Qty, Price FROM transactions.qvd (qvd);

// Step 2: Load historical cost rates with intervals
CostHistory:
LOAD ProductID, ValidFrom, ValidTo, CostRate FROM cost_history.qvd (qvd);

// Step 3: Link transaction date to applicable cost interval
Inner Join (Trans)
IntervalMatch(TransDate, ProductID)
LOAD ValidFrom, ValidTo, ProductID
Resident CostHistory;

// Step 4: Join in the rate
Left Join (Trans)
LOAD ProductID, ValidFrom, CostRate
Resident CostHistory;

DROP TABLE CostHistory;
```

### Recipe 5: Loading Data from Multiple CSV Files

```qlik
// Dynamic loading from folder
FOR EACH vFile IN FileList('lib://DataFiles/Sales*.csv')
    LET vYear = SubField(SubField('$(vFile)', '/', -1), '.', 1);
    Sales:
    LOAD *, '$(vYear)' as SourceYear FROM [$(vFile)]
    (txt, delimiter is ',', embedded labels);
NEXT vFile
```

### Recipe 6: Using Concat() to Store Multiple Values in One Cell

```qlik
// In script: concatenate child records into parent
Orders: LOAD OrderID, CustomerID FROM orders.qvd (qvd);

OrderLines:
LOAD OrderID, Concat(ProductName, ', ') as Products
FROM order_lines.qvd (qvd)
GROUP BY OrderID;

LEFT JOIN (Orders) LOAD * Resident OrderLines;
DROP TABLE OrderLines;
```

### Recipe 7: KPI with RAG Status and Conditional Colour

```qlik
// KPI Measure:
Sum(Sales)

// KPI conditional colour (background):
if(Sum(Sales) / Sum(Target) >= 1,
    rgb(0, 160, 0),              // Green — on target
    if(Sum(Sales) / Sum(Target) >= 0.8,
        rgb(255, 165, 0),        // Amber — within 20% of target
        rgb(200, 0, 0)           // Red — more than 20% below target
    )
)

// Label colour (white for readability on dark backgrounds):
white()
```

### Recipe 8: Reference Lines in Gauge Chart

```qlik
// Gauge chart setup:
// Measure: Sum(Sales)
// Under Add-ons → Reference lines:
//   Expression: =Sum(Target)
//   Label: Target
//   Colour: red()
//
// Under Appearance → Presentation:
//   Max: =Sum(Target) * 1.2  (20% above target)
//
// Segments:
//   Segment 1 limit: =Sum(Target)*0.30  — colour: grey
//   Segment 2 limit: =Sum(Target)*0.60  — colour: red
//   Segment 3 limit: =Sum(Target)       — colour: yellow
//   Final segment   — colour: green (with gradient)
```

### Recipe 9: Extended IntervalMatch for Slowly Changing Products

```qlik
// Goal: assign the correct product price to each transaction
// even though prices changed over time

PriceHistory:
LOAD
    ProductID,
    Date(ValidFrom) as ValidFrom,
    Date(if(IsNull(ValidTo), Today(), ValidTo)) as ValidTo,
    Price
FROM price_history.qvd (qvd);

Transactions:
LOAD TransID, ProductID, TransDate, Quantity FROM transactions.qvd (qvd);

// Extended interval match: matches on TransDate AND ProductID
IntervalMatch(TransDate, ProductID)
LOAD ValidFrom, ValidTo, ProductID
Resident PriceHistory;

// Now each transaction has ValidFrom and ValidTo
// Join back to get the Price
Left Join (Transactions)
LOAD ProductID, ValidFrom, Price Resident PriceHistory;
```

### Recipe 10: Associating Persistent Colours to Field Values

```qlik
// In chart: Colour → By dimension → Custom
// For each dimension value, assign a colour:
// In the colour picker, map:
//   'ZA'  → green
//   'UK'  → blue
//   'US'  → red

// Or via expression:
pick(
    match(Country, 'ZA', 'UK', 'US', 'DE'),
    green(), blue(), red(), darkgray()
)
```

### Recipe 11: Smart Search Filter Pattern

```qlik
// Use GetCurrentSelections() in a text box to show active filters
='Active filters: ' & GetCurrentSelections(chr(10), ': ', ', ', 5)

// Button to clear all selections
// Action: Clear selections (all fields)
```

### Recipe 12: Creating a Geo Map from Coordinates

```qlik
// Script: load latitude/longitude
Stores:
LOAD
    StoreID,
    StoreName,
    Latitude,
    Longitude,
    GeoMakePoint(Longitude, Latitude) as Coordinates
FROM stores.csv;

// In chart: Map visualisation
// Layer → Point layer
// Location field: Coordinates
// Size by: Sum(Sales)
// Colour by: Sum(Sales)/Sum(TOTAL Sales)
```

---

*Document compiled from Qlik Sense April 2020 official documentation, Qlik Sense Cookbook (Packt 2015), Learning Qlik Sense — The Official Guide Second Edition (Packt 2015), and Qlik Sense Advanced Data Visualisation (Dr Christopher Ilacqua, Packt 2015). For the most current guidance, consult help.qlik.com.*
