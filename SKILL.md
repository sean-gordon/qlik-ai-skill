---
name: QlikSense
description: "Use this skill when asked to investigate Qlik Sense data models, ETL load scripts, UI expressions (Set Analysis, Aggr, range functions), visualisation design, performance optimisation, Section Access, incremental reloads, or when debugging any Qlik Sense error — script, data model, or system-level. Also use this skill when the user mentions QVD, QVF, reload log, data model viewer, master items, star schema in a Qlik context, preceding load, ApplyMap, synthetic keys, or describes a Qlik chart showing wrong values, zeros, nulls, or dashes — even if they don't say 'Qlik Sense' explicitly. Includes a complete function reference and advanced pattern library sourced from official Qlik documentation, plus the Komment write-back extension (Kaptain service, partial reloads, write-back to external databases). Also use when the user mentions Komment, write-back, or commenting in a Qlik context."
version: 4.1
---

# Qlik Sense Expert Assistant Guide

This skill equips you with comprehensive Qlik Sense architecture, scripting, frontend expression, visualisation design, and debugging expertise. Use this guide to analyse and solve Qlik-related problems systematically and completely.

**Scope:** Qlik Sense app development — data modelling, load scripts, expressions, visualisations, and debugging. This covers Desktop, Enterprise, and SaaS editions at the application layer. It does not cover QSEoW server administration (QRS/Engine API, reload tasks, security rules) or infrastructure operations (backup/restore, service management, cache warming).

## How to use the knowledge base — ALWAYS retrieve through the tool

This skill has a large reference corpus (~60k tokens across 18 files). **Never read whole reference files to answer a question.** For accuracy and low token use, every lookup goes through the retrieval tool, which returns only the few relevant passages (typically under 1,500 tokens) with their source file and heading path. Reading a whole file is a last resort, used only when the tool genuinely cannot be made to run (see step D) or when you have been explicitly asked to work through one file end to end.

The tool ships with this skill in the **`tool/` folder beside this SKILL.md**. Work down this ladder on the first Qlik lookup of a session, then keep using whichever rung succeeded:

**A — MCP tool (preferred).** If a tool named `qlik_knowledge_search` is available in the session, call it:
- `qlik_knowledge_search(query, top_k=5, domain=optional)` — e.g. `qlik_knowledge_search("incremental reload upsert pattern", domain="advanced")`.
- Use a `domain` filter to narrow: `backend`, `frontend`, `functions`, `advanced`, `debugging`, `visualisation`, `komment`, or cross-cutting tags `set-analysis`, `qvd`, `section-access`, `performance`. Call `qlik_knowledge_domains()` if unsure.

**B — CLI (works the same session, no restart).** If `qlik_knowledge_search` is *not* in the session, run the bundled CLI via the shell — it reads the same index and needs no MCP restart. Use the tool's own venv Python:
- Windows: `tool\.venv\Scripts\python.exe tool\qlik_search.py "your query" --domain advanced`
- macOS/Linux: `tool/.venv/bin/python tool/qlik_search.py "your query" --domain advanced`
- List filters with `... qlik_search.py --domains`.

**C — Bootstrap if not installed, then retry B.** If step B prints `QLIK_TOOL_NOT_READY` (exit code 3) or the venv is missing, install the tool once, then go back to step B:
- Windows: `py tool\setup.py`  ·  macOS/Linux: `python3 tool/setup.py`
- `setup.py` creates the venv, installs dependencies, and builds the index (first run downloads a ~90MB local embedding model; no API key, then offline). It also prints the `claude mcp add` command — run it so `qlik_knowledge_search` (step A) is available in future sessions, but you do **not** need to wait for a restart: step B works immediately after setup.

**D — Last resort only.** If, and only if, the tool cannot be made to run after setup (e.g. no Python available), read the single most relevant reference file below — never several.

Always make a fresh, specific search per sub-question; several narrow searches beat one vague one.

