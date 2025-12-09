# Design Documentation

## Overview

This document provides technical details and code coordinates for the Workflow Execution Dashboard. Use this as a reference for understanding the architecture, key implementation details, and where to find specific functionality in the codebase.

## Architecture

### Configuration-Driven Design

The dashboard uses a YAML-based configuration system that externalizes all settings:

- **Configuration File**: `chart.yaml:1-40`
- **Parser**: `visualize.py:6-20` - Reads and validates YAML configuration
- **Dataset Config**: `chart.yaml:4-40` - Each dataset has independent settings

### Data Flow

```
chart.yaml → visualize.py → EMBEDDED_DATA (JSON) → workflow_dashboard.html
     ↓              ↓                                        ↓
CSV files    Pandas DataFrame                      Plotly.js visualization
```

**Key transformations:**
1. `visualize.py:29-47` - Read CSV files referenced in chart.yaml
2. `visualize.py:42` - Convert DataFrame to JSON dict: `df.to_dict('records')`
3. `visualize.py:424` - Embed JSON in HTML as `EMBEDDED_DATA` constant
4. `workflow_dashboard.html:614-665` - Load embedded data into JavaScript

## Key Components

### 1. YAML Configuration System

**File**: `chart.yaml`

**Structure**:
- Title: `chart.yaml:1`
- Datasets array: `chart.yaml:3-40`
- Per-dataset configuration:
  - Name (unique ID): `chart.yaml:4`
  - Label (display name): `chart.yaml:5`
  - CSV file path: `chart.yaml:6`
  - X-axis config: `chart.yaml:7-9`
  - Y-axis config: `chart.yaml:10-12`
  - Filters array: `chart.yaml:13-24`

**Parser Implementation**: `visualize.py:6-20`
- Validation for missing file
- Validation for empty datasets array
- Error handling with user-friendly messages

### 2. Multi-Select Data Points

**Click Handler**: `workflow_dashboard.html:786-804`
```javascript
document.getElementById('plot').on('plotly_click', function(data) {
    const point = data.points[0];
    const pointData = {};
    const columns = DATASET_METADATA[filters.dataset].columns;
    columns.forEach((col, idx) => {
        pointData[col] = point.customdata[idx];
    });

    const pointId = JSON.stringify(pointData);

    if (selectedPoints.has(pointId)) {
        selectedPoints.delete(pointId);
    } else {
        selectedPoints.add(pointId);
    }

    updateDataTable();
});
```

**Selected Points Storage**: `workflow_dashboard.html:435`
- Uses JavaScript `Set` for uniqueness
- Point ID is JSON stringified entire row
- Survives filtering (points remain selected)
- Cleared on dataset change: `workflow_dashboard.html:907`

**Table Display**: `workflow_dashboard.html:822-858`
- Function: `updateDataTable()`
- Builds HTML table from selected points
- Updates count badge: `workflow_dashboard.html:827`
- Enables/disables export button: `workflow_dashboard.html:828`

### 3. CSV Export

**Export Function**: `workflow_dashboard.html:861-891`
```javascript
function exportToCSV() {
    if (selectedPoints.size === 0) return;

    const selectedData = Array.from(selectedPoints).map(pointId => JSON.parse(pointId));
    const columns = Object.keys(selectedData[0]).filter(c => c !== '_dataset');

    // Build CSV with proper escaping
    let csv = columns.join(',') + '\n';
    selectedData.forEach(point => {
        const row = columns.map(col => {
            const value = point[col] || '';
            // Escape commas and quotes
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                return '"' + value.replace(/"/g, '""') + '"';
            }
            return value;
        });
        csv += row.join(',') + '\n';
    });

    // Download via Blob API
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'selected_data.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
```

**CSV Escaping Rules**:
- Strings with commas → wrap in double quotes
- Strings with quotes → escape with double quotes (`"` becomes `""`)
- Empty values → empty string

### 4. Dynamic Filter Generation

**Filter Metadata Building**: `workflow_dashboard.html:654-660`
```javascript
const filterMetadata = {};
datasetCfg.filters.forEach(filterCfg => {
    const column = filterCfg.column;
    filterMetadata[column] = [...new Set(datasetData.map(d => d[column]))].sort();
});
datasetFilterMetadata[datasetName] = filterMetadata;
```

