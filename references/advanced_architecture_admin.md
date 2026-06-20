# Qlik Sense Advanced Patterns and Best Practices — Architecture Admin


> Split from `advanced_patterns.md`. Companion files share the `advanced_` prefix.


## App Architecture and Design

### Three-Sheet Pattern

A well-designed Qlik Sense app typically uses three tiers of sheets:

1. **Overview / Executive Sheet** — KPIs, summary charts, trends. High-level. Decision-makers.
2. **Analysis Sheets** — Drill-down charts, filters, comparative analysis. Analysts.
3. **Detail / Data Sheets** — Tables, raw data, export-ready. Power users.

### Global Filters / Selections Panel

- Place filter panes for the most common dimensions (Date, Region, Product) on a collapsible sidebar or at the top of key sheets.
- Use a "Clear All Selections" button on every sheet.

### Bookmarks for Common Contexts

Encourage users to create bookmarks for:
- Current YTD with default filters
- Prior year comparative view
- Key market/region selections
- "All data" (cleared selections) starting point

### Sheet Navigation and Actions

Buttons can navigate to other sheets and simultaneously set selections:

```qlik
// Button action: Navigate to sheet + Set field value
// Action 1: Set field value — Year = 2024
// Action 2: Navigate to sheet — Analysis Sheet
```

### Naming Conventions

| Object | Convention | Example |
|--------|-----------|---------|
| Tables | PascalCase | `FactSales`, `DimCustomer` |
| Fields | PascalCase | `CustomerID`, `OrderDate` |
| Variables | camelCase with `v` prefix | `vCurrentYear`, `vLastYear` |
| Measures | Title Case | `Total Sales`, `Gross Margin %` |
| Dimensions | Title Case | `Customer Name`, `Product Category` |
| QVD files | PascalCase + `.qvd` | `FactSales.qvd`, `DimCustomer.qvd` |
| Script tabs | Descriptive names | `01_Init`, `02_Extract`, `03_Transform` |

### Script Tab Organisation

```
Tab 01: Initialisation (SET variables, common settings)
Tab 02: Date Calendar (master date table)
Tab 03: Dimension Tables (customers, products, etc.)
Tab 04: Fact Tables (transactions, events)
Tab 05: Derived Fields and Aggregations
Tab 06: Data Quality Checks
```

### Date Calendar Pattern

A proper calendar table is essential for time intelligence.

```qlik
// Generate a complete date calendar
MinDate:
LOAD Min(TransDate) as MinDate FROM transactions.qvd (qvd);

MaxDate:
LOAD Max(TransDate) as MaxDate FROM transactions.qvd (qvd);

LET vMinDate = Peek('MinDate', 0, 'MinDate');
LET vMaxDate = Peek('MaxDate', 0, 'MaxDate');
DROP TABLES MinDate, MaxDate;

Calendar:
LOAD
    Date(Date, 'DD/MM/YYYY') as Date,
    Year(Date) as Year,
    Month(Date) as Month,
    Day(Date) as Day,
    Week(Date) as Week,
    WeekYear(Date) as WeekYear,
    WeekDay(Date) as WeekDay,
    Dual('Q' & Ceil(Month(Date)/3), Ceil(Month(Date)/3)) as Quarter,
    Dual(WeekYear(Date) & 'W' & Week(Date), WeekStart(Date)) as YearWeek,
    MonthName(Date) as MonthYear,
    Year(Date) * 100 + Month(Date) as YearMonth,
    InYearToDate(Date, Today(), 0) as IsYTD,
    InQuarterToDate(Date, Today(), 0) as IsQTD,
    InMonthToDate(Date, Today(), 0) as IsMTD,
    InYear(Date, Today(), -1) as IsPriorYear,
    InYearToDate(Date, Today(), -1) as IsPriorYTD
;
LOAD Date($(vMinDate) + RowNo() - 1) as Date
AUTOGENERATE $(vMaxDate) - $(vMinDate) + 1;
```

---

## Section Access and Security

Section Access controls which users see which data within an app. It is defined in the script.

### Basic Structure

```qlik
Section Access;
LOAD * INLINE [
ACCESS, USERID, PASSWORD, [FIELD_NAME]
ADMIN, ADMIN_USER, admin123,
USER, john.doe@company.co.za, pass123, ZA
USER, jane.smith@company.co.za, pass456, UK
USER, *,, *
];

Section Application;
// Normal data load below
```

### Access Levels

| ACCESS value | Permissions |
|--------------|-------------|
| `ADMIN` | Full access, all data, can manage app |
| `USER` | Standard access, subject to data reduction |

### Data Reduction (Row-Level Security)

The field name in Section Access must match a field name in the app data. Qlik automatically filters rows so each user only sees their own data.

```qlik
Section Access;
LOAD * INLINE [
ACCESS, USERID, REGION
ADMIN, admin@company.co.za,
USER, john.doe@company.co.za, ZA
USER, jane.smith@company.co.za, UK
];

Section Application;
Transactions:
LOAD *, Region FROM transactions.qvd (qvd);
// User john.doe will only see rows where Region='ZA'
```