| Reference file | Covers (use as a `domain` hint, or to pick a last-resort read) |
|-----------|-----------|
| [scripting_knowledgebase.md](references/scripting_knowledgebase.md) | Backend load scripts: LOAD variants, joins, mapping, null handling, IntervalMatch, CrossTable |
| [expression_knowledgebase.md](references/expression_knowledgebase.md) | Frontend expressions: Set Analysis, Aggr, TOTAL, layout/navigation functions |
| [debugging_guide.md](references/debugging_guide.md) | Script errors, data model diagnostics, performance, server troubleshooting |
| [visualization_guide.md](references/visualization_guide.md) | Chart selection, KPI design, DAR layout, styling |
| [komment_guide.md](references/komment_guide.md) | Komment write-back extension: install, security rules, widgets, Kaptain, partial reloads |
| **Functions** — `functions_operators_aggregation.md` | Operators; aggregation functions (Sum, Count, Avg, Aggr, Concat) |
| `functions_setanalysis.md` | Set Analysis BNF syntax, identifiers, operators, P()/E() |
| `functions_datetime.md` | All date/time functions, period boundaries, in-period functions |
| `functions_string_numeric.md` | String, numeric, conditional, logical, null, formatting, interpretation |
| `functions_counter_range_stat.md` | Counter, range, financial, statistical, ranking functions |
| `functions_inter_record.md` | Above/Below/Peek, synthetic dimension, chart selection functions |
| `functions_other.md` | Colour, mapping, geospatial, file, system, table info, script prefixes, system variables |
| **Advanced** — `advanced_datamodel.md` | Chasm/fan traps, link tables, ApplyMap vs join, Join/Keep |
| `advanced_qvd_incremental.md` | All four incremental QVD patterns, QVD optimisation |
| `advanced_scripting.md` | Advanced scripting, Hierarchy/Crosstable/IntervalMatch prefixes, cleansing |
| `advanced_expressions_viz.md` | Advanced Set Analysis, master library, alternate states |
| `advanced_architecture_admin.md` | App architecture, Section Access, publishing, ODAG, Direct Discovery, governance |
| `advanced_cookbook.md` | The 12 complete cookbook recipes |

> The retrieval tool indexes every file above. Setup and registration details are in `tool/README.md`.

---

## 1. Contextual Distinction: Backend vs. Frontend

**This is the most critical concept in Qlik Sense.** Always maintain a strict separation between the two execution environments. Mixing contexts is the most common source of Qlik errors.

### Backend (Data Load Script / ETL)
Executed during app reloads. Runs linearly, top to bottom (except preceding loads which evaluate bottom to top within a block). Responsible for all data extraction, transformation, key resolution, and schema creation.

**Key Statements:** `LOAD`, `SELECT`, `RESIDENT`, `MAPPING LOAD`, `JOIN`, `KEEP`, `CONCATENATE`, `NoConcatenate`, `STORE`, `DROP TABLE`, `BINARY`, `GENERIC LOAD`, `CROSSTABLE`, `INTERVALMATCH`

**Script-Only Functions:** `Exists()`, `Peek()`, `Lookup()`, `ApplyMap()`, `FieldValue()`, `FieldValueCount()`, `NoOfTables()`, `TableName()`, `NoOfRows()`, `QvdCreateTime()`, `QvdNoOfRecords()`, `FileList()`, `RecNo()`, `IterNo()`

**Reference:** [Scripting Reference](references/scripting_knowledgebase.md)

### Frontend (Chart Expressions / UI)
Evaluated dynamically in real time in response to user selections. Every chart expression re-evaluates whenever selections change. Executed per sheet object, not during reload.

**Key Concepts:** Set Analysis, nested aggregations with `Aggr()`, `TOTAL` qualifier, dimension-aware navigation, alternate states

**UI-Only Functions:** `Sum()`, `Count()`, `Avg()`, `Only()`, `Concat()`, `Aggr()`, `Dimensionality()`, `Above()`, `Below()`, `Before()`, `After()`, `GetSelectedCount()`, `GetCurrentSelections()`, `RangeSum()`, `FirstSortedValue()`, `Rank()`, `TOTAL`

**Reference:** [Expressions Reference](references/expression_knowledgebase.md)

---

## 2. Data Modelling Architecture & Best Practices

