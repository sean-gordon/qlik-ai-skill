# Qlik Sense AI Skill

A comprehensive, reusable knowledge skill for AI coding assistants to provide **senior-developer-level** Qlik Sense support — covering scripting, data modelling, Set Analysis, visualisation design, performance optimisation, Section Access, and system debugging.

---

## File Structure

```
qlik-ai-skill/
├── SKILL.md                              # Main skill config + routing (tool-first)
├── references/
│   ├── scripting_knowledgebase.md        # Backend load script encyclopaedia
│   ├── expression_knowledgebase.md       # Frontend expressions encyclopaedia
│   ├── visualization_guide.md            # Chart selection, design, styling
│   ├── debugging_guide.md                # Debugging, error handling, admin
│   ├── komment_guide.md                  # Komment write-back extension
│   ├── functions_operators_aggregation.md   # Operators + aggregation functions
│   ├── functions_setanalysis.md          # Set Analysis BNF + element functions
│   ├── functions_datetime.md             # Date/time functions
│   ├── functions_string_numeric.md       # String, numeric, conditional, logical
│   ├── functions_counter_range_stat.md   # Counter, range, financial, statistical
│   ├── functions_inter_record.md         # Inter-record + chart selection functions
│   ├── functions_other.md                # Colour, mapping, geospatial, system, prefixes
│   ├── advanced_datamodel.md             # Data modelling, traps, link tables
│   ├── advanced_qvd_incremental.md       # Incremental loads + QVD optimisation
│   ├── advanced_scripting.md             # Advanced scripting + prefixes + cleansing
│   ├── advanced_expressions_viz.md       # Advanced Set Analysis, master library
│   ├── advanced_architecture_admin.md    # Architecture, Section Access, governance
│   └── advanced_cookbook.md              # 12 complete cookbook recipes
└── tool/                                 # Semantic-search retrieval tool
    ├── setup.py                          # One-command bootstrap: venv + deps + index
    ├── qlik_index.py                     # Shared search core (used by server + CLI)
    ├── qlik_mcp_server.py                # MCP server: qlik_knowledge_search
    ├── qlik_search.py                    # CLI search (same-session, no MCP restart)
    ├── build_chunks.py                   # References → retrievable chunks
    ├── build_index.py                    # Embed + index (local or pgvector)
    ├── chunks.jsonl                      # Pre-built chunks
    ├── requirements.txt
    └── README.md                         # Tool setup guide
```

**v4.1:** the skill now **always** answers through the retrieval tool and
self-bootstraps it if missing (`tool/setup.py`). A CLI (`tool/qlik_search.py`)
lets it retrieve in the same session without waiting for an MCP restart.

**v4.0:** the two largest references (`functions_reference.md`,
`advanced_patterns.md`) were split into focused files so any single read stays
small, and the retrieval tool was added. Instead of loading whole files
(7k–14k tokens), the assistant pulls only the passages it needs (~1,500 tokens).
See `tool/README.md`.

### What Each File Covers

