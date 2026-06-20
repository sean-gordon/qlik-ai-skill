# Qlik Sense Function Reference (Complete) — Other


> Split from `functions_reference.md`. Companion files share the `functions_` prefix.


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