### 3-Tier QVD Architecture
```
Layer 1 — Extract:      Raw tables → stored as Extract QVDs (no transformation)
Layer 2 — Transform:    Load Extract QVDs, apply business logic, mapping, key resolution → Transform QVDs
Layer 3 — Application:  Load Transform QVDs directly into app (minimal transforms at this layer)
```
This architecture enables incremental reloads, re-use across apps, and fast app loads (QVD optimised mode).

### Schema Design
- **Target:** Star or Snowflake schema with one central fact table.
- **Avoid synthetic keys:** Resolve by renaming fields, dropping unnecessary associations, or building a Link Table.
- **Avoid circular references:** Rename key fields to clarify their role per context (e.g., `OrderDate` vs `InvoiceDate`).
- **Prefer `ApplyMap()`** over `JOIN` for adding single fields — faster, no row multiplication risk.
- **Use `AutoNumber()`** on composite keys to replace long string keys with integers — reduces memory 5–10x.
- **Use `KEEP`** instead of `JOIN` to preserve star schema while filtering rows.

### Incremental Reloads
Use QVD-based incremental patterns to only load new/changed records. Check `QvdCreateTime()` to detect existing QVDs and track the last loaded max date as the delta watermark.

**Reference:** [Scripting Reference — Section 10](references/scripting_knowledgebase.md)

---

## 3. Set Analysis & Expression Patterns

### Key Set Analysis Patterns
| Pattern | Expression |
| :--- | :--- |
| Ignore all selections | `Sum({1} Sales)` |
| Clear a specific field | `Sum({<Year = >} Sales)` |
| Override to a value | `Sum({<Year = {2026}>} Sales)` |
| Prior year | `Sum({<Year = {$(=Max(Year)-1)}>} Sales)` |
| Dynamic date range | `Sum({<Date = {">=$(=vStart)<=$(=vEnd)"}>} Sales)` |
| Customers with sales > 100K | `Sum({<Customer = {"=Sum(Sales)>100000"}>} Sales)` |
| Possible values (nested) | `Sum({<Customer = P({<Product={'Shoes'}>} Customer)>} Sales)` |
| Rolling 12 months | `RangeSum(Above(Sum(Sales), 0, 12))` |
| % of total | `Sum(Sales) / Sum(TOTAL Sales)` |
| % within dimension | `Sum(Sales) / Sum(TOTAL <Region> Sales)` |

**Reference:** [Expressions Reference](references/expression_knowledgebase.md)

---

## 4. Visualisation Selection

Select chart types based on the analytical question:

| Question Type | Chart |
| :--- | :--- |
| Compare magnitudes | Horizontal bar (many items), vertical bar (few/time) |
| Show trends over time | Line chart |
| Compare multiple series | Small Multiples / Bar Table |
| Part-to-whole (few items) | Pie chart (max 5 slices) |
| Part-to-whole (hierarchical) | Treemap (max 3 levels) |
| Financial movement | Waterfall chart |
| Distribution of a metric | Histogram or box plot |
| Two-metric correlation | Scatter plot |
| Three-metric analysis | Bubble chart |
| KPI performance vs target | Bullet graph or KPI card with RAG |
| Flow between stages | Sankey diagram or Funnel chart |

**Critical anti-patterns to avoid:** dual-axis charts, interleaved bars (use small multiples), legends (use direct labels), stacked area charts (use line table).

**Reference:** [Visualisation Design Guide](references/visualization_guide.md)

---

## 5. Troubleshooting & Debugging Protocol

When diagnosing Qlik problems, follow this systematic approach:

1. **Identify the layer:** Is the issue in the load script (backend) or chart expression (frontend)?
2. **Script errors:** Check `ScriptError`, `ScriptErrorList`, and `ScriptErrorCount`. Use `Trace` and `FlushLog` for runtime logging. Use the Data Load Editor debugger with Limited Load mode.
3. **Data model issues:** Open the Data Model Viewer. Look for `$Syn` tables (synthetic keys) and red circular reference arrows. Resolve both before diagnosing expressions.
4. **Expression issues:** Use a Straight Table to isolate field values vs. expression results. Test Set Analysis scope with `Count({1} DISTINCT Field)` and `Count({$} DISTINCT Field)` side by side.
5. **Performance issues:** Check for large string keys (fix with `AutoNumber()`), unoptimised QVD loads (fix by removing WHERE from the QVD LOAD), and heavy `Aggr()` usage (pre-calculate in script).
6. **System issues:** Check QMC reload logs, service status, and data connection credentials.