| File | Key Topics |
| :--- | :--- |
| **SKILL.md** | Backend/frontend distinction, data model architecture, quick Set Analysis patterns, visualisation selection, troubleshooting protocol |
| **scripting_knowledgebase.md** | All LOAD variants (Preceding, Resident, Autogenerate, Inline, Binary, QVD), ApplyMap, JOIN/KEEP/Concatenate, key scripting functions (Exists, Peek, Lookup, AutoNumber), date/string/numeric functions, null handling, incremental reloads, IntervalMatch, CrossTable, Section Access, subroutines (Calendar, Generic Load pivoting), QVD optimisation, data model patterns, link tables |
| **expression_knowledgebase.md** | Full Set Analysis syntax (identifiers, operators, modifiers, wildcards, numeric ranges, aggregation searches, P/E element functions), common YoY/YTD/MAT patterns, all aggregation functions, Aggr(), TOTAL qualifier, date/string/conditional functions in expressions, colour functions, layout/navigation functions (Above/Below/RowNo), range functions, ranking, variables, alternate states, master items, number formatting |
| **visualization_guide.md** | Full chart type matrix (Comparison, Composition, Distribution, Relationship, KPI, Flow), anti-pattern guide, KPI design patterns, advanced chart implementations (trendlines, heatmaps, Gantt, butterfly, waterfall, funnel), alternate states for comparison, dynamic dimensions/measures, Developer Mode, conditional show/hide, storytelling, colour palettes, typography, layout grid, number formatting standards, extensions |
| **debugging_guide.md** | Data Load Editor debugger, Trace/FlushLog, reload log locations, ScriptError codes, graceful error handling, common syntax gotchas, Data Model Viewer diagnostics (synthetic keys, circular references), expression debugging, performance optimisation checklist, QVD optimised mode rules, Aggr() performance, QSEoW server troubleshooting, QMC common tasks, Data Gateway configuration, reload failure checklist, Section Access debugging, NPrinting troubleshooting, Engine/QMC REST API |
| **functions_reference.md** | Complete function encyclopaedia sourced from official Qlik docs: all operators, aggregation functions (with full parameter tables), complete Set Analysis BNF syntax, 50+ date/time functions, all string/numeric/statistical/financial/colour/mapping/inter-record/system/table functions, script prefix reference, system variables |
| **advanced_patterns.md** | Advanced scripting patterns, all four incremental QVD reload patterns, SCD via IntervalMatch, data modelling (chasm/fan traps, link tables, hierarchy table), optimisation strategies, complex Set Analysis patterns, app architecture, master library, alternate states, publishing, streams, administration, security rules, On-Demand Apps, Direct Discovery, Analytic Connections, 12 complete cookbook recipes |
| **komment_guide.md** | Komment write-back extension by ExtendBI — installation (QMC + Kaptain service), external DB config (MS SQL/MySQL/PostgreSQL/Oracle), load script `IsPartialReload()` pattern, QMC security rules (CommentingRole), all 12 widget types, optional settings (conditional show/write, permissions, audit trail, layout), multi-environment `ComputerName()` routing, Qlik SaaS setup, Kaptain admin module |

---

## Installation

The skill works in two parts, and **both are required** for the experience it is designed for:

- **Part A — the skill files** (`SKILL.md` + `references/`). The assistant's Qlik guide and the full knowledge corpus.
- **Part B — the retrieval tool** (`tool/`). It indexes the references so the assistant pulls only the passages it needs (~1,500 tokens) instead of loading a whole file (7k–14k). The skill is built to **always** answer through this tool — for accuracy and low token use — and will offer to install it itself if it is missing. On hosts with a local Python runtime (e.g. Claude Code), install it. Browser-only hosts run Part A alone.

For non-technical users, the easiest way is to let your AI assistant do it. Copy the prompt below; it installs and builds everything.

### 1. Agentic AI Assistants (Claude Code, Antigravity, Aider, etc.)

If your AI assistant can run terminal commands and write files, paste this prompt.