**Filter UI Generation**: `workflow_dashboard.html:526-569`
- Reads filter config from YAML
- Dynamically creates filter sections
- First 2 filters expanded by default: `workflow_dashboard.html:546`
- Remaining filters collapsed
- Each filter gets "All" / "None" buttons

**Filter Application**: `workflow_dashboard.html:689-808`
```javascript
function applyFilters() {
    const filters = getSelectedFilters();
    const datasetCfg = CHART_CONFIG.datasets.find(d => d.name === filters.dataset);

    // Filter data
    let filteredData = allData.filter(row => row._dataset === filters.dataset);

    // Apply each configured filter
    datasetCfg.filters.forEach(filterCfg => {
        const column = filterCfg.column;
        if (filters[column]) {
            filteredData = filteredData.filter(row => filters[column].includes(row[column]));
        }
    });

    // Update scatter plot, histogram, and enable click handlers
}
```

### 5. Histogram with Percentiles

**Percentile Calculation**: `workflow_dashboard.html:452-460`
```javascript
function calculatePercentiles(durations, percentiles) {
    const sorted = [...durations].sort((a, b) => a - b);
    const results = {};
    percentiles.forEach(p => {
        const index = Math.ceil((p / 100) * sorted.length) - 1;
        results[p] = sorted[Math.max(0, index)];
    });
    return results;
}
```

**Histogram Rendering**: `workflow_dashboard.html:463-523`
- Uses Plotly histogram trace
- Adds vertical lines for percentiles: `workflow_dashboard.html:489-498`
- Color coding:
  - 50th: Green solid (`#4daf4a`)
  - 75th: Orange dashed (`#ff7f00`)
  - 95th: Red dashed (`#e41a1c`)
  - 97th: Purple dotted (`#984ea3`)

**Percentile Info Display**: `workflow_dashboard.html:516-522`
- Shows numeric values below histogram
- Updates with filtered data
- Formatted to 2 decimal places

### 6. Collapsible Panels

**CSS Implementation**: `visualize.py:144-178`
```css
.histogram-container.collapsed {
    width: 50px;
    padding: 10px;
}
.histogram-container.collapsed .histogram-content {
    display: none;
}
```

**Toggle Function**: `workflow_dashboard.html:446-449`
```javascript
function togglePanel(panelId) {
    const panel = document.getElementById(panelId);
    panel.classList.toggle('collapsed');
}
```

**Collapse Buttons**: `visualize.py:377-379`, `visualize.py:387-389`
- Positioned in panel headers
- Arrow icon rotates 180° when collapsed: `visualize.py:207-209`

### 7. Per-Dataset Configuration

**Axis Configuration**: `workflow_dashboard.html:635-652`
```javascript
const xColumn = datasetCfg.x_axis.column;
const yColumn = datasetCfg.y_axis.column;

const xValues = datasetData.map(d => new Date(d[xColumn]));
const yValues = datasetData.map(d => parseFloat(d[yColumn]));

// Calculate ranges with 5% padding
const xPadding = (maxX - minX) * 0.05;
const yPadding = (maxY - minY) * 0.05;

datasetAxisRanges[datasetName] = {
    xaxis: [new Date(minX.getTime() - xPadding), new Date(maxX.getTime() + xPadding)],
    yaxis: [minY - yPadding, maxY + yPadding]
};
```

**Axis Labels**: `workflow_dashboard.html:756-763`
```javascript
const layout = {
    xaxis: {
        title: datasetCfg.x_axis.label,  // From YAML
        range: axisRanges.xaxis
    },
    yaxis: {
        title: datasetCfg.y_axis.label,   // From YAML
        range: axisRanges.yaxis
    },
    // ...
};
```

### 8. Configurable Color Grouping

**Overview**: Allows users to dynamically choose which attribute determines data point colors, enabling different analytical perspectives (by user, team, SLA status, etc.).

**UI Component**: `visualize.py:400-406`
```python
<div class="filter-section">
    <h3 onclick="toggleSection(this)">🎨 Color By</h3>
    <div class="filter-content">
        <select id="color-by-select" class="filter-select" onchange="onColorByChange()">
        </select>
    </div>
</div>
```

**State Variables**: `visualize.py:445-446`
```javascript
let colorGroupBy = null;  // Track which attribute determines color
let colorMap = {};  // Map attribute values to colors
```