### Dynamic Data Reduction

Use a separate table for access control (loaded from a secure source):

```qlik
Section Access;
UserAccess:
SQL SELECT ACCESS, USERID, REGION FROM security_db.dbo.UserAccessRights;

Section Application;
```

### OMIT Fields

Fields listed in `OMIT` column are hidden from that user:

```qlik
Section Access;
LOAD * INLINE [
ACCESS, USERID, OMIT
USER, standard_user, Salary; CostPrice
ADMIN, admin_user,
];
```

### Inherited Access Restrictions

When publishing or exporting apps, Section Access restrictions are inherited. Users cannot bypass them through direct export.

---

## Data Manager vs Data Load Editor

| Feature | Data Manager | Data Load Editor |
|---------|-------------|-----------------|
| Target user | Non-developers, analysts | Developers |
| Interface | GUI drag-and-drop | Script editor |
| Capabilities | Basic transformations, associations | Full script power |
| Suitable for | Small-medium apps | Enterprise apps |
| QVD support | Limited | Full |
| Scripted logic | No | Yes |
| Recommended for production | No | Yes |

### Synchronising Managed Tables

When both are used together, sync scripted tables via Data Manager → "Synchronise scripted tables".

### Calculated Fields in Data Manager

Data Manager supports calculated fields using a subset of Qlik functions:

```qlik
// In Data Manager calculated field:
Upper([CustomerName])
Left([ProductName], 10)
Year([OrderDate])
```

---

## Publishing, Streams, and Distribution

### Streams

Streams are the primary container for published apps in Qlik Sense Enterprise. Apps in a stream are visible to users with access to that stream.

**Types of content in streams:**
- Published apps (read-only for users)
- Community sheets (shared by non-owners)

**Stream hierarchy:**
- Streams are flat (not hierarchical).
- Access is controlled by security rules.
- The "Published" state is separate from the "Development" working copy.

### Publishing Workflow

1. Develop app in personal "My Work" space (Qlik Sense Desktop or server personal space).
2. Test and validate.
3. Publish to a stream via: App menu → Publish → Select stream.
4. Once published, users can see the app but cannot edit the base version.

### Duplicate vs Publish

- **Duplicate**: creates a personal copy you can edit.
- **Publish**: shares the original (or a copy) to a stream. Owner retains edit rights.

### Community Sheets

Regular users (not app owners) can create **private sheets** and optionally **publish them** to the community area of the app for other users to see without the owner needing to do anything.

```
Private sheet → Published (community) sheet → Approved (owner adds to app) sheet
```

### Reload Scheduling

Apps in Qlik Sense Enterprise are reloaded via **Tasks** in the QMC:
- Sequential tasks
- Trigger-based (on completion of another task)
- Time-based schedule
- Event-based

---

## Storytelling and Snapshots

### Snapshots

A snapshot is a static image of a visualisation at a point in time. Snapshots do NOT update when data reloads.

**Uses:**
- Preserve a state before selections change.
- Use in a data story to illustrate a finding.
- Annotate with text overlays.

### Creating a Story

1. Navigate to "Storytelling" mode.
2. Add slides.
3. Drag snapshots or live sheets (embedded sheets) onto slides.
4. Add text boxes, shapes, and images.
5. Annotate key findings with callouts.

### Embedded Sheets in Stories

Unlike snapshots, embedded sheets in a story remain live (connected to current data). Useful when the story is presented with fresh data each time.

---

## On-Demand Apps

On-demand apps enable analysis of large datasets without loading all data into memory. Users make selections in a "selection app" to define a subset, then generate an "on-demand app" containing only that subset.

### Components

1. **Selection App**: Regular Qlik Sense app with aggregated data. User makes selections to narrow scope.
2. **Template App**: Contains the detailed data load script with binding expressions.
3. **On-Demand App**: Generated dynamically when user triggers creation.

### Binding Expressions in Template Apps

```qlik
// Template app script uses binding expressions
// These are substituted with actual selected values when the app is generated
SELECT * FROM Orders
WHERE CustomerID IN ($(ods_CustomerID))
  AND Year = $(ods_Year);
```

---

## Direct Discovery

Direct Discovery allows Qlik Sense to query large databases on-demand rather than loading all data into memory.

### Field Types

| Type | Description |
|------|-------------|
| `DIMENSION` | Fields used as dimensions; loaded into memory |
| `MEASURE` | Fields used in aggregations; queried from source |
| `DETAIL` | Additional fields accessible in detail tables |

### Differences from In-Memory

- Slower for interactive use (each selection triggers a database query).
- Suitable for very large datasets that cannot fit in RAM.
- Limited chart type support.
- No offline access.
- Sorting and chart inter-record functions not available for MEASURE fields.

```qlik
DIRECT QUERY
    DIMENSION CustomerID, CustomerName, Region
    MEASURE Sales, Quantity
    DETAIL OrderDate, ProductID
FROM large_transactions;
```

---

