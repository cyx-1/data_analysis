# Workflow Execution Dashboard

> **Transform CSV performance metrics into portable HTML dashboards for standardized team reviews**

## What Is This?

**A tool that generates self-contained, interactive HTML dashboards from CSV files** so your team can review system performance metrics in a consistent, shareable format - no server required.

**Key Value**:
- 📊 **One Command** → Generates a complete HTML dashboard from CSV files
- 📦 **Portable** → Self-contained HTML file with embedded data (no server needed)
- 🔄 **Standardized** → YAML configuration ensures consistent visualization across teams
- 🎯 **Interactive** → Click, filter, select, and export data points for analysis
- 📤 **Shareable** → Email the HTML file, or drop it in Slack/Teams - opens anywhere

**Perfect For**:
- Performance review meetings (display metrics on one screen)
- Incident post-mortems (analyze and export specific data points)
- Executive summaries (standardized charts across departments)
- Sharing analysis with remote team members (no infrastructure setup)

## How It Works

```bash
# 1. Create configuration file (one time)
chart.yaml  →  Define what to visualize

# 2. Run generator
uv run visualize.py  →  Reads CSVs, generates HTML

# 3. Share and analyze
workflow_dashboard.html  →  Open in browser, share with team
```

**Result**: A single HTML file containing all your data, ready to open in any browser.

## Real-World Example

**Scenario**: Your team runs workflows across multiple environments and needs to review execution performance.

**Before**:
- CSV files scattered across systems
- Different people use different tools (Excel, Tableau, custom scripts)
- Hard to share analysis (screenshots, copying data)
- No standard format for reviews

**After**:
1. Configure `chart.yaml` once (defines what X-axis, Y-axis, filters mean)
2. Drop CSV files in folder
3. Run `uv run visualize.py`
4. Share `workflow_dashboard.html` via email/Slack
5. Everyone sees the same interactive dashboard
6. Select problematic data points → Export → Investigate

**Result**: Standardized performance reviews across all teams, with portable analysis.

## Features

- **YAML-Based Configuration**: Externalize all settings in `chart.yaml`
- **Interactive Scatter Plot**: Configurable X and Y axes
- **Multi-Select Data Points**: Click points to select, view in table, and export to CSV
- **Duration Histogram**: Shows distribution with percentile markers (50th, 75th, 95th, 97th)
- **Multi-Select Filters**: Filter data by multiple criteria simultaneously (configured per dataset)
- **Collapsible Panels**: Hide histogram and filters for full-screen chart view
- **Dataset-Specific Configuration**: Each dataset can have different axes, labels, and filters
- **Embedded Data**: No web server required - CSV data is embedded in HTML
- **Dynamic Updates**: Filters, histogram, and table update instantly
- **Rich Tooltips**: Hover over data points to see all attributes
- **Interactive Tools**: Zoom, pan, reset, and export to PNG
- **Self-Contained**: HTML file works in any modern browser

## Documentation

- **[README.md](README.md)** (this file) - User guide and feature documentation
- **[design.md](design.md)** - Technical architecture and code coordinates
- **[agent.md](agent.md)** - AI agent guide for code modifications

## Prerequisites

