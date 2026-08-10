# table.html — Behavior Documentation

## Purpose

An interactive Hebrew-language data table for the Oct 7 database (`oct7database.com`).  
Loads victim data from remote CSVs, renders a filterable/searchable DataTables table, and embeds a map (`locations.html`) when a single row is in view.

---

## Data Sources

Two CSV files are fetched at page load via **PapaParse** (in sequence):

1. **Geni enrichment data**  
   `https://raw.githubusercontent.com/yuval-harpaz/alarms/refs/heads/master/data/geni.csv`  
   - Columns used: `pid`, `geni` (a Geni.com profile URL)  
   - Loaded first; stored in a `geniMap` object keyed by `pid`

2. **Main database**  
   `https://raw.githubusercontent.com/yuval-harpaz/alarms/refs/heads/master/data/oct7database.csv`  
   - All display logic operates on this data after geni data is merged

---

## Column Handling

### Hidden Columns

The following columns are loaded from the CSV but **not shown** in the table:

```
first name, last name, middle name, nickname,
Event location, Event location class,
Death location, Death location class
```

### Added Column

- **`geni`** — appended as the last column; populated from `geniMap[row.pid]`; rendered as a clickable link showing the last path segment of the Geni URL

### Quote Sanitization (pre-render)

Before rendering, ASCII double-quotes (`"`) in these columns are replaced with the Hebrew Gereshayim character (`״`) to prevent DataTables search breakage:
- `מקום המוות`
- `מקום האירוע`
- `Death location`
- `Event location`

---

## Column Translations

### Column Header Translations (English → Hebrew)

| CSV Column     | Displayed As      |
|----------------|-------------------|
| `front`        | חזית              |
| `Status`       | סטטוס             |
| `Role`         | תפקיד             |
| `Country`      | ארץ               |
| `Gender`       | מין               |
| `Age`          | גיל               |
| `Party`        | מסיבה             |
| `Residence`    | מקום מגורים       |
| `Event date`   | תאריך אירוע       |
| `Death date`   | תאריך פטירה       |

All other column names are displayed as-is (including Hebrew column names from the CSV).

### Cell Value Translations

#### `Gender` column

| CSV Value | Displayed As |
|-----------|-------------|
| `F`       | נ            |
| `M`       | ז            |

#### `front` column

| CSV Value    | Displayed As       |
|--------------|--------------------|
| `Accident`   | תאונה              |
| `Gaza`       | עזה                |
| `Home`       | עורף               |
| `Iran`       | איראן              |
| `Iraq`       | עיראק              |
| `Jordan`     | ירדן               |
| `North`      | צפון               |
| `Other`      | אחר                |
| `West Bank`  | יהודה ושומרון      |
| `Yemen`      | תימן               |

#### `Status` column

Values may be semicolon-separated composites (e.g. `killed;returned`). Each part is translated individually then re-joined with `; `.

| CSV Value    | Displayed As |
|--------------|-------------|
| `kidnapped`  | נחטף         |
| `killed`     | נהרג         |
| `returned`   | הוחזר        |
| `released`   | שוחרר        |
| `died`       | נפטר         |
| `rescued`    | חולץ         |
| `retrieved`  | הושב         |

#### `Age` column

Parsed as integer (`parseInt`); non-numeric values become empty string.

#### `הנצחה` column

Any `http://` or `https://` URL found in the cell value is wrapped in a clickable `<a target="_blank">` tag.

#### `הספריה הלאומית` column

Cell value is treated as a National Library authority ID and wrapped as:  
`https://www.nli.org.il/he/authorities/<value>`

---

## Filters

### 1. Free Text Search

- Input: `#globalSearch`
- Uses DataTables built-in `table.search(value).draw()` — searches all visible columns simultaneously

### 2. Dropdown Multi-Select Filters (auto-generated)

For each column that meets all these criteria, a checkbox dropdown filter is generated:
- Has more than 1 unique value
- Fewer than 50 unique values
- Max value string length < 30 characters
- Column name does not contain `location class` or `date`

The dropdown shows translated values (same translations as cell rendering). All checkboxes start checked (= no filter).

**Filter logic (custom DataTables search function):**
- If all values checked → `columnFilters[idx] = null` → no filtering
- If none checked → `columnFilters[idx] = []` → all rows hidden
- If some checked → only rows whose cell value (after translation) is in the checked set pass

HTML entities in checkbox values are decoded before comparison.

### 3. Date Range Filters (auto-generated)

For each column whose name contains `date` (case-insensitive), a `min date / max date` input pair is generated. Defaults:
- min: `2023-10-07`
- max: today's date

**Filter logic:**
- Empty cell value → row passes (not filtered out)
- Year-only values (e.g. `"2023"`) → compared against the year of min/max
- Full date strings → parsed as `Date` objects and compared

### 4. Memorial Site Filter (`אתר הנצחה`)

A manually-defined dropdown with checkboxes for known memorial sites. Filters on the `הנצחה` column by URL substring:

