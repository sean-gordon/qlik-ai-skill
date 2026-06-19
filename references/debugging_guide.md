# Qlik Sense Debugging & Troubleshooting Protocol

Use this guide to identify, analyse, and resolve errors in Qlik Sense load scripts, data models, expressions, and system services.

## Companion references

| Reference | Use when |
|-----------|----------|
| [Scripting Knowledgebase](scripting_knowledgebase.md) | Writing or reviewing backend load scripts, LOAD/SELECT/JOIN patterns |
| [Expression Knowledgebase](expression_knowledgebase.md) | Writing or debugging frontend chart expressions, Set Analysis, Aggr |
| [Functions Reference](functions_reference.md) | Looking up any Qlik function signature, parameters, or examples |
| [Advanced Patterns](advanced_patterns.md) | Implementing incremental loads, link tables, SCD, hierarchy, or complex modelling |
| [Visualisation Guide](visualization_guide.md) | Choosing chart types, applying DAR layout, or styling dashboards |

## Table of Contents

1. [Data Load Editor Debugger](#1-data-load-editor-debugger)
2. [Real-Time Logging](#2-real-time-logging)
3. [Script Error Reference](#3-script-error-reference)
4. [Common Syntax Gotchas](#4-common-syntax-gotchas)
5. [Data Model Viewer Diagnostics](#5-data-model-viewer-diagnostics)
6. [Expression Debugging in Charts](#6-expression-debugging-in-charts)
7. [Performance Optimisation](#7-performance-optimisation)
8. [System Administration & Server Troubleshooting](#8-system-administration--server-troubleshooting)
9. [Section Access Debugging](#9-section-access-debugging)
10. [NPrinting & Reporting Troubleshooting](#10-nprinting--reporting-troubleshooting)
11. [Qlik Sense API & Automation Debugging](#11-qlik-sense-api--automation-debugging)

---

## 1. Data Load Editor Debugger

The built-in debugger is the primary tool for testing scripts in Qlik Sense Desktop, SaaS, or Enterprise.

1. Open the **Data Load Editor** and click **Show debug panel** (top right).
2. Enable **Limited load** (e.g., 100 rows) to test logic without loading full datasets.
   - *Caveat:* In limited loads, keys may not match across tables, causing unassociated tables in the Data Model Viewer. This is expected and safe for syntax testing.
3. Add **Breakpoints** by clicking line numbers. Execution pauses here for variable inspection.
4. Use **Step** to execute line-by-line and observe console output and active variable values.
5. Use the **Variables** panel (in the debug view) to inspect the current value of every variable.

---

## 2. Real-Time Logging

### Trace Statement
Writes text to the reload progress window and the reload log file. Essential for printing variable states.
```qlik
LET vCount = NoOfRows('CustomerTable');
Trace Customer records loaded: $(vCount);
Trace Current timestamp: $(=Now());
```

### FlushLog Statement
Forces Qlik to write the log buffer to disk immediately. Place before any memory-intensive or crash-prone operation.
```qlik
FOR EACH vTable IN 'Sales', 'Inventory', 'Customers'
    Trace Processing: $(vTable);
    FlushLog;
    LOAD * FROM [lib://QVDs/$(vTable).qvd] (qvd);
NEXT vTable
```

### Reload Log Files
- **Qlik Sense Enterprise (QSEoW):** Logs stored at `C:\ProgramData\Qlik\Sense\Log\Engine\Reload\`
- **Qlik Cloud (SaaS):** Available in the reload task history in the Management Console.
- **Qlik Sense Desktop:** Logs at `%USERPROFILE%\Documents\Qlik\Sense\Log\`

---

## 3. Script Error Reference

### ErrorMode Variable
Controls how the script engine handles errors:

| Value | Behaviour |
| :--- | :--- |
| `SET ErrorMode = 0;` | Ignore all errors — continue executing |
| `SET ErrorMode = 1;` | Prompt or halt (default behaviour) |
| `SET ErrorMode = 2;` | Abort immediately on first error |

### ScriptError Codes

| Code | Description | Code | Description |
| :--- | :--- | :--- | :--- |
| 0 | No error | 9 | Database not found |
| 1 | General error | 10 | Table not found |
| 2 | Syntax error | 11 | Field not found |
| 3 | General ODBC error | 12 | File has wrong format |
| 4 | General OLE DB error | 13 | BIFF error |
| 5 | Custom database error | 14 | BIFF error (encrypted) |
| 6 | XML error | 15 | BIFF error (unsupported version) |
| 7 | HTML error | 16 | Semantic error |
| 8 | File not found | | |

### Graceful Error Handling Pattern
```qlik
// Temporarily allow errors without halting
SET ErrorMode = 0;

LOAD * FROM [lib://Source/Sales.qvd] (qvd);

IF ScriptError = 8 THEN
    Trace WARNING: Sales QVD not found. Skipping and continuing.;
ELSEIF ScriptError > 0 THEN
    Trace ERROR $(ScriptError): $(ScriptErrorList);
    EXIT SCRIPT;
END IF

// Restore default behaviour
SET ErrorMode = 1;
```

### ScriptErrorList
A text variable containing the list of errors from the most recent reload. Inspect after a failed load.
```qlik
Trace Errors encountered: $(ScriptErrorList);
```

---

## 4. Common Syntax Gotchas

### Quote Types
| Quote | Purpose | Example |
| :--- | :--- | :--- |
| `'single'` | Literal string values | `WHERE Country = 'South Africa'` |
| `"double"` | Field/table names with spaces | `LOAD "Customer Code" as CustomerCode` |
| `[square brackets]` | Field/table names (alternative) | `LOAD [Customer Code] as CustomerCode` |
| `` `backtick` `` | Field/table names (alternative, some contexts) | Rare — prefer brackets |

> **Common mistake:** Using single quotes for field names: `LOAD 'CustomerID'` — this loads the literal string "CustomerID" as a value, not the field.

### Missing Semicolons
Every complete script statement must end with `;`. The most frequent cause of general syntax errors.

### Preceding Load Evaluation Order
The script evaluates a preceding load block **bottom to top**. A field created in the upper `LOAD` cannot be used in the lower `LOAD`.

```qlik
// CORRECT: Year is calculated in the lower LOAD; YearGroup uses it in the upper LOAD
LOAD *,
     If(Year >= 2025, 'Current', 'Historical') as YearGroup;    // Evaluated second
LOAD *,
     Year(OrderDate) as Year                                      // Evaluated first
FROM [lib://Orders.qvd] (qvd);

// WRONG: Cannot reference Year in the same LOAD where it is calculated
LOAD
    Year(OrderDate) as Year,
    If(Year >= 2025, 'Current', 'Historical') as YearGroup      // Year not yet available here!
FROM [lib://Orders.qvd] (qvd);
```

### Auto-Concatenation Pitfall
If two consecutively loaded tables share **identical field names**, Qlik automatically merges them. If you then try to `DROP TABLE` the second table, the script fails because the table no longer exists separately.

```qlik
// Fix: explicitly use NoConcatenate or rename fields
NoConcatenate
Table2:
LOAD OrderID, SalesAmount FROM [lib://File2.qvd] (qvd);
```

### Drop/Rename Sequence
Always drop or rename tables **after** their last use. Dropping before use causes runtime errors in any subsequent `RESIDENT` load.

---

## 5. Data Model Viewer Diagnostics

### Identifying Synthetic Keys
Synthetic key tables appear as `$Syn1`, `$Syn2`, etc. in the Data Model Viewer. They are created when two tables share more than one common field name.

**Resolution options:**
1. **Rename** the redundant field in one of the tables.
2. **Drop** the field if it doesn't serve an association purpose.
3. **Use AutoNumber()** to merge multiple fields into a single composite key.
4. **Use a Link Table** for complex many-to-many relationships.

```qlik
// Synthetic key example: Orders and Customers both have CustomerID and OrderDate
// Fix: rename OrderDate in Customers to avoid double association
LOAD
    CustomerID,
    Name,
    Date(FirstOrderDate) as CustomerFirstOrderDate  // Renamed from OrderDate
FROM [lib://Customers.qvd] (qvd);
```

### Identifying Circular References
Circular references appear as **red dotted arrows** in the Data Model Viewer. Qlik will still load, but one link is disabled (greyed out), causing unexpected blank charts.

**Resolution:**
- Rename the duplicated key field to clarify its role in each table context.
- Split the table creating the loop into two separate tables.

### Checking Table Associations
In the Data Model Viewer:
- **Grey arrow:** Unassociated tables (no shared key).
- **Blue line:** Correct 1-to-many association.
- **Red line / dotted:** Circular reference — requires resolution.

### Table Profiling from Script
```qlik
// After loading, print table diagnostics
Trace --- Data Model Summary ---;
LET numTables = NoOfTables();
FOR i = 0 TO $(numTables) - 1
    LET tName  = TableName($(i));
    LET tRows  = NoOfRows('$(tName)');
    LET tCols  = NoOfFields('$(tName)');
    Trace Table: $(tName) | Rows: $(tRows) | Fields: $(tCols);
NEXT i
```

---

## 6. Expression Debugging in Charts

### Using a Table to Inspect Expression Values
When a chart shows unexpected results, add a **Straight Table** with the relevant dimension and suspect measures side by side to compare raw field values vs. calculated values.

### Checking Set Analysis Results
```qlik
// Add a test measure to confirm Set Analysis scope:
Count({<Year = {2026}>} DISTINCT OrderID)    // Should match your expected 2026 order count
Count({1} DISTINCT OrderID)                  // Should match total orders regardless of selection
```

### NULL vs. Zero Issues
```qlik
// A chart showing NULL instead of 0 usually means the WHERE clause or set expression
// has no matching rows — not a formula error.
// Wrap with:
If(IsNull(Sum(Sales)), 0, Sum(Sales))

// Or use the NullZero() function in some contexts:
Alt(Sum(Sales), 0)
```

### Dual Value Confusion
Fields loaded as `Dual()` have both a text and a numeric representation. If a filter returns unexpected results, check whether the comparison uses the text or numeric value:
```qlik
// In expression context, numeric comparison uses the numeric dual part:
Sum({<Month = {6}>} Sales)           // Selects month 6 (June, numeric dual)
Sum({<Month = {'Jun'}>} Sales)       // Selects by text representation
```

---

## 7. Performance Optimisation

### Data Model Performance Checklist

| Issue | Diagnosis | Fix |
| :--- | :--- | :--- |
| Slow chart recalculation | Large fact tables with string keys | Apply `AutoNumber()` on composite keys |
| High memory consumption | Wide tables with unused fields | Only `LOAD` needed fields; drop the rest |
| Slow reload | Full DB extract every time | Implement incremental QVD reload pattern |
| Many synthetic keys | Multiple shared fields between tables | Resolve via rename, drop, or link table |
| Aggregation search in Set Analysis slow | Using `=Sum(...)` inside `{}` | Pre-calculate flag field in script instead |

### QVD Optimised Mode
A QVD load runs in **optimised mode** (10–100x faster) only when:
- No `WHERE` clause is present
- No `JOIN` or `CONCATENATE` is combined in the same `LOAD` statement
- No field transformations appear in the `LOAD` (only field name aliases using `AS` are allowed)

```qlik
// OPTIMISED (fast)
Sales: LOAD * FROM [lib://QVDs/Sales.qvd] (qvd);

// NOT optimised (WHERE clause breaks it)
Sales: LOAD * FROM [lib://QVDs/Sales.qvd] (qvd) WHERE Year = 2026;

// FIX: Use a Resident load for filtering
TempSales: LOAD * FROM [lib://QVDs/Sales.qvd] (qvd);
Sales: LOAD * RESIDENT TempSales WHERE Year = 2026;
DROP TABLE TempSales;
```

### Aggr() Performance
`Aggr()` calculates a virtual table per chart row. Avoid:
- High-cardinality outer dimensions (> 10,000 rows)
- Nesting `Aggr()` inside another `Aggr()`
- Using `Aggr()` in a table with many rows and many columns

Pre-calculate in the reload script using `RESIDENT` grouping and `GROUP BY`:
```qlik
// Pre-calculate max order value per customer in script
CustMaxOrder:
LOAD
    CustomerID,
    Max(OrderValue) as MaxOrderValue
RESIDENT FactOrders
GROUP BY CustomerID;
```

---

## 8. System Administration & Server Troubleshooting

### Qlik Sense Repository Not Responding (QSEoW)
If the Repository Service (QRS) stalls due to database/API delays:
1. Open Registry Editor (`regedit`).
2. Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control`
3. Create a new **DWORD (32-bit)** value named `ServicesPipeTimeout`.
4. Set value data to `86400000` (Decimal) — increases service timeout to 24 hours.
5. Restart the server.

### QMC (Qlik Management Console) Common Tasks

| Task | Navigation Path |
| :--- | :--- |
| Reload task monitoring | QMC → Tasks → Reload Tasks |
| App migration between streams | QMC → Apps → Move to Stream |
| License allocation | QMC → License → User Allocations |
| Custom properties | QMC → Custom Properties |
| Data connections | QMC → Data Connections |
| Proxy management | QMC → Proxies |
| Engine tuning (memory limits) | QMC → Engines |
| Extension management | QMC → Extensions |
| Log monitoring | QMC → System Notifications; or file path `C:\ProgramData\Qlik\Sense\Log\` |

### Qlik Cloud Data Gateway Configuration
```cmd
// Navigate to agent install path
cd "C:\Program Files\Qlik\ConnectorAgent\ConnectorAgent"

// Set tenant URL
connectoragent qcs set_config --tenant_url mytenant.us.qlikcloud.com

// Generate security keys and get registration code
connectoragent qcs generate_keys
connectoragent qcs get_registration

// Start the connector service
connectoragent service start
```
Then complete deployment in Qlik Cloud Management Console → Data Gateways.

### Reload Failure Checklist
When a scheduled reload fails, check in order:

1. **Data connection credentials expired** — test connection in QMC → Data Connections.
2. **Source file missing or path changed** — check `lib://` connection paths.
3. **QVD not found** — verify the previous layer's reload completed successfully.
4. **Timeout** — large SQL queries may exceed engine timeout. Tune `QueryTimeout` in QMC → Engines.
5. **Section Access loop** — the reload service account must have ADMIN access in Section Access.
6. **Memory limit exceeded** — tune `WorkingSetSizeMB` in QMC → Engines.

---

## 9. Section Access Debugging

Section Access errors cause silent data suppression (users see blank data, not an error message). Common issues:

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| User sees no data | USERID not matching | Check case: Section Access values must be UPPERCASE |
| Admin sees correct data; users see nothing | REDUCTION_KEY field case mismatch | Ensure `Upper()` wrapper in Section Application |
| Scheduled reload fails | Scheduler service account not in Section Access | Add `INTERNAL\SA_SCHEDULER` with ACCESS = ADMIN |
| OMIT field still visible | Field name case mismatch in OMIT column | OMIT values must match the field name exactly in UPPERCASE |

```qlik
// Always include the scheduler account as ADMIN
SECTION ACCESS;
LOAD * INLINE [
    ACCESS, USERID,                  REDUCTION_KEY
    ADMIN,  INTERNAL\SA_SCHEDULER,   *
    ADMIN,  DOMAIN\QLIK_ADMIN,        *
    USER,   DOMAIN\USER_A,           ZA
];
```

---

## 10. NPrinting & Reporting Troubleshooting

### Connection Issues
1. Verify the NPrinting Engine is connected to the Qlik Sense node via QMC → NPrinting Connections.
2. Confirm Object IDs are correct (activate Developer Mode in Qlik Sense to extract them).
3. Ensure the report template references the correct connection (App → Sheet → Object).

### Object Not Rendering in Report
- Object is hidden by a Show Condition — remove or override for the NPrinting service account.
- Chart has no data for the filter set used in the NPrinting task — check the filter settings.
- Extension objects may not be supported — use native Qlik Sense charts instead.

### Extracting Object IDs for NPrinting
Activate Developer Mode:
```
https://your-server/sense/app/{appId}/sheet/{sheetId}/state/edit/options/developer
```
Right-click any object → Developer → Copy Object ID (e.g., `CH176`).

---

## 11. Qlik Sense API & Automation Debugging

### Engine API (WebSocket JSON-RPC)
Qlik's Engine API communicates over WebSocket. Use browser dev tools (F12 → Network → WS) to inspect messages.

### QMC REST API
```bash
# Get all apps via REST API
curl -X GET "https://your-server/qrs/app?xrfkey=abcdefghijklmnop" \
     -H "X-Qlik-Xrfkey: abcdefghijklmnop" \
     -H "X-Qlik-User: UserDirectory=INTERNAL;UserId=sa_api" \
     --cert client.pem --key client_key.pem

# Trigger a reload task
curl -X POST "https://your-server/qrs/task/{taskId}/start/synchronous?xrfkey=abcdefghijklmnop" \
     -H "X-Qlik-Xrfkey: abcdefghijklmnop"
```

### Qlik Cloud Management API (Bearer Token)
```bash
# List all spaces
curl -X GET "https://your-tenant.us.qlikcloud.com/api/v1/spaces" \
     -H "Authorization: Bearer {api_key}"

# Reload an app
curl -X POST "https://your-tenant.us.qlikcloud.com/api/v1/reloads" \
     -H "Authorization: Bearer {api_key}" \
     -H "Content-Type: application/json" \
     -d '{"appId": "your-app-id"}'
```