## Analytic Connections (SSE)

Server-Side Extensions (SSE) allow Qlik Sense to call external calculation engines (Python, R, etc.) from both the data load script and chart expressions.

### Script Usage

```qlik
// Call external function from script
Values: LOAD Rand() as A, Rand() as B AUTOGENERATE 50;

// Call function P.Calculate in plugin, passing fields A and C
Load * Extension P.Calculate(Values{A, C});

// Evaluate an R script
Load A as A_echo, B as B_echo
Extension R.ScriptEval('q;', Values{A, B});

// Use a variable for the script
Load * Extension R.ScriptEval('$(My_R_Script)', Values{A, B});
```

### Chart Usage

```qlik
// In a chart measure
P.PredictSales(Sum(Sales), Count(Orders))
```

---

## Administration and Governance

### Qlik Sense Architecture (Enterprise)

| Component | Role |
|-----------|------|
| QRS (Repository Service) | Central configuration, security rules, app metadata |
| QES (Engine Service) | In-memory analytics engine; handles calculations |
| QPS (Proxy Service) | Authentication, session management, load balancing |
| QSS (Scheduler Service) | Task scheduling and reload execution |
| QDS (Data Connector Service) | Manages data connections |
| NPrinting | Pixel-perfect reporting and distribution |

### Nodes and Deployment

- **Central node**: primary; runs all services.
- **Worker/rim nodes**: additional computation; scale-out for more apps or users.
- **Single-node**: development/small deployments.
- **Multi-node**: production enterprise deployments.

### Licensing

| Type | Description |
|------|-------------|
| Professional | Full access: create, edit, publish, reload |
| Analyser | View and interact only (no editing) |
| Analyser Capacity | Concurrent session-based (not per user) |
| Core | QIX engine API access |

**Tokens**: older licensing model; each user access pass consumes tokens from a pool.

### Security Rules

Security rules govern access to streams, apps, data connections, and other resources. Written in the QMC using the Security Rules editor.

```
// Allow all users access to Published stream
resource.stream.name = "Published" and user.@IsActive = "True"

// Allow group members to publish
resource.hasPrivilege("publish") and user.group = "Publishers"
```

### Managing Data Connections

- Data connections are stored in the QRS.
- Shared connections are available to all apps on the node.
- Personal connections (Desktop) are stored locally.
- Connection security: users need explicit permission to use each connection.

### Tasks and Reload Monitoring

- Schedule reloads via QMC → Tasks → Create task.
- Chain tasks: configure sequential dependencies.
- Monitor via QMC → Tasks → Status.
- Reload logs: QMC → Apps → [App] → Reload history.

### Extensions and Custom Objects

- Extensions are uploaded via QMC → Extensions.
- Only administrators can upload extensions.
- Extensions appear in the chart type picker for all users.

---

## Debugging and Troubleshooting

### Script Debugging

Use the Debug pane in the Data Load Editor:

```
1. Set a breakpoint by clicking the gutter next to the line.
2. Click "Debug script" button.
3. Step through with Step In, Step Over, Step Out.
4. Inspect variable values in the Variables panel.
5. View log output in the Log panel.
```

### Common Script Errors

| Error | Likely Cause |
|-------|-------------|
| "Invalid path" | Missing `lib://` prefix or incorrect connection name |
| "Table not found" | Table referenced before it was loaded, or wrong name |
| "Circular reference" | Two tables create a loop of associations |
| "Synthetic key" | Two tables share more than one field name |
| Statement not terminated | Missing semicolon at end of LOAD or SQL |
| Single quote inside string | Use `''` (double single quote) inside a quoted string |

### Data Model Viewer Diagnostics

In the Data Model Viewer:
- **Orange highlighted tables**: tables associated to the selected table.
- **Dashed border**: loosely coupled table (circular reference detected).
- **`$Syn` tables**: synthetic key tables (should be avoided).

Field statistics in the Preview pane:
- **Density**: percentage of non-NULL values.
- **Subset ratio**: percentage of dimension values that exist in fact table.
- **Has duplicates**: flag for non-unique values.
- **Total distinct values vs Present distinct values**: useful for detecting bad keys.

### Performance Profiling

```qlik
// Log timing of each section
LET vStart = Now();
// ... load operations ...
TRACE Section completed in $(=Interval(Now()-vStart, 'hh:mm:ss'));
```

### Checking for Circular References

```qlik
// Script will warn: "Circular reference detected"
// Look for the loosely coupled table (dashed line) in Data Model Viewer
// Resolution: rename fields or use a link table
```

### Validating Data After Load

```qlik
// After loading, verify counts
LET vSalesRows = NoOfRows('FactSales');
LET vCustRows  = NoOfRows('DimCustomer');
TRACE FactSales has $(vSalesRows) rows;
TRACE DimCustomer has $(vCustRows) rows;

// Verify expected fields exist
LET vFieldCount = NoOfFields('FactSales');
IF vFieldCount < 10 THEN
    TRACE WARNING: FactSales has fewer fields than expected;
END IF;
```

---