| Checkbox Label           | URL substring matched           |
|--------------------------|----------------------------------|
| חללי צה"ל                | `idf.il`                        |
| ביטוח לאומי (אזרחים)     | `laad.btl.gov.il`               |
| משטרת ישראל              | `lezichram.police.gov.il`       |
| שב"כ                     | `shabak.gov.il`                 |
| יזכור                    | `izkor.gov.il`                  |
| אחר / ללא                | empty cell OR no known site URL |

All start checked. If all checked → `memorialFilterValues = null` → no filter.

### 5. PID Row Selection Filter

Clicking a table row sets `selectedPid` to that row's `pid` value and redraws the table.  
A custom DataTables search function then passes only the row whose `pid` column exactly equals `selectedPid`.  
This effectively isolates a single person's row.

### Filter Execution Order

All custom search functions are pushed to `$.fn.dataTable.ext.search` and execute on every `table.draw()`. The order is:
1. PID exact match filter
2. Memorial site filter
3. Multi-select column filters
4. Date range filters (one per date column, pushed dynamically)

DataTables built-in text search runs alongside these.

---

## Reset Button

Clicking **איפוס** (Reset):
1. Sets `selectedPid = null` (clears PID filter)
2. Clears global search input and DataTables search state
3. Checks all multi-select checkboxes
4. Checks all memorial checkboxes
5. Resets all date inputs to defaults (`2023-10-07` → today)
6. Hides the embedded map
7. Calls `table.draw()`

---

## Map Integration (`locations.html?pid=<num>`)

After every `table.draw()`, a `draw` event handler checks:

```javascript
var visibleRows = table.rows({ filter: 'applied' }).data().length;
if (visibleRows === 1 && selectedPid !== null) { ... }
```

**Condition:** exactly 1 row is visible **AND** `selectedPid` is set (i.e. the single row is the result of an intentional click, not a coincidental free-text match).

**Action:**
1. Gets the `pid` of the single visible row
2. Sets `$('#map-iframe').attr('src', 'locations.html?pid=' + pid)`
3. Shows `#map-container` (a `<div>` containing the iframe)

When multiple rows are visible, `#map-container` is hidden.

### How `locations.html` handles `?pid=<num>`

`locations.html` reads the `pid` URL parameter on load:
```javascript
const urlParams = new URLSearchParams(window.location.search);
const pidParam = urlParams.get('pid');
```
After a 500 ms delay (to ensure map tiles load), it calls `focusOnPid(pidParam)` which:
- Searches all map features for a matching `pid` (features can have comma-separated PIDs like `"283,287"`)
- Normalizes by stripping `.0` suffixes
- For point markers: calls `map.setView(latlng, 17)` and opens the popup
- For polygon areas: centers on bounds at zoom 15 and opens the popup
- Also hides the welcome popup overlay when `pid` is in the URL

---

## XLSX Export

Two buttons are available:

| Button                        | Behavior                                                      |
|-------------------------------|---------------------------------------------------------------|
| הורד את כל הטבלה (XLSX)       | Exports all rows in `data` array (unfiltered)                 |
| הורד נתונים מסוננים (XLSX)    | Exports only rows currently visible after all filters applied |

Both apply the same cell transformations (translations, Age parsing) as the table display.  
SheetJS (`xlsx@0.18.5`) is loaded lazily from CDN if not already present.

---

## Column Resizing

Each `<th>` gets an absolutely-positioned `<div class="resizer">` appended after DataTables initializes (100 ms timeout).  
Dragging the resizer sets explicit `width`, `min-width`, `max-width` on the `<th>`.  
Direction is inverted for RTL: dragging right decreases width.  
After resize, sticky column positions are recalculated.

---

## Sticky Columns

The first three columns are sticky (RTL layout):
- Column 1: `right: 0`
- Column 2: `right: <col1 width>px`
- Column 3: `right: <col1 width + col2 width>px`

Positions are recalculated after column resize.

---

## DataTables Configuration

```javascript
$('#oct7table').DataTable({
    dom: 'lrt',    // hides default search box and length menu; shows only: length, table, processing
    order: [],     // no default sort
    paging: false, // all rows shown, no pagination
    autoWidth: false
});
```

---

## Dependencies

| Library          | Version  | Source                               |
|------------------|----------|--------------------------------------|
| jQuery           | 3.7.1    | code.jquery.com CDN                  |
| jQuery UI        | 1.13.2   | code.jquery.com CDN                  |
| DataTables       | 1.13.6   | cdn.datatables.net                   |
| PapaParse        | 5.4.1    | cdn.jsdelivr.net                     |
| SheetJS (xlsx)   | 0.18.5   | cdn.jsdelivr.net (lazy-loaded)       |

---

## Replication Notes

To replicate on another host:
1. The two CSV URLs must remain accessible (or be replaced with local equivalents)
2. The `locations.html` file must be served from the **same origin** as `table.html` (used in an iframe — cross-origin iframes will be blocked by most browsers)
3. All column translations are hardcoded in the `translations` object — update if CSV column names change
4. The `hideCols` array controls which CSV columns are invisible — update to match your CSV schema
5. The memorial site filter is hardcoded — update the `value` substrings if memorial URL patterns change
6. The `pid` column must exist in the CSV and must be unique per person; it is the join key between the table and the map