**Populate Dropdown**: `visualize.py:548-559`
```javascript
// Populate Color By dropdown with filter columns
const colorBySelect = document.getElementById('color-by-select');
colorBySelect.innerHTML = '';
datasetCfg.filters.forEach((filterCfg, index) => {
    const option = document.createElement('option');
    option.value = filterCfg.column;
    option.textContent = filterCfg.label;
    colorBySelect.appendChild(option);
});
// Set default to first filter column
colorGroupBy = datasetCfg.filters[0]?.column;
colorBySelect.value = colorGroupBy;
```

**Color Application Logic**: `visualize.py:728-748`
```javascript
// Use colorGroupBy for grouping and coloring
const groupColumn = colorGroupBy || datasetCfg.filters[0]?.column || 'user_name';

// Group by the selected color attribute
const dataByGroup = {};
filteredData.forEach(row => {
    const groupValue = row[groupColumn];
    if (!dataByGroup[groupValue]) {
        dataByGroup[groupValue] = [];
    }
    dataByGroup[groupValue].push(row);
});

// Get unique values for coloring
const uniqueGroups = [...new Set(filteredData.map(r => r[groupColumn]))].sort();

// Build color map for consistent coloring
colorMap = {};
uniqueGroups.forEach((value, idx) => {
    colorMap[value] = COLOR_PALETTE[idx % COLOR_PALETTE.length];
});
```

**Change Handler**: `visualize.py:941-946`
```javascript
// Handle color by change
function onColorByChange() {
    const colorBySelect = document.getElementById('color-by-select');
    colorGroupBy = colorBySelect.value;
    applyFilters();  // Rebuild chart with new coloring
}
```

**Color Palette**: `visualize.py:427-430`
```javascript
const COLOR_PALETTE = [
    '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00',
    '#ffff33', '#a65628', '#f781bf', '#999999', '#66c2a5'
];
```

**Use Cases**:
- Color by SLA Status → Identify SLA violations visually
- Color by User → Compare individual performance
- Color by Team → Analyze team-level patterns
- Color by Location → Identify geographic issues

### 9. SLA Tracking

**Overview**: Built-in support for tracking Service Level Agreement compliance through `expected_duration` and `is_sla_met` columns.

**Data Generation**: `generate_data.py:35-37`, `generate_data2.py:35-37`
```python
# SLA attributes
expected_duration = round(random.uniform(150, 250), 2)  # Expected SLA duration
is_sla_met = 'Yes' if duration <= expected_duration else 'No'
```

**CSV Columns**:
- `expected_duration`: Target completion time (float, in seconds)
- `is_sla_met`: Compliance indicator (string, "Yes" or "No")

**Configuration**: `chart.yaml:17-19`, `chart.yaml:43-45`
```yaml
filters:
  - column: "user_name"
    label: "Users"
    icon: "👥"
  - column: "is_sla_met"
    label: "SLA Status"
    icon: "✅"  # Second filter, expanded by default
```

**Data Flow**:
1. Generate data with SLA calculation: `generate_data.py:35-37`
2. Write to CSV: `generate_data.py:48-49`
3. Read into pandas: `visualize.py:29-47`
4. Embed in HTML: `visualize.py:424`
5. Load in JavaScript: `workflow_dashboard.html:614-665`
6. Filter by SLA Status: `workflow_dashboard.html:698-703`
7. Color by SLA Status: `visualize.py:728-748`

**Typical Workflow**:
1. Select dataset in dropdown
2. Choose "Color By: SLA Status" → Red points are failures
3. Filter "SLA Status: No" → Show only failed executions
4. Click failed points to select them
5. Export to CSV for investigation
6. Correlate with User/Team filters to identify patterns

**Analysis Patterns**:
- **Identify violations**: Color by SLA Status, visually see red points
- **Root cause analysis**: Filter by "SLA Status: No", then check User/Team distribution
- **Trend analysis**: Use timestamp (X-axis) to see if violations increase over time
- **Performance comparison**: Color by User, filter by SLA Status to see who meets SLA

### 10. Settings Panel & Display Controls

**Overview**: Centralized gear icon settings for controlling panel visibility, with automatic plot resizing to maximize screen space.

**Settings Icon UI**: `visualize.py:357-377`
```css
.settings-icon {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 44px;
    height: 44px;
    background: white;
    border-radius: 50%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    cursor: pointer;
    font-size: 22px;
    z-index: 1000;
}
```