**Reference:** [Debugging & Troubleshooting Protocol](references/debugging_guide.md)

---

## 6. Section Access (Security)

Section Access controls row-level (and column-level) data visibility per user.

**Critical rules:**
1. All ACCESS, USERID, and reduction field values must be **UPPERCASE**.
2. The reduction key field must exist in the Section Application data model (also uppercase).
3. The reload service account (`INTERNAL\SA_SCHEDULER`) must have `ACCESS = ADMIN`.
4. `OMIT` hides entire fields from specific users.
5. Test as a named user using the "Always one selected value" or "Open in browser" approaches.

**Reference:** [Scripting Reference — Section 13](references/scripting_knowledgebase.md)

---

## 7. Complete Function & Pattern References

Look up function signatures with `qlik_knowledge_search` (domain `functions`) when you need exact parameter order, return types, or usage examples. If reading files directly, the function reference is split by family: `functions_operators_aggregation.md`, `functions_setanalysis.md`, `functions_datetime.md`, `functions_string_numeric.md`, `functions_counter_range_stat.md`, `functions_inter_record.md`, and `functions_other.md` (colour, mapping, geospatial, file, system, prefixes, variables).

Consult the advanced files (domain `advanced`) when implementing incremental reload strategies (append, insert-only, upsert, full SCD — see `advanced_qvd_incremental.md`), resolving data model problems (chasm/fan traps, link tables — `advanced_datamodel.md`), building complex Set Analysis (`advanced_expressions_viz.md`), or working through complete recipes (`advanced_cookbook.md`).

---

## 8. Generic Problem-Solving Methodology

Use this methodology for any Qlik issue where the root cause is not immediately obvious. Work through the steps in order — do not skip ahead to fix attempts before completing diagnosis.

### Step 1 — Establish the symptom precisely

Before touching any script or expression, define the symptom exactly:

| Question | Why it matters |
| :--- | :--- |
| Is the field returning `0`, `NULL`, `-`, or a wrong value? | `0` usually means a calculation computed as zero. `NULL`/`-` usually means a failed join or missing association. A wrong value means the calculation is running but using incorrect inputs. |
| Does a comparable field (same type, same join pattern) work correctly? | Isolates whether the problem is structural (data model) or specific to this field's logic. |
| Does the issue appear in both the frontend chart and a raw Straight Table? | If only the chart, the problem is in the expression or dimension context. If both, the problem is in the data model. |
| Is the issue in one app or multiple apps that share the same source? | Points to whether the fix belongs in a source (upstream) app or a downstream consumer app. |

---

### Step 2 — Read the reload log before touching the script

**Always read the reload log first.** The log is the ground truth of what actually executed — it is more reliable than reading the script, because the script may have been edited but not yet reloaded, or code may be in a disabled section or wrong tab.

**What to look for in the log:**

- Confirm the table in question was actually created (look for the table label and `lines fetched` count).
- Confirm any fix code was actually executed (search for a unique table name or field name from the fix).
- Check `lines fetched` on Left Joins — the number tells you how many rows were read from the source table, but **does not confirm matches were found**. Zero matches still show as `lines fetched > 0` followed by `Joining/Keeping`.
- Check field counts on table creation — if a field you expect is missing from `fields found`, it was never loaded.
- Look for `Exit Script` — any code after this line does not execute.
- Check variable values — `LET` statements in the log show the resolved value of variables at reload time. An undefined variable resolves to empty string (numerically `0`).

---

### Step 3 — Trace the data flow from source to chart

For a field that returns zero or null, trace the complete path:

```
QVD source
  → LOAD into staging table (correct field name? correct alias?)
    → Transformation / preceding load (correct formula? no broken chain?)
      → Key used in LEFT JOIN (does key exist in both tables? same data type?)
        → Field lands in target table (confirmed in log fields found?)
          → Target table concatenated into fact table (field carried through?)
            → Fact table has association path to Calendar/dimension (date field not dropped?)
              → Frontend expression references correct field name
```

Breaks at any point in this chain produce a zero or null result in the frontend.

**Common break points:**

| Break point | Symptom | Diagnostic |
| :--- | :--- | :--- |
| Wrong source field name in LOAD | Field loads as NULL | Compare QVD field names in log vs. script |
| Undefined variable `$(vName)` | Variable expands to `''` = `0` in formulas | Check `LET` statements at top of log |
| Key mismatch in Left Join | All joined fields = NULL | Compare row counts between source QVDs (FDR vs non-FDR variants are a common cause) |
| Forward-reference within a single LOAD | Expression uses alias defined in same LOAD | Use a preceding load to compute the alias first, then reference it in the outer LOAD |
| Date field dropped before Calendar join | No association path from Calendar to table | Search log for `drop fields` on the date field |
| Fix code not in the reload | Field unchanged after applying fix | Search log for a unique identifier from the fix code |

---

### Step 4 — Distinguish zero from null

`Sum()` returns `0` for both NULL values and genuinely zero values. To distinguish:

```qlik
// In a Straight Table, add these two columns side by side:
Count([FieldName])          // returns 0 if field is always NULL
Count({1} [FieldName])      // counts regardless of selections
Only([FieldName])           // shows the value if all rows agree, '-' if mixed or null
```

If `Count([FieldName])` = 0, the field is NULL in all rows — the join failed or the field was never populated.
If `Count([FieldName])` > 0 but `Sum([FieldName])` = 0, the values exist but are genuinely zero — the calculation formula is the problem.

---

### Step 5 — Verify the fix executed before concluding it failed

Before diagnosing why a fix "didn't work", confirm the fix actually ran:

1. Search the reload log for a unique string from the fix code (a new table name, a new field alias, a `DROP TABLE` statement).
2. If not found: the script was not saved, the code is after `Exit Script`, or it is in a disconnected tab.
3. If found but still returning zero: the fix ran but has a logical error — return to Step 3.

**Never diagnose a fix as logically incorrect until you have confirmed it actually executed.**

---

### Step 6 — Preceding load syntax rules

A preceding load chains LOAD statements so that each outer LOAD reads from the result of the inner LOAD below it. Key rules:

- **Each LOAD block must end with a semicolon (`;`).** Semicolons are required between LOAD blocks — they are statement separators, not terminators of the chain. Removing them breaks the syntax.
- **An alias defined in one LOAD is not available as a field name in the same LOAD.** If expression B depends on alias A, A must be computed in an inner LOAD so that the outer LOAD can read it as a real field.
- **The chain is read bottom to top** during execution — the innermost LOAD (with the data source) runs first, feeding the next LOAD up, and so on to the outermost LOAD.

```qlik
// Correct 2-level preceding load — semicolons required between blocks
OuterTable:
LOAD
    KeyField,
    (Value / WorkingDays) * ProRataDays    AS ProRataValue   // reads fields from inner LOAD
;                                                            // ← required
LOAD
    KeyField,
    RawValue                               AS Value,
    NetWorkDays(StartDate, EndDate)        AS WorkingDays,   // computed here, available above
    NetWorkDays(StartDate, CutoffDate)     AS ProRataDays
Resident SourceTable;
```

---

### Step 7 — Binary load app chains

When an app binary-loads another app, the loaded app's complete data model (all tables, all fields, all associations) is inherited. This creates a chain where:

- A downstream app's tables may have keys from a **different QVD variant** than the upstream app's tables — causing Left Joins to find no matches.
- Tables inherited from binary load may need to be **dropped and rebuilt** from the downstream app's own QVD sources before joins are applied.
- Confirm the app chain direction before deciding where a fix belongs — fixing the wrong app in the chain has no effect.

**Reference:** [Debugging & Troubleshooting Protocol](references/debugging_guide.md)