- Python 3.11+ (installed automatically by uv)
- [uv](https://github.com/astral-sh/uv) package manager

## Quick Start

### 1. Install Dependencies

The project uses `uv` for dependency management (no pip required). Dependencies are automatically installed when you run scripts:

```bash
uv run visualize.py
```

### 2. Generate Sample Data

Create sample workflow execution data:

```bash
# Generate first dataset (100 data points, Nov 2025)
uv run generate_data.py

# Generate second dataset (100 data points, Dec 2025)
uv run generate_data2.py
```

### 3. Configure Your Dashboard

Edit `chart.yaml` to configure your dashboard:

```yaml
title: "Workflow Execution Dashboard"

datasets:
  - name: "workflow_data.csv"
    label: "November 2025 Workflows"
    csv_file: "workflow_data.csv"
    x_axis:
      column: "timestamp"
      label: "Execution Time"
    y_axis:
      column: "duration"
      label: "Duration (seconds)"
    filters:
      - column: "user_name"
        label: "Users"
        icon: "👥"
      - column: "team"
        label: "Teams"
        icon: "🏢"
```

Each dataset can have:
- Different X/Y axis columns and labels
- Different filter columns
- Custom icons and labels
- Independent configuration

### 4. Create the Dashboard

Generate the interactive HTML dashboard:

```bash
uv run visualize.py
```

This will:
- Read configuration from `chart.yaml`
- Load all configured CSV files
- Embed data directly in HTML
- Create `workflow_dashboard.html`

### 5. View the Dashboard

Simply open the HTML file in your browser:

```bash
# Double-click workflow_dashboard.html
# Or open from your browser's File menu
```

**No web server required!** Data is embedded directly in the HTML.

## Configuration File (chart.yaml)

### Structure

```yaml
title: "Your Dashboard Title"

datasets:
  - name: "unique_dataset_id"           # Unique identifier
    label: "Human-Readable Label"       # Display name in dropdown
    csv_file: "path/to/file.csv"        # CSV file path
    x_axis:
      column: "column_name"             # CSV column for X axis
      label: "X Axis Label"             # Display label
    y_axis:
      column: "column_name"             # CSV column for Y axis
      label: "Y Axis Label"             # Display label
    filters:
      - column: "column_name"           # CSV column to filter by
        label: "Filter Label"           # Display label
        icon: "🔹"                      # Optional icon
```

### Example: Multiple Datasets with Different Configurations

```yaml
title: "Multi-Environment Performance Dashboard"

datasets:
  # Production data - focus on response time
  - name: "prod"
    label: "Production"
    csv_file: "prod_metrics.csv"
    x_axis:
      column: "timestamp"
      label: "Time"
    y_axis:
      column: "response_time_ms"
      label: "Response Time (ms)"
    filters:
      - column: "endpoint"
        label: "API Endpoints"
        icon: "🔌"
      - column: "region"
        label: "Regions"
        icon: "🌍"

  # Staging data - focus on throughput
  - name: "staging"
    label: "Staging Environment"
    csv_file: "staging_metrics.csv"
    x_axis:
      column: "timestamp"
      label: "Time"
    y_axis:
      column: "requests_per_sec"
      label: "Throughput (req/s)"
    filters:
      - column: "service_name"
        label: "Services"
        icon: "⚙️"
      - column: "version"
        label: "Versions"
        icon: "📦"
```

## CSV File Format

The CSV files should contain your data columns. The `chart.yaml` configuration determines which columns are used for axes and filters.

### Example CSV:

```csv
user_name,workflow_name,timestamp,duration,correlation_id,team,title,location
Alice,Data Processing,2025-11-25 23:04:00,280.25,corr-0001-9030,Engineering,Data Engineer,New York
Bob,Model Training,2025-11-21 11:17:00,262.97,corr-0013-5404,Data Science,ML Engineer,San Francisco
Charlie,ETL Pipeline,2025-11-30 12:53:00,160.35,corr-0012-9639,Analytics,Senior Analyst,London
```

## Dashboard Features

### 1. Multi-Select Data Points

- **Click** on any data point to select it
- Click again to deselect
- Selected points appear in the table below the chart
- **Export button** downloads selected points as CSV
- Selection counter shows how many points are selected

### 2. Duration Histogram

- Shows distribution of Y-axis values (e.g., duration)
- **Percentile markers**:
  - 🟢 50th percentile (solid green line)
  - 🟠 75th percentile (dashed orange line)
  - 🔴 95th percentile (dashed red line)
  - 🟣 97th percentile (dotted purple line)
- Updates dynamically with filters
- Collapsible panel

### 3. Dynamic Filters

Configured in `chart.yaml` per dataset:
- First 2 filters are expanded by default
- Remaining filters are collapsed
- Multi-select checkboxes
- "All" / "None" buttons for quick selection
- Instant updates (no apply button needed)
- Dataset-specific filter options

### 4. Collapsible Panels

- **Histogram**: Click ◀ to collapse/expand
- **Filters**: Click ◀ to collapse/expand
- Both collapsed = full-screen scatter plot view

### 5. Data Table & Export

- Table shows all attributes of selected points
- Scrollable with sticky header
- **Export CSV** button downloads selected data
- Button disabled when no points selected

## Dashboard Controls

### Navigation
- **Zoom**: Click and drag to select an area
- **Pan**: Hold Shift and drag
- **Reset**: Double-click anywhere on the chart
- **Export Chart**: Click camera icon to save as PNG

### Hover Information
Move your mouse over any data point to see all its attributes

## Project Structure

```
data_analysis/
├── README.md                  # This file - User guide
├── design.md                  # Technical architecture and code coordinates
├── agent.md                   # AI agent guide for development
├── chart.yaml                 # Dashboard configuration
├── pyproject.toml            # Project dependencies
├── uv.lock                   # Locked dependencies
├── generate_data.py          # Generate sample dataset 1
├── generate_data2.py         # Generate sample dataset 2
├── visualize.py              # Main visualization script
├── workflow_data.csv         # Sample data (November)
├── workflow_data2.csv        # Sample data (December)
└── workflow_dashboard.html   # Generated interactive dashboard
```

## Dependencies

Managed by `uv` and defined in `pyproject.toml`:

- **pandas**: Data manipulation and CSV processing
- **pyyaml**: YAML configuration parsing
- **plotly**: Interactive visualization library

## Customization

### Modify Configuration

Edit `chart.yaml` to:
- Change chart title
- Add/remove datasets
- Configure X/Y axes per dataset
- Customize filter columns per dataset
- Change labels and icons

### Modify Data Generation

Edit `generate_data.py` or `generate_data2.py` to customize:
- User names and profiles
- Workflow names
- Date ranges
- Duration ranges
- Number of data points

### Modify Visualization

Edit `visualize.py` to customize:
- Chart colors
- Marker sizes
- Layout and styling
- HTML/CSS styling

## Troubleshooting

### No chart.yaml found

**Error**: `Error: chart.yaml not found`

**Solution**: Create a `chart.yaml` file following the examples above.

### CSV file not found

**Error**: `Warning: {file} not found, skipping...`

**Solution**: Ensure the CSV file path in `chart.yaml` is correct and the file exists.

### No datasets configured

**Error**: `Error: No datasets configured in chart.yaml`

**Solution**: Add at least one dataset to the `datasets` list in `chart.yaml`.

### Missing dependencies

**Error**: Module import errors

**Solution**: Dependencies are automatically managed by uv:
```bash
uv sync
```

## Advanced Usage

### Add More Datasets

1. Create a new CSV file
2. Add configuration to `chart.yaml`:

```yaml
datasets:
  - name: "my_new_dataset"
    label: "My New Dataset"
    csv_file: "my_data.csv"
    x_axis:
      column: "time"
      label: "Time"
    y_axis:
      column: "value"
      label: "Value"
    filters:
      - column: "category"
        label: "Categories"
        icon: "📊"
```

3. Regenerate: `uv run visualize.py`

### Different Axes Per Dataset

Each dataset can plot different columns:

```yaml
datasets:
  # Dataset 1: Time vs Duration
  - name: "duration_analysis"
    x_axis:
      column: "timestamp"
      label: "Time"
    y_axis:
      column: "duration"
      label: "Duration (s)"

  # Dataset 2: Cost vs Throughput
  - name: "cost_analysis"
    x_axis:
      column: "cost_usd"
      label: "Cost ($)"
    y_axis:
      column: "throughput"
      label: "Throughput (ops/s)"
```

### Dataset-Specific Filters

Configure different filters per dataset:

```yaml
datasets:
  # Web service dataset
  - name: "web_metrics"
    filters:
      - column: "endpoint"
        label: "Endpoints"
      - column: "http_method"
        label: "HTTP Methods"
      - column: "status_code"
        label: "Status Codes"

  # Database dataset
  - name: "db_metrics"
    filters:
      - column: "query_type"
        label: "Query Types"
      - column: "table_name"
        label: "Tables"
      - column: "index_used"
        label: "Index Usage"
```

### Export Selected Data

1. Click data points to select them
2. Review selected points in the table
3. Click "📥 Export CSV" button
4. File downloads as `selected_data.csv`

## Tips

1. **Start Simple**: Begin with a basic configuration and add complexity as needed
2. **One Config File**: All datasets are configured in one `chart.yaml` file
3. **Regenerate Anytime**: Edit `chart.yaml` and run `uv run visualize.py` to update
4. **No Server Needed**: Share the HTML file directly - data is embedded
5. **Collapsible UI**: Hide panels you don't need for focused analysis
6. **Multi-Select Power**: Select specific data points for detailed analysis
7. **Percentiles**: Use histogram percentiles to identify outliers quickly
8. **Filter Combinations**: Combine multiple filters for targeted analysis

## Technical Documentation

For developers and AI agents:
- **[design.md](design.md)** - Detailed architecture, code coordinates, and implementation details
- **[agent.md](agent.md)** - Guide for AI agents working with this codebase

These documents provide:
- Exact code coordinates for all features (file:line references)
- Data flow diagrams
- Extension points for new features
- Common task workflows
- Debugging guides

## License

This project is open source and available for use in your organization.

## Support

For issues or questions, refer to the documentation or contact your development team.