**Settings Panel UI**: `visualize.py:378-389`
```css
.settings-panel {
    position: fixed;
    top: 75px;
    right: 20px;
    width: 250px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    padding: 20px;
    z-index: 1000;
    display: none;  /* Hidden by default */
}
```

**HTML Structure**: `visualize.py:423-434`
```html
<div class="settings-icon" onclick="toggleSettings()">⚙️</div>
<div class="settings-panel" id="settings-panel">
    <div class="settings-title">Display Settings</div>
    <div class="settings-option">
        <input type="checkbox" id="show-histogram" checked
               onchange="togglePanelVisibility('histogram-panel', this.checked)">
        <label for="show-histogram">Performance Distribution</label>
    </div>
    <div class="settings-option">
        <input type="checkbox" id="show-filters" checked
               onchange="togglePanelVisibility('filters-panel', this.checked)">
        <label for="show-filters">Filters</label>
    </div>
</div>
```

**Toggle Functions**: `visualize.py:481-512`
```javascript
// Toggle settings panel visibility
function toggleSettings() {
    const settingsPanel = document.getElementById('settings-panel');
    settingsPanel.classList.toggle('active');
}

// Toggle panel visibility with plot resize
function togglePanelVisibility(panelId, isVisible) {
    const panel = document.getElementById(panelId);
    if (isVisible) {
        panel.classList.remove('hidden-panel');
    } else {
        panel.classList.add('hidden-panel');
    }

    // Force browser to recalculate layout, then resize plot
    requestAnimationFrame(() => {
        // Force reflow by reading offsetHeight
        const container = document.querySelector('.container');
        void(container.offsetHeight);

        // Wait for CSS transition, then resize
        setTimeout(() => {
            const plotDiv = document.getElementById('plot');
            if (plotDiv && plotDiv.data) {
                Plotly.Plots.resize(plotDiv);  // Recalculate dimensions
            }
        }, 400);
    });
}
```

**Close-on-Click-Outside**: `visualize.py:504-512`
```javascript
document.addEventListener('click', function(event) {
    const settingsPanel = document.getElementById('settings-panel');
    const settingsIcon = document.querySelector('.settings-icon');

    if (!settingsPanel.contains(event.target) &&
        !settingsIcon.contains(event.target)) {
        settingsPanel.classList.remove('active');
    }
});
```

**Plot Resize Mechanism**:
1. **requestAnimationFrame**: Ensures code runs after current rendering frame
2. **Force reflow**: Reading `offsetHeight` forces browser to complete layout recalculation
3. **setTimeout(400ms)**: Waits for CSS transition to complete
4. **Plotly.Plots.resize()**: Recalculates plot dimensions based on new container size

**Key Features**:
- Fixed position gear icon (always visible in top right)
- Settings panel appears below gear icon
- Checkboxes control histogram and filters visibility
- Plot automatically expands when panels are hidden
- Plot automatically shrinks when panels are shown
- Smooth transitions (0.3s ease) for panel visibility
- Click outside settings panel to close it

**Benefits**:
- Single control point for display settings
- No spacing issues (panels use `display: none`)
- Bidirectional plot resizing (expand and shrink)
- Clean UI without multiple collapse buttons
- Easy to extend with additional display options

### 11. Embedded Data System

**Why Embedded?**
- No CORS issues
- No web server required
- Self-contained HTML file
- Works offline

**Embedding Process**: `visualize.py:26-47`
1. Read CSV with pandas
2. Convert to dict: `df.to_dict('records')`
3. Store in `embedded_data` dict keyed by dataset name
4. JSON serialize into HTML: `visualize.py:424`

**Data Structure**:
```javascript
const EMBEDDED_DATA = {
    "workflow_data.csv": [
        {user_name: "Alice", workflow_name: "...", timestamp: "...", duration: 280.25, ...},
        {user_name: "Bob", ...},
        // ... more rows
    ],
    "workflow_data2.csv": [
        // ... rows from second dataset
    ]
};
```

**Loading Data**: `workflow_dashboard.html:614-665`
- No async operations needed
- Data available immediately
- Tagged with `_dataset` property for filtering

## Data Flow Details

### Initialization Sequence

