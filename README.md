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
└── tool/                                 # Optional semantic-search retrieval tool
    ├── build_chunks.py                   # References → retrievable chunks
    ├── build_index.py                    # Embed + index (local or pgvector)
    ├── qlik_mcp_server.py                # MCP server: qlik_knowledge_search
    ├── chunks.jsonl                      # Pre-built chunks
    ├── requirements.txt
    └── README.md                         # Tool setup guide
```

**v4.0 change:** The two largest references (`functions_reference.md`,
`advanced_patterns.md`) were split into focused files so any single read stays
small, and an optional retrieval tool was added. With the tool connected, Claude
searches the corpus and pulls only the passages it needs (~1,500 tokens) instead
of loading whole files (7k–14k tokens). See `tool/README.md`.

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

The skill works in two parts:

- **Part A — the skill itself** (`SKILL.md` + `references/`). This is all you need. With it installed, the assistant reads the relevant reference file directly when answering Qlik questions.
- **Part B — the optional retrieval tool** (`tool/`). It indexes the references so the assistant pulls only the passages it needs (~1,500 tokens) instead of loading a whole file (7k–14k). Recommended if your assistant supports MCP (e.g. Claude Code), but not required.

For non-technical users, the easiest way to install is to let your AI assistant do it for you. Copy the prompt below; it covers both parts.

### 1. Agentic AI Assistants (Claude Code, Antigravity, Aider, etc.)

If your AI assistant can run terminal commands and write files, paste this prompt. It downloads, installs, builds, and registers everything.

**Copy and paste this prompt:**
```text
Please install or update the Qlik Sense AI skill from the public repository at
https://github.com/sean-gordon/qlik-ai-skill

PART A — install the skill files (required):
1. Clone or download the repository (SKILL.md, the references/ folder, and the tool/ folder).
2. Identify the correct skills path for your host. If you support global skills, install to the
   global folder (e.g. %USERPROFILE%\.{ai_assistant_name}\skills\QlikSense\ on Windows or
   ~/.{ai_assistant_name}/skills/QlikSense/ on macOS/Linux, replacing {ai_assistant_name} with
   your config directory such as claude or gemini). Otherwise install locally under
   .agents/skills/QlikSense/ in the project workspace.
3. Place SKILL.md at the QlikSense/ root and copy the entire references/ folder beside it.
   Overwrite any existing files so everything is up to date.

PART B — set up the retrieval tool (optional but recommended if you support MCP):
4. From the tool/ folder, create an isolated Python virtual environment (Python 3.10+; the
   Windows "py" launcher or python3 both work) and install dependencies into it:
     - Windows:      py -m venv .venv ; .\.venv\Scripts\python.exe -m pip install -r requirements.txt
     - macOS/Linux:  python3 -m venv .venv ; ./.venv/bin/python -m pip install -r requirements.txt
5. Build the search index (this downloads a ~90MB embedding model once, then runs offline; no API key):
     - Windows:      .\.venv\Scripts\python.exe build_index.py --backend chroma
     - macOS/Linux:  ./.venv/bin/python build_index.py --backend chroma
6. Register the MCP server with your host, using the venv's Python interpreter (NOT a bare
   "python3" — the dependencies live in the venv). For Claude Code, run:
     claude mcp add qlik-knowledge --scope user \
       --env QLIK_BACKEND=chroma \
       --env QLIK_INDEX_DIR="<absolute path to the tool folder>" \
       -- "<absolute path to the venv python>" "<absolute path to tool/qlik_mcp_server.py>"
   For other MCP hosts, add an equivalent stdio server entry pointing the command at the venv
   Python and tool/qlik_mcp_server.py, with the same two env vars.
7. Verify: confirm SKILL.md + references/ are in place, and (if you did Part B) that the
   qlik_knowledge_search and qlik_knowledge_domains tools are connected. Restart the assistant
   if MCP tools only load at startup. Report what you installed and confirm it is ready.
```

### 2. Web-Based AI (Claude Projects, Custom GPTs)

Browser interfaces have no filesystem access, so use the skill files only (Part A — the retrieval tool needs a local Python runtime and cannot run here):
1. Download this repository as a ZIP (green **Code** button → **Download ZIP**) and extract it.
2. Upload `SKILL.md` and every markdown file inside `references/` to your Claude Project knowledge base, Custom GPT builder, or equivalent workspace.

### 3. Manual Installation (For Developers)

#### Part A — skill files

Copy the skill into your assistant's skills folder (replace `{ai_assistant_name}`, e.g. `claude` or `gemini`):

| OS | Global path |
|----|-------------|
| Windows | `%USERPROFILE%\.{ai_assistant_name}\skills\QlikSense\` |
| macOS/Linux | `~/.{ai_assistant_name}/skills/QlikSense/` |

For a project-scoped install instead, copy into `.agents/skills/QlikSense/` at your workspace root. Either way, keep this layout:

```
QlikSense/
├── SKILL.md
├── references/          # all 18 reference markdown files
└── tool/                # only needed for Part B
```

For **Claude Code**, you can also reference `SKILL.md` and the `references/` files from your project's `CLAUDE.md` as additional context sources.

#### Part B — retrieval tool (optional)

See [`tool/README.md`](tool/README.md) for the full setup. In short, from the `tool/` folder: create a venv, `pip install -r requirements.txt`, run `build_index.py --backend chroma`, then register the MCP server (pointing at the venv Python) per the commands in the prompt above. A `pgvector` backend is available for teams sharing one central index.

> **Tip:** the `tool/chroma_db/` index is a build output and is intentionally not committed — each machine builds it locally with `build_index.py` (free, no API key). `tool/chunks.jsonl` *is* committed so you can skip re-chunking unless you edit the references.

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