**Copy and paste this prompt:**
```text
Please install or update the Qlik Sense AI skill from the public repository at
https://github.com/sean-gordon/qlik-ai-skill

PART A — install the skill files:
1. Clone or download the whole repository (SKILL.md, the references/ folder, AND the tool/ folder).
2. Identify the correct skills path for your host. If you support global skills, install to the
   global folder (e.g. %USERPROFILE%\.{ai_assistant_name}\skills\QlikSense\ on Windows or
   ~/.{ai_assistant_name}/skills/QlikSense/ on macOS/Linux, replacing {ai_assistant_name} with
   your config directory such as claude or gemini). Otherwise install locally under
   .agents/skills/QlikSense/ in the project workspace.
3. Place SKILL.md at the QlikSense/ root and copy the entire references/ AND tool/ folders beside
   it. Overwrite any existing files so everything is up to date.

PART B — set up the retrieval tool (required; the skill answers through it):
4. From the installed QlikSense/ folder, run the one-command bootstrap with any Python 3.10+:
     - Windows:      py tool\setup.py
     - macOS/Linux:  python3 tool/setup.py
   This creates a virtual environment, installs dependencies, and builds the search index
   (first run downloads a ~90MB local embedding model once, then works offline; no API key).
5. setup.py prints a `claude mcp add ...` command at the end. Run it to register the MCP server
   (it points at the venv's Python and tool/qlik_mcp_server.py). For non-Claude MCP hosts, add an
   equivalent stdio server entry using that same venv Python and tool/qlik_mcp_server.py.
   The generated Chroma index is stored in the user cache by default
   (`%LOCALAPPDATA%\qlik-ai-skill\index` on Windows, or `$XDG_CACHE_HOME` on
   Unix-like systems when set); set `QLIK_INDEX_DIR` to use a custom index path.
6. Verify: SKILL.md + references/ + tool/ are in place, `tool/setup.py` completed, and (after a
   restart, since MCP tools load at startup) `qlik_knowledge_search` is connected. The skill also
   works immediately via the bundled CLI (tool/qlik_search.py) without a restart. Report what you
   installed and confirm it is ready.
```

### 2. Web-Based AI (Claude Projects, Custom GPTs)

Browser interfaces have no filesystem access, so they run **Part A only** — the retrieval tool needs a local Python runtime. The assistant reads the relevant reference file directly:
1. Download this repository as a ZIP (green **Code** button → **Download ZIP**) and extract it.
2. Upload `SKILL.md` and every markdown file inside `references/` to your Claude Project knowledge base, Custom GPT builder, or equivalent workspace.

### 3. Manual Installation (For Developers)

#### Part A — skill files

Copy the skill into your assistant's skills folder (replace `{ai_assistant_name}`, e.g. `claude` or `gemini`):

| OS | Global path |
|----|-------------|
| Windows | `%USERPROFILE%\.{ai_assistant_name}\skills\QlikSense\` |
| macOS/Linux | `~/.{ai_assistant_name}/skills/QlikSense/` |

For a project-scoped install instead, copy into `.agents/skills/QlikSense/` at your workspace root. Either way, keep this layout (the `tool/` folder must sit beside `SKILL.md` so the skill can find it):

```
QlikSense/
├── SKILL.md
├── references/          # all 18 reference markdown files
└── tool/                # the retrieval tool (Part B)
```

For **Claude Code**, you can also reference `SKILL.md` and the `references/` files from your project's `CLAUDE.md` as additional context sources.

#### Part B — retrieval tool

One command from the installed `QlikSense/` folder builds everything:

```bash
# Windows           macOS/Linux
py tool\setup.py    python3 tool/setup.py
```

It creates `tool/.venv`, installs dependencies, builds the Chroma index when the
local filesystem permits it, and prints the `claude mcp add` command to register
the MCP server. If Chroma SQLite writes are blocked, setup completes in
`chunks.jsonl` fallback mode so CLI/MCP search remains usable. See
[`tool/README.md`](tool/README.md) for details, the `pgvector` team backend, and
the CLI (`tool/qlik_search.py`).

> **Tip:** the `tool/chroma_db/` index and `tool/.venv` are build outputs and are intentionally not committed — each machine builds them locally with `setup.py` (free, no API key). `tool/chunks.jsonl` *is* committed so you can skip re-chunking unless you edit the references.

---

## Usage

Once installed, the AI assistant automatically detects and loads the skill whenever you ask questions related to:
- Writing or debugging Qlik load scripts
- Set Analysis expressions
- Data model design (star schema, QVDs, incremental reloads)
- Chart selection and dashboard design
- Performance issues and optimisation
- Section Access and row-level security
- Qlik Sense Enterprise or Cloud administration
- Komment write-back, Kaptain service, partial reloads from extensions, or write-back to external databases