1. **HTML loads**: `workflow_dashboard.html`
2. **Parse config**: `workflow_dashboard.html:423` - Load `CHART_CONFIG` from embedded JSON
3. **Initialize filters**: `workflow_dashboard.html:894-902` - Populate dataset dropdown
4. **Load data**: `workflow_dashboard.html:614-665` - Process `EMBEDDED_DATA`
5. **Build metadata**: `workflow_dashboard.html:629-662` - Calculate axis ranges and filter values
6. **Update UI**: `workflow_dashboard.html:917-920` - Populate filters for first dataset
7. **Initial render**: `workflow_dashboard.html:921` - Call `applyFilters()` to draw chart

### Filter Update Flow

1. User changes filter → `checkbox.onchange`: `workflow_dashboard.html:583`
2. Call `applyFilters()`: `workflow_dashboard.html:689`
3. Get selected filters: `workflow_dashboard.html:668-686`
4. Filter data: `workflow_dashboard.html:695-703`
5. Group by first filter column: `workflow_dashboard.html:705-716`
6. Create Plotly traces: `workflow_dashboard.html:721-750`
7. Update scatter plot: `workflow_dashboard.html:783`
8. Update histogram: `workflow_dashboard.html:807`

### Dataset Change Flow

1. User selects dataset → `onchange`: `visualize.py:395`
2. Clear selections: `workflow_dashboard.html:907`
3. Update filters: `workflow_dashboard.html:908` → `updateFiltersForDataset()`
4. Apply filters: `workflow_dashboard.html:909` → `applyFilters()`
5. Rebuild filter UI: `workflow_dashboard.html:526-569`
6. Recalculate viewport: `workflow_dashboard.html:753` - Use dataset-specific ranges

### Point Selection Flow

1. User clicks point → Plotly event: `workflow_dashboard.html:786`
2. Extract point data: `workflow_dashboard.html:787-792`
3. Create unique ID: `workflow_dashboard.html:795` - JSON stringify all columns
4. Toggle in Set: `workflow_dashboard.html:797-801`
5. Update table: `workflow_dashboard.html:803` → `updateDataTable()`
6. Build table HTML: `workflow_dashboard.html:842-857`
7. Enable export button: `workflow_dashboard.html:828`

## Code Coordinates Reference

### Configuration
- YAML schema: `chart.yaml:1-40`
- Config parser: `visualize.py:6-20`
- Config validation: `visualize.py:8-10`, `visualize.py:18-20`

### Data Loading
- CSV reading: `visualize.py:29-47`
- JSON embedding: `visualize.py:42`
- Embedded data constant: `workflow_dashboard.html:424`
- Data loading function: `workflow_dashboard.html:614-665`

### Visualization
- Scatter plot rendering: `workflow_dashboard.html:689-808`
- Histogram rendering: `workflow_dashboard.html:463-523`
- Hover template builder: `workflow_dashboard.html:810-819`
- Percentile calculation: `workflow_dashboard.html:452-460`

### Filters
- Filter metadata building: `workflow_dashboard.html:654-660`
- Filter UI generation: `workflow_dashboard.html:526-569`
- Filter application: `workflow_dashboard.html:698-703`
- Get selected filters: `workflow_dashboard.html:668-686`

### Selection & Export
- Click handler: `workflow_dashboard.html:786-804`
- Selected points storage: `workflow_dashboard.html:435`
- Table update: `workflow_dashboard.html:822-858`
- CSV export: `workflow_dashboard.html:861-891`

### Color Grouping
- Color By dropdown UI: `visualize.py:400-406`
- State variables: `visualize.py:445-446` (colorGroupBy, colorMap)
- Populate dropdown: `visualize.py:548-559`
- Change handler: `visualize.py:941-946` (onColorByChange)
- Color application logic: `visualize.py:728-748`
- Color palette: `visualize.py:427-430`

### SLA Tracking
- Data generation with SLA: `generate_data.py:35-37`, `generate_data2.py:35-37`
- CSV field inclusion: `generate_data.py:48-49`, `generate_data2.py:48-49`
- SLA filter config: `chart.yaml:17-19`, `chart.yaml:43-45`
- Data flow: generate_data.py → CSV → pandas → JSON → embedded HTML

