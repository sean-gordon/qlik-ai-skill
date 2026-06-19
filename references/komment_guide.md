# Komment Write-Back Extension — Complete Reference

**Product:** Komment by ExtendBI  
**Docs:** https://docs.extendbi.com/komment  
**Support:** info@extendbi.com  
**Latest version:** 2.6.0 (12 Sep 2022)

Komment is a Qlik Sense extension that adds **write-back** capability — users can annotate rows, assign statuses, enter dates, and flag actions directly inside a published Qlik Sense app. The data is stored either as QVDs (via Qlik's QIX Engine) or in an external database (via the Kaptain service). A partial reload then brings the written data back into the app without running a full reload.

---

## 1. Architecture Overview

```
Qlik Sense App
  └─ Komment Extension (chart object)
       │
       ├─ QIX Engine mode  ──→  QVD files on data connection
       │                         (partial reload re-reads QVDs)
       │
       └─ Kaptain mode     ──→  Kaptain Node.js service (port 8000)
                                  └─ External DB: MS SQL / MySQL /
                                     PostgreSQL / Oracle / MongoDB
```

### Connection Mode Comparison

| Capability | QIX Engine | Kaptain |
|---|:---:|:---:|
| Security rules required | Yes | No |
| Concurrent user handling | No | Yes |
| Analyzer license users | No | Yes |
| External database writeback | No | Yes |
| Automatic save (no reload) | No | Yes |
| Additional service install | No | Yes |
| Setup complexity | Low | Medium |

**Rule of thumb:** Use QIX Engine for small deployments or prototypes. Use Kaptain for production, concurrent users, or when Analyzer-licensed users need to write back.

---

## 2. Installation

### 2.1 Komment Extension (QMC)

1. Download the latest Komment ZIP from ExtendBI.
2. In QMC → **Extensions** → Import ZIP.
3. The extension appears under **Custom Objects → Extend BI** in the app editor.
4. Remove any older Komment version before uploading a new one.

**Disable QVD storage** (if Kaptain-only deployment): edit `Settings.txt` inside the ZIP, set `disableQVD = true`, repackage, and re-import.

### 2.2 Kaptain Service Installation (v2.6.0)

**Prerequisites:** Admin rights on the Windows server; port 8000 available; port 4747 inbound open between Kaptain and the Qlik Engine.

```
1. Run Kaptain-installer-2.6.0.exe → select Full Installation
2. Start services in Windows Services:
   - Kaptain DB Service
   - Kaptain Server Service
3. Open http://localhost:8000 → set root password
4. Configure Qlik Hub URL(s)
5. Set Qlik User ID (service account used for Qlik connections)
6. Upload exported Qlik PEM certificates (Client.pem, Client_key.pem, Root.pem)
7. Set Log Level to "info"
8. Submit and confirm
```

**Firewall rule (PowerShell):**
```powershell
New-NetFirewallRule -DisplayName "Kaptain Inbound" -Direction Inbound `
    -LocalPort 8000 -Protocol TCP -Action Allow -Profile Domain
```

#### Kaptain v2.5.0 (manual config)

Edit `C:\Program Files\ExtendBI\Kaptain\config\default.json`:
```json
{
  "corsAllowOrigins": "https://your-qlik-server.domain.com",
  "userId": "DOMAIN\\serviceaccount",
  "COMPANY": "YourCompanyName",
  "qlikHost": "cert",
  "keyFile": "qlik/client_key.pem",
  "caFile": "qlik/root.pem",
  "certFile": "qlik/client.pem"
}
```

### 2.3 Certificate Setup (Qlik → Kaptain)

```
1. QMC → Certificates
2. Add machine name = Kaptain server hostname
3. No password; include secret key; export as PEM format
4. Copy Client.pem, Client_key.pem, Root.pem to:
   C:\Program Files\ExtendBI\Kaptain\config\Qlik\
5. For HTTPS on Kaptain: also export Windows-format certs (with password)
   and copy to C:\Program Files\ExtendBI\Kaptain\config\kaptain\
```

### 2.4 External Database Configuration

Config file: `C:\Program Files\ExtendBI\Kaptain\config\default.json`

**MySQL:**
```json
"mysql": {
    "MYSQL_POOL": 300,
    "MYSQL_SERVER": "your-mysql-host",
    "MYSQL_PORT": 3306,
    "MYSQL_USER": "admin",
    "MYSQL_PASSWORD": "strongpassword",
    "MYSQL_DATABASE": "Kaptain"
}
```

**MS SQL:**
```json
"mssql": {
    "MSSQL_SERVER": "your-mssql-host",
    "MSSQL_PORT": 1433,
    "MSSQL_USER": "admin",
    "MSSQL_PASSWORD": "strongpassword",
    "MSSQL_DATABASE": "Kaptain",
    "DRIVER": "msnodesqlv8",
    "OPTIONS": {
        "encrypt": true,
        "enableArithAbort": true,
        "trustedConnection": false
    }
}
```

**MS SQL — Windows Authentication:** Set `"DRIVER": "msnodesqlv8"` and `"trustedConnection": true`. Requires Microsoft SQL Server 2012 Native Client.

**PostgreSQL:**
```json
"postgresql": {
    "POSTGRE_USER": "postgres",
    "POSTGRE_SERVER": "localhost",
    "POSTGRE_DATABASE": "Kaptain",
    "POSTGRE_PASSWORD": "strongpassword",
    "POSTGRE_PORT": 4432
}
```

**Oracle:**
```json
"oracle": {
    "ORACLE_SERVER": "your-oracle-host",
    "ORACLE_LIB": "C:\\Projects\\instantclient_19_11",
    "ORACLE_PORT": 1521,
    "ORACLE_USER": "admin",
    "ORACLE_PASSWORD": "strongpassword",
    "ORACLE_DATABASE": "ORCL"
}
```

### 2.5 SSL / HTTPS for Kaptain

```
1. Extract OpenSSL to c:\install\openssl\
2. Place your PFX certificate in the same folder
3. Run from an Administrator Command Prompt:
   openssl pkcs12 -in server.pfx -out "c:\install\server.pem" -nokeys -password pass:<password>
   openssl pkcs12 -in server.pfx -out "c:\install\server_key.pem" -nocerts -nodes -password pass:<password>
4. Move server.pem and server_key.pem to \config\kaptain\
5. Restart Kaptain Server Service
```

---

## 3. Load Script

The Komment load script has two responsibilities:
1. Protect the main data model from running during partial reloads.
2. Define placeholder fields for every editable Komment column.

### 3.1 Wrapping the Existing Data Model

```qlik
If not IsPartialReload() then

    // --- Your existing LOAD statements go here ---
    CASES:
    LOAD
        CASEID,
        Country,
        Severity,
        Null() as Status,    // editable Komment field
        Null() as Action,    // editable Komment field
        Null() as Date       // editable Komment field
    FROM [lib://DataConnections/Source.xlsx]
    (ooxml, embedded labels, table is Sheet1);

End if

// AutoCalendar must be OUTSIDE the IsPartialReload block:
// [$(Must_Include=lib://DateCalendar/DateCalendar.qvs)]
```

**Key rules:**
- `Null() as FieldName` creates a column with no data — Komment populates it at runtime.
- If the field already exists in source data, load it normally (without `Null()`).
- To set a default value instead of null: `'Pending' as Status`.
- The `AutoCalendar` script must sit **after** the `End if` — it must run on every reload including partials.
- Reload the app fully after adding new field definitions before configuring them in the Komment UI.

### 3.2 Kaptain — Partial Reload Script (auto-generated)

When using Kaptain, the UI generates a load script block. It uses two variables to support multi-environment deployments:

```qlik
// Environment-aware Kaptain routing
LET vKaptainURL = if(ComputerName()='PROD',
                      'https://kaptain.prod.local:8000/',
                  if(ComputerName()='DEV',
                      'http://localhost:8000/', ''));

LET vKapsuleID  = if(ComputerName()='PROD', '5f0318d0234137223853e87e',
                 if(ComputerName()='DEV',  '5e1209a0234137223853a12f', ''));
```

This eliminates manual URL changes when promoting apps from development to production.

---

## 4. Security Rules (QIX Engine Mode Only)

Three security rules are required in QMC to allow published-app users to write back via Komment. These rules are **not needed** when using Kaptain.

| Rule Name | Resource Filter | Action | Condition |
|---|---|---|---|
| CommentingRole_App | `App_*` | Update | `((user.roles="CommentingRole") and resource.stream.HasPrivilege("read"))` |
| CommentingRole_AppObject | `App.Object_*` | Read | `((user.roles="CommentingRole"))` |
| CommentingRole_DataConnection | `DataConnection_*` | Read | `((user.roles="CommentingRole"))` |

**What each rule does:**
- **App — Update:** Lets Komment save data back into the app's QVD storage.
- **AppObject — Read:** Grants script access needed for the partial reload trigger.
- **DataConnection — Read:** Allows the partial reload to read all data connections referenced in the script.

**After creating the rules:** assign the `CommentingRole` custom property to users in QMC.

---

## 5. Configuration (Komment Property Panel)

### 5.1 Setup Section

| Setting | Purpose | Notes |
|---|---|---|
| **Mode** | Display format | Table / Form / Popup — set at development time; users cannot change it |
| **Fact Table Name** | Data model table for associations | Select from current data model |
| **Writeback Variable Name** | Unique ID for this Komment object | Must be unique per app |
| **Writeback Table Name** | QVD file name / Kapsule name | Must be unique per app and storage location |
| **Custom Date Format** | Date display format | Kaptain only |
| **Ignore Timezone** | Disable timezone conversion | Kaptain only |
| **Server Timezone** | Override server timezone | Kaptain only |

### 5.2 Data Connection Section

| Setting | Purpose | Notes |
|---|---|---|
| **Connection Type** | QIX Engine or Kaptain | See Section 1 comparison |
| **QVD Data Connection** | Folder connection for QVD storage | QIX Engine only |
| **QVD Storage** | Single QVD or separate QVDs per object | Single QVD consolidates all objects |
| **Kaptain URL** | Service endpoint | e.g. `https://kaptain.yourdomain.com:8000/` |
| **Kapsule ID** | Unique Kaptain collection ID | Generated by Kaptain admin console |

---

## 6. Display Modes

Mode is a **development-time decision** — it cannot be changed by end users at runtime.

### Table Mode (default)
Standard grid layout. Supports two editing approaches:
- **Inline editing:** Users click directly on a cell to edit it. Unsaved changes show a change indicator. Users clear or save per row.
- **Batch editing:** Users select multiple rows, click Batch Edit, and apply the same value to all selected records simultaneously.

### Form Mode
Depends on Qlik selections from other sheet objects. Users enter data that applies to all currently selected records. Best for structured data entry workflows.

### Popup Mode
The Komment object renders as a floating button on the sheet. Clicking opens a modal form. Saves screen space when the form is not always needed.

---

## 7. Widgets

Widgets are the individual editable fields within a Komment object. Each widget maps to one field in the Fact Table.

| Widget | Purpose | Key Properties |
|---|---|---|
| **Readonly** | Non-editable display (from Qlik field or expression) | Komment Key Field option; URL display; Total row aggregation |
| **Field** | Hidden data carrier — stores additional data the user does not see | Saves metadata alongside visible fields |
| **Text** | Free-text input | Single-line or multi-line; character limit |
| **Date** | Calendar date picker | Format definition; supports direct typing |
| **Dropdown** | Selection list | Values from: manual list / Qlik field / Qlik variable; supports search; multi-select; user-added options |
| **Group** | Button-group selection | Manual or dynamic values; custom button colours per option |
| **Number** | Numeric input | Type: Number or Percentage; decimal places; increment/decrement controls |
| **Check** | Boolean checkbox | Task-completion toggle |
| **Variable** | Hidden metadata written to backend | Hard-coded or calculated value; not visible to users |
| **Validation** | Conditional input verification | Expression-based rule; custom error message; **not available in Table inline mode** |
| **Container** | Groups widgets in Form/Popup layouts | Controls column/row span using 12-column grid |
| **Notification** | Captures notification recipient data | Field name; user selection list; custom button label |

### Widget Common Settings

**Mode** — Field or Expression: most widgets can reference either a raw Qlik field or a calculated expression (write the expression without a leading `=`).

**Komment Key Field** — mark the first Readonly widget as the key to associate written data back to the correct row. Recommended as the first widget in every Komment object.

**Field names must not contain** `.` or `$` characters. Kapsule names must start with a letter or underscore and cannot include `$` or the `system.` prefix.

---

## 8. Buttons

Five button types are available under the **Buttons** section:

| Button | Default On | Purpose |
|---|:---:|---|
| Submit | Yes | Commits edits and triggers save (+ partial reload for QIX Engine) |
| Clear | Yes | Discards unsaved changes in the current session |
| Add | No | Creates a new blank record |
| Remove | No | Deletes the selected record (sets `_state = removed` — data is preserved for audit) |
| Reset | No | Resets all widgets to blank; Form and Popup modes only |

Each button supports:
- **Custom label** for end-user display.
- **Partial reload toggle** (Submit button; default enabled) — triggers a partial reload after save.
- **Confirmation dialogue** — optional header and message shown before the action executes.

---

## 9. Optional Settings

### 9.1 Conditional Show / Hide

Controls widget visibility based on any Qlik expression. Located in each widget's **Advanced Settings**.

```qlik
// Show only for user with ID "da":
=if(subfield(osuser(), 'Id=', 2) = 'da', -1, 0)

// Always hide a widget (useful for Field widgets):
0
```

**Convention:** `-1` = true (visible); `0` = false (hidden).

### 9.2 Conditional Write

Controls whether a widget is editable for the current user. Same syntax as Conditional Show:

```qlik
// Editable only for user "da":
=if(subfield(osuser(), 'Id=', 2) = 'da', -1, 0)
```

### 9.3 Mandatory Fields

Marks a widget as required — users cannot submit without filling it in. Located in each widget's **Advanced Settings**.

**Limitation:** Mandatory validation does not work in **Table inline mode**.

### 9.4 Freeze Columns

Pins a column so it remains visible when the user scrolls horizontally. Configured per widget in **Advanced Settings**.

### 9.5 Exclude Null Values

Applies to Readonly widgets. Toggle to hide rows where the referenced field is null — mirrors native Qlik Sense table behaviour.

### 9.6 Permission Rules

Object-level read/write access control. Separate from QMC security rules — these control access within the Komment object itself.

| Permission | Controls |
|---|---|
| Read | Which users can see the Komment object's contents |
| Write | Which users can edit data in the Komment object |

```qlik
// Allow write only for users listed in a Komment_Users field:
=if(substringcount(
    concat(upper(Komment_Users), ';'),
    upper(subfield(Osuser(), 'UserId=', 2))
) = 1, -1, 1)
```

Common pattern: load an authorised user list into the data model, then use `concat()` + `substringcount()` to match the current user.

### 9.7 Layout

**Cell colours (dynamic):**
```qlik
// Colour cells based on Action field value using variables:
=pick(match([Action], 'Follow-up', 'Pending', 'No Action'),
      vColor_Bad, vColor_Neutral, vColor_Good)
```

**Custom header colours:** set per widget.

**Column widths:** drag to resize in Table mode, or set in Advanced Settings. In Form/Popup mode, widget width uses a 12-column grid (default: 12 = full width).

**Page size** and **dialogue size** are set under Layout → Appearance.

**Wrap Line:** available on Readonly and Text widgets to prevent text truncation.

### 9.8 Localisation

Customise all button labels and dialogue text via **Appearance → Localizations**. Supports:
- Table button labels (Submit, Clear, Add, Remove, Reset).
- Discard changes confirmation dialogue text.

### 9.9 Utilities

| Utility | What it does |
|---|---|
| Batch Edit | Allow multi-row simultaneous editing (enabled by default in Table mode) |
| Excel Export | Adds an export icon — downloads current table as XLSX |
| Column Filter | Users can show/hide columns (session-only; resets when app closes) |
| CSS Styling | Apply custom CSS scoped to: Current Object / All Komment Objects / Entire App |

---

## 10. Audit Trail

Komment automatically tracks every write-back operation.

### What is captured

| Field | Contains |
|---|---|
| `Komment_<ObjectName>.CreatedBy` | User ID who made the change (encoded string) |
| `Komment_<ObjectName>.CreatedAt` | Timestamp of the change (numeric) |
| `Komment_<ObjectName>._state` | Record state: `new`, `modified`, or `removed` |

### Displaying audit data in expressions

```qlik
// Extract readable username:
=SubField([Komment_DEMO2.CreatedBy], 'Id=', 2)

// Display timestamp:
=timestamp([Komment_DEMO2.CreatedAt])

// If your locale uses comma as decimal separator:
=timestamp(Replace([Komment_DEMO2.CreatedAt], '.', ','))
```

### Centralised audit app

Audit trail QVDs from multiple Komment objects across different apps can be loaded into a single master audit application for organisation-wide change tracking.

---

## 11. Multiple Qlik Sense Sites (Dev/Prod)

Use `ComputerName()` in the load script to dynamically switch between environments — eliminates manual changes when promoting apps:

```qlik
LET vKaptainURL = if(ComputerName() = 'PROD-SERVER',
                     'https://kaptain.prod.local:8000/',
                 if(ComputerName() = 'DEV-SERVER',
                     'http://localhost:8000/', ''));

LET vKapsuleID  = if(ComputerName() = 'PROD-SERVER', 'PROD_KAPSULE_ID',
                 if(ComputerName() = 'DEV-SERVER',   'DEV_KAPSULE_ID', ''));
```

### Deployment workflow

**First-time production deploy:**
1. Export app from development QMC.
2. Import and run a full reload on production.

**Updating an existing app:**
1. If Komment widget configuration changed: export the Kapsule from dev Kaptain admin as `.kap`, import on production Kaptain. Note: `.kap` files contain structure only, not data.
2. Replace the Kapsule on production before reloading and publishing.

---

## 12. Qlik SaaS Configuration

### Extension versions

| Version | Description |
|---|---|
| Komment | All files bundled in ZIP — may require browser refreshes on first use |
| Komment-Remote | Files hosted on ExtendBI AWS — lighter and faster; contact ExtendBI to request |

### Content Security Policy (QMC)

After importing the extension in the SaaS management console, add to **Content Security Policy**:

| Directive | Origin | Required for |
|---|---|---|
| `connect-src` + `connect-src (web-socket)` | `app.cryptolens.io` | License validation (both versions) |
| `connect-src, font-src, img-src, script-src, style-src` | `extendbi-qlik-remote-dev.s3.eu-north-1.amazonaws.com` | Komment-Remote version only |

### SaaS load script difference

In SaaS, the auto-generated script uses `DataFiles/` (forward slashes) instead of `\\` used in QSEoW. Replace any `"undefined"` or `"undefined/"` placeholders with your chosen Data Storage name (e.g. `"DataFiles"`).

### User ID format

In Qlik SaaS, use the **IdP Subject** format for user identification (instead of `DOMAIN\initials` used in QSEoW).

---

## 13. Kaptain Admin Module

Access the Kaptain admin console at `http://<server>:8000` (or HTTPS equivalent).

### Admin capabilities

**Users:**
- Create / update / delete users.
- Assign roles: USER or ADMIN.
- Set Qlik User ID format: `UserDirectory\initials` (case-sensitive; use IdP Subject for SaaS).
- Grant or restrict Kapsule creation rights.

**Groups:**
- Define read/write permissions for group members.
- Assign Kapsules and users to groups.
- Note: object-level permissions are still managed inside the Komment extension itself.

**API Keys:**
- Generate API keys for secure Komment ↔ Kaptain integration.
- Embed the key in the Komment extension's `Settings.txt` file.
- For data connections created before v2.5.2: add an `Authorization: Bearer <API Key>` header to the REST connection.
- Create separate API keys per Kaptain server instance to simplify key rotation.

### User capabilities

Users (non-admin) can:
- View Kapsules they own or belong to their groups (Name, ID, Related Komment Table, Key Field, Owner, last update).
- Sort, search, and filter Kapsules.
- Delete individual Granules (rows) or entire Kapsules.
- Export Kapsule structure as `.kap` / import from `.kap`.
- Access Logs to verify reload execution and troubleshoot.

---

## 14. Troubleshooting Quick Reference

| Symptom | Likely cause | Fix |
|---|---|---|
| Written data not appearing after save | Partial reload not triggered / security rules missing | Check CommentingRole assignment; verify partial reload toggle is on |
| "Extension not ready" on first SaaS load | SaaS needs time to internalise the extension | Refresh browser 2–3 times |
| Kaptain API call fails | Missing or expired API key | Regenerate key in Kaptain admin; update Settings.txt |
| Mandatory validation not enforcing | Widget in Table inline mode | Switch to Form/Popup mode or use Batch Edit mode |
| Validation widget not working | Used in Table mode | Validation widget is only supported in Form and Popup modes |
| Wrong environment Kapsule loaded | ComputerName() not matching | Verify `ComputerName()` returns the expected server name in a Qlik text object |
| QVD not updating on partial reload | AutoCalendar inside IsPartialReload block | Move AutoCalendar script outside / after the `End if` |
| Timestamp displays as number | Locale decimal separator mismatch | Use `timestamp(Replace([Field],'.',','))` |
| Concurrent-user write conflicts | QIX Engine in use | Migrate to Kaptain for concurrent user support |

---

## 15. Version History (key milestones)

| Version | Date | Highlights |
|---|---|---|
| 2.6.0 | Sep 2022 | CDN support for SaaS; API key security; partial reload visibility controls |
| 2.5.0 | Oct 2021 | Kapsule import/export; Windows Integrated Auth; MySQL/PostgreSQL/Oracle writeback |
| 2.4.0 | Jun 2021 | Notification widget; admin user management; widget-level permission rules; conditional show changed to `-1`/`0` syntax |
| 2.3.0 | Apr 2021 | CSS styling; batch edit; Reset button; Total row; keyboard shortcuts |
| 2.2 | Oct 2020 | Native Qlik selection; Excel export; column freeze; dynamic Kaptain parameters |
| 2.1 | Jul 2020 | Kaptain connection type; Add/Remove buttons; read/write permission rules; "Select" widget renamed "Dropdown" |
