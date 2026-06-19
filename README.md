# Qlik Sense AI Skill

A comprehensive, reusable knowledge skill for AI coding assistants to provide **senior-developer-level** Qlik Sense support — covering scripting, data modelling, Set Analysis, visualisation design, performance optimisation, Section Access, and system debugging.

---

## File Structure

```
qlik-ai-skill/
├── SKILL.md                           # Main skill configuration and quick-reference index
└── references/
    ├── scripting_knowledgebase.md     # Backend load script encyclopaedia
    ├── expression_knowledgebase.md    # Frontend expressions encyclopaedia
    ├── visualization_guide.md         # Chart selection, design, and styling guide
    ├── debugging_guide.md             # Debugging, error handling, and admin guide
    ├── functions_reference.md         # Complete function reference (from official Qlik docs)
    ├── advanced_patterns.md           # Advanced patterns and cookbook recipes
    └── komment_guide.md               # Komment write-back extension — full implementation guide
```

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

For non-technical users, the easiest way to install this skill is to let your AI assistant do it for you. Depending on the type of AI you are using, follow the relevant guide below.

### 1. Agentic AI Assistants (Claude Code, Antigravity, Aider, etc.)
If your AI assistant has the ability to run terminal commands and write files, copy and paste the prompt below. The AI will download, configure, and install the skill for you automatically.

**Copy and paste this prompt:**
```text
Please install or update the Qlik Sense AI skill from the public repository at https://github.com/sean-gordon/qlik-ai-skill

To do this:
1. Clone or download the repository files (both SKILL.md and all files in the references/ folder).
2. Identify the correct installation path. If you support global configuration skills, install them in the global folder (e.g. %USERPROFILE%\.{ai_assistant_name}\config\skills\QlikSense\ on Windows or ~/.{ai_assistant_name}/config/skills/QlikSense/ on macOS/Linux, replacing {ai_assistant_name} with your configuration directory, such as gemini). Otherwise, install them locally in the project workspace under .agents/skills/QlikSense/.
3. Overwrite any existing files to ensure everything is up to date.
4. Verify the installation is complete and confirm it is ready for use.
```

### 2. Web-Based AI (Claude Projects, Custom GPTs)
If you are using a web browser interface that does not have direct access to your computer's filesystem, you can upload the files manually:
1. Download this repository as a ZIP file (click the green **Code** button at the top of this page, then select **Download ZIP**).
2. Extract the ZIP file on your computer.
3. Upload `SKILL.md` and all the markdown files inside the `references/` folder to your Claude Project knowledge base, Custom GPT builder, or equivalent AI workspace.

### 3. Manual Installation (For Developers)

If you prefer to install the files manually:

#### Global Installation
Copy the repository contents to your global AI assistant skills folder (replace `{ai_assistant_name}` with your tool's directory name, e.g. `gemini` or `claude`):

**Windows:**
```
%USERPROFILE%\.{ai_assistant_name}\config\skills\QlikSense\
```

**macOS/Linux:**
```
~/.{ai_assistant_name}/config/skills/QlikSense/
```

Ensure the directory structure is:
```
QlikSense/
├── SKILL.md
└── references/
    ├── debugging_guide.md
    ├── expression_knowledgebase.md
    ├── scripting_knowledgebase.md
    └── visualization_guide.md
```

#### Project-Specific (Workspace) Installation
1. Navigate to your workspace root.
2. Create the directory: `.agents/skills/QlikSense/`
3. Copy all files from this repository into that folder.

#### Claude Code
Place `SKILL.md` content in your `CLAUDE.md`, or reference the files from your project's `CLAUDE.md` as additional context sources.

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