### Settings Panel & Display Controls
- Settings icon CSS: `visualize.py:357-377`
- Settings panel CSS: `visualize.py:378-389`
- Settings HTML structure: `visualize.py:423-434`
- Toggle settings function: `visualize.py:481-486`
- Toggle panel visibility: `visualize.py:489-512`
- Close on click outside: `visualize.py:504-512`
- Plot resize mechanism: `visualize.py:497-510` (requestAnimationFrame + Plotly.Plots.resize)

### UI Components
- Dataset dropdown: `visualize.py:393-397`
- Filter sections: `visualize.py:305-355`
- Table container: `visualize.py:366-374`
- Histogram panel: `visualize.py:411-415`
- Filters panel: `visualize.py:416-417`

### Styling
- Main layout: `visualize.py:68-79`
- Panel styles: `visualize.py:144-178`, `visualize.py:180-209`
- Table styles: `visualize.py:118-143`
- Filter styles: `visualize.py:210-293`

## Extension Points

### Adding New Dataset Types

**Where to modify**:
1. `chart.yaml` - Add new dataset configuration
2. No code changes needed!

**Example**:
```yaml
datasets:
  - name: "custom_metrics"
    label: "Custom Metrics"
    csv_file: "metrics.csv"
    x_axis:
      column: "event_time"
      label: "Event Time"
    y_axis:
      column: "metric_value"
      label: "Metric Value"
    filters:
      - column: "metric_name"
        label: "Metric Names"
        icon: "📊"
```

### Adding New Filter Types

**Current limitation**: Only multi-select checkboxes
**To add range filters or date pickers**:
1. Extend YAML schema in `chart.yaml` with filter type
2. Modify `updateFiltersForDataset()`: `workflow_dashboard.html:526-569`
3. Add new UI generation code for different filter types
4. Update `getSelectedFilters()`: `workflow_dashboard.html:668-686`
5. Update `applyFilters()`: `workflow_dashboard.html:698-703`

### Adding New Chart Types

**To add box plots, violin plots, etc.**:
1. Add `chart_type` to dataset config in `chart.yaml`
2. Modify `applyFilters()`: `workflow_dashboard.html:689-808`
3. Add conditional rendering based on chart type
4. Reuse existing filter and data infrastructure

### Customizing Appearance

**Colors**:
- Palette: `workflow_dashboard.html:427-430`
- Percentile colors: `workflow_dashboard.html:489-498`

**Sizes**:
- Marker size: `workflow_dashboard.html:740`
- Chart height: `visualize.py:317`, `visualize.py:321`
- Panel width: `visualize.py:145`, `visualize.py:163`

**Fonts**:
- Base font: `visualize.py:63`
- All text inherits from body style

## Performance Considerations

### Data Size Limits

**Current implementation**:
- All data embedded in HTML
- No pagination
- Suitable for: **< 10,000 data points per dataset**

**For larger datasets**:
1. Consider server-side filtering
2. Implement data virtualization
3. Use WebGL for rendering (Plotly scattergl)

### Optimization Opportunities

**Current bottlenecks**:
1. `applyFilters()` rebuilds entire chart: `workflow_dashboard.html:783`
   - Alternative: Use Plotly.restyle() for updates
2. Table rendering uses innerHTML: `workflow_dashboard.html:857`
   - Alternative: DOM manipulation or virtual scrolling
3. No debouncing on filter changes
   - Alternative: Add 100ms debounce on checkbox changes

**Memory usage**:
- `allData`: Full dataset in memory
- `selectedPoints`: Only selected rows
- Plotly maintains separate copy for rendering

## Security Considerations

### CSV Injection Prevention

**Export function**: `workflow_dashboard.html:870-877`
- Escapes commas and quotes
- Does NOT prevent formula injection
- **Recommendation**: Prefix values starting with `=`, `+`, `-`, `@` with `'`

### XSS Prevention

**No user input accepted**: HTML is generated server-side
**Data source**: Only from configured CSV files
**HTML escaping**: Plotly handles escaping in tooltips

### CORS Bypass

**Why embedded data works**:
- No cross-origin requests
- All data in same HTML file
- Browser same-origin policy satisfied

## Troubleshooting Guide

### Chart not rendering

**Check**:
1. Browser console for JavaScript errors
2. Plotly library loaded: `visualize.py:60`
3. CHART_CONFIG not empty: `workflow_dashboard.html:423`
4. EMBEDDED_DATA not empty: `workflow_dashboard.html:424`

### Filters not updating

**Check**:
1. Filter metadata populated: `workflow_dashboard.html:654-660`
2. Event handlers attached: `workflow_dashboard.html:583`
3. `applyFilters()` being called: `workflow_dashboard.html:689`

### Export not working

**Check**:
1. Points selected: `selectedPoints.size > 0`
2. Export button enabled: `workflow_dashboard.html:828`
3. Browser allows downloads
4. No popup blocker interfering

### Histogram showing wrong data

**Check**:
1. `currentDatasetConfig` set: `workflow_dashboard.html:530`
2. Y-axis column exists in data
3. Values are numeric: `parseFloat()` at `workflow_dashboard.html:471`
4. `updateHistogram()` called after `applyFilters()`: `workflow_dashboard.html:807`

## Testing Checklist

### Manual Testing

**Configuration**:
- [ ] Invalid YAML syntax
- [ ] Missing CSV file
- [ ] Invalid column name
- [ ] Empty filters array
- [ ] Multiple datasets
- [ ] Same dataset different configs

**UI Interactions**:
- [ ] Click data points
- [ ] Select/deselect points
- [ ] Export CSV
- [ ] Change filters
- [ ] Change dataset
- [ ] Collapse/expand panels
- [ ] Zoom/pan chart

**Data Validation**:
- [ ] CSV with missing columns
- [ ] CSV with extra columns
- [ ] CSV with null values
- [ ] CSV with special characters
- [ ] Empty CSV
- [ ] Large CSV (1000+ rows)

## Future Enhancements

### Planned Features

1. **Undo/Redo for selections**
   - Track selection history
   - Add undo/redo buttons
   - Keyboard shortcuts (Ctrl+Z, Ctrl+Y)

2. **Save/Load selections**
   - Export selection IDs to JSON
   - Import selection IDs
   - Bookmark feature

3. **Advanced filtering**
   - Date range picker
   - Numeric range sliders
   - Text search
   - Regex support

4. **Comparison mode**
   - Show multiple datasets on same chart
   - Side-by-side comparison
   - Diff highlighting

5. **Chart annotations**
   - Add notes to specific points
   - Draw reference lines
   - Highlight regions

### Architecture Improvements

1. **Modular JavaScript**
   - Split into multiple files
   - Use ES6 modules
   - Add build step

2. **State management**
   - Centralized state object
   - State change listeners
   - Undo/redo support

3. **Testing**
   - Unit tests for calculations
   - Integration tests for interactions
   - Visual regression tests

## Contributing Guidelines

### Code Style

**Python**:
- PEP 8 compliant
- Type hints for public functions
- Docstrings for modules and functions

**JavaScript**:
- Semicolons required
- camelCase for variables
- UPPER_CASE for constants
- Single quotes for strings

**YAML**:
- 2-space indentation
- Lowercase keys
- Comments for complex sections

### Adding Features

1. Update `design.md` with code coordinates
2. Add examples to `README.md`
3. Update `agent.md` if affects AI agent usage
4. Test with sample data
5. Commit with descriptive message

### Debugging Tips

**Enable verbose logging**:
```javascript
// Add at top of <script> section
const DEBUG = true;
function log(...args) {
    if (DEBUG) console.log('[Dashboard]', ...args);
}
```

**Inspect data structures**:
```javascript
// In browser console
console.log('All data:', allData);
console.log('Selected points:', selectedPoints);
console.log('Filter metadata:', datasetFilterMetadata);
console.log('Chart config:', CHART_CONFIG);
```

## Version History

### v1.2.0 - Current
- Centralized gear icon settings for display controls
- Bidirectional plot resizing (expand and shrink automatically)
- UTF-8 encoding support for emoji and international characters
- Improved filter initialization (all selected by default)
- Configurable color grouping (choose attribute for data point colors)
- SLA tracking (expected_duration and is_sla_met columns)
- YAML-based configuration
- Multi-select data points with export
- Dynamic histogram with percentiles
- Dataset-specific configuration
- Embedded data (no server required)

### Previous Versions
- v0.5.0 - Collapsible panels and histogram
- v0.4.0 - Embedded data
- v0.3.0 - Dataset-specific filters
- v0.2.0 - Multi-select filters
- v0.1.0 - Initial Tableau-like visualization
