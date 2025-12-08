# Workflow Execution Dashboard

A Tableau-like interactive data visualization tool for analyzing workflow execution data. Built with Python, Plotly, and uv for fast, modern Python dependency management.

## Features

- **Interactive Scatter Plot**: Time vs Duration visualization
- **Multi-Select Filters (Right Sidebar)**: Filter data by multiple criteria simultaneously
  - Dataset filter: Select one or more CSV files
  - Team filter: Select multiple teams
  - Title filter: Select multiple job titles
  - Location filter: Select multiple locations
  - User filter: Click legend to show/hide users
- **Dynamic CSV Loading**: CSV files are loaded on demand, not embedded in HTML
- **Viewport Preservation**: When filtering, the chart axes stay fixed - only data points disappear
- **"All" and "None" Buttons**: Quickly select or clear all items in each filter category
- **Apply Filters Button**: Update visualization after making filter selections
- **Rich Attribute Tracking**: Each execution includes team, title, and location information
- **Detailed Tooltips**: Hover over data points to see:
  - User name
  - Team
  - Title
  - Location
  - Workflow name
  - Execution timestamp
  - Duration
  - Correlation ID
- **Interactive Tools**: Zoom, pan, reset, and export to PNG
- **Self-Contained**: HTML file works in any modern browser (requires CSV files in same directory)

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

### 3. Create the Dashboard

Generate the interactive HTML dashboard:

```bash
uv run visualize.py
```

This will:
- Find all CSV files matching `workflow_data*.csv`
- Process and visualize all datasets
- Create `workflow_dashboard.html`

### 4. View the Dashboard

**Important**: Due to browser security restrictions, you need to view the dashboard through a local web server (not by opening the HTML file directly).

**Option A: Use the built-in server (Recommended)**

```bash
uv run start_server.py
```

This will:
- Start a local web server on port 8000
- Automatically open the dashboard in your browser
- Keep running until you press Ctrl+C

**Option B: Use Python's built-in HTTP server**

```bash
# Python 3
python -m http.server 8000

# Then open in your browser:
# http://localhost:8000/workflow_dashboard.html
```

**Why can't I just open the HTML file?**

When you open `workflow_dashboard.html` directly (using `file://` protocol), browsers block JavaScript from loading the CSV files for security reasons (CORS policy). Running a local web server solves this issue.

## CSV File Format

The program expects CSV files with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `user_name` | string | Name of the user who executed the workflow |
| `workflow_name` | string | Name of the workflow |
| `timestamp` | datetime | Execution timestamp (format: `YYYY-MM-DD HH:MM:SS`) |
| `duration` | float | Duration in seconds |
| `correlation_id` | string | Unique identifier for the execution |
| `team` | string | Team the user belongs to |
| `title` | string | Job title of the user |
| `location` | string | Location of the user |

### Example CSV:

```csv
user_name,workflow_name,timestamp,duration,correlation_id,team,title,location
Alice,Data Processing,2025-11-25 23:04:00,280.25,corr-0001-9030,Engineering,Data Engineer,New York
Bob,Model Training,2025-11-21 11:17:00,262.97,corr-0013-5404,Data Science,ML Engineer,San Francisco
Charlie,ETL Pipeline,2025-11-30 12:53:00,160.35,corr-0012-9639,Analytics,Senior Analyst,London
```

## Using Your Own Data

1. Place your CSV files in the project directory
2. Name them with the pattern `workflow_data*.csv` (e.g., `workflow_data_prod.csv`, `workflow_data_staging.csv`)
3. Run the visualization script: `uv run visualize.py`

The dashboard will automatically detect and include all matching CSV files.

## Dashboard Controls

### Right Sidebar Filters
The filter panel on the right side provides dynamic filtering with instant updates:

1. **📁 Dataset** (Dropdown)
   - Select which CSV file to visualize
   - Single selection - only one dataset at a time

2. **👥 Users** (Multi-select checkboxes)
   - Select multiple users to include in the visualization
   - Filters update automatically as you check/uncheck
   - "All" / "None" buttons for quick selection

3. **🏢 Teams** (Multi-select checkboxes)
   - Select multiple teams to include in the visualization
   - Checkboxes allow any combination of teams
   - "All" / "None" buttons for quick selection

4. **💼 Titles** (Multi-select checkboxes)
   - Select multiple job titles
   - Multi-select enables comparing different roles
   - "All" / "None" buttons for quick selection

5. **📍 Locations** (Multi-select checkboxes)
   - Select multiple locations
   - View data from specific geographic regions
   - "All" / "None" buttons for quick selection

**How It Works:**
- **Instant Updates**: Filters apply automatically as you check/uncheck boxes
- **No Apply Button**: The visualization updates immediately
- **Viewport Fixed**: Chart axes stay fixed - only data points appear/disappear
- **Combine Filters**: All filters work together (e.g., Engineering team + Remote location)

### Navigation
- **Zoom**: Click and drag to select an area
- **Pan**: Hold Shift and drag, or use the pan tool in the toolbar
- **Reset**: Double-click anywhere on the chart
- **Export**: Click the camera icon to save as PNG

### Hover Information
Move your mouse over any data point to see:
- Workflow name (bold)
- User name
- Team
- Title
- Location
- Execution time
- Duration in seconds
- Correlation ID

## Project Structure

```
data_analysis/
├── README.md                  # This file
├── pyproject.toml            # Project configuration
├── uv.lock                   # Locked dependencies
├── generate_data.py          # Generate sample dataset 1
├── generate_data2.py         # Generate sample dataset 2
├── visualize.py              # Main visualization script
├── start_server.py           # Local web server for viewing dashboard
├── workflow_data.csv         # Sample data (November)
├── workflow_data2.csv        # Sample data (December)
└── workflow_dashboard.html   # Generated interactive dashboard
```

## Dependencies

Managed by `uv` and defined in `pyproject.toml`:

- **pandas**: Data manipulation and CSV processing
- **plotly**: Interactive visualization library

## Customization

### Modify Data Generation

Edit `generate_data.py` or `generate_data2.py` to customize:
- User names and profiles (team, title, location)
- Workflow names
- Date ranges
- Duration ranges
- Number of data points
- Teams, titles, and locations available

### Modify Visualization

Edit `visualize.py` to customize:
- Chart colors
- Marker sizes
- Layout and styling
- Hover information format

## Troubleshooting

### No CSV files found

**Error**: `Error: No CSV files found matching 'workflow_data*.csv'`

**Solution**: Generate sample data first:
```bash
uv run generate_data.py
```

### Missing dependencies

**Error**: Module import errors

**Solution**: uv automatically manages dependencies. If issues persist, try:
```bash
uv sync
```

### Empty or corrupt CSV

**Error**: Pandas parsing errors

**Solution**: Verify your CSV has:
- A header row with correct column names
- Properly formatted timestamps
- No missing required columns

## Advanced Usage

### Add More Datasets

Create additional CSV files following the naming pattern:

```bash
# Copy and modify the data generation script
cp generate_data.py generate_data3.py

# Edit the script to change users, workflows, dates
# Run it to create workflow_data3.csv
uv run generate_data3.py

# Regenerate the dashboard
uv run visualize.py
```

The dashboard dropdown will automatically include the new dataset.

### Export Data

Use the camera icon in the toolbar to export the current view as a high-resolution PNG (1200x700px at 2x scale).

## Tips

1. **Large Datasets**: The visualization handles hundreds of points well. For thousands, consider filtering or aggregating data first.
2. **Time Ranges**: Use different CSV files for different time periods (daily, weekly, monthly) for better analysis.
3. **Multi-Select Power**: Select multiple teams AND locations simultaneously to analyze specific combinations (e.g., all Data Science team members in Remote locations).
4. **Filter Analysis**: Use the Team, Title, and Location filters to analyze performance by organizational segments.
5. **Viewport Stability**: The fixed viewport when filtering makes it easy to see where data points were before/after filtering.
6. **Quick Filtering**: Use "All" and "None" buttons to quickly reset filter sections.
7. **Sharing**: When sharing the HTML file, include all CSV files in the same directory. Consider creating a zip file with everything.

## License

This project is open source and available for use in your organization.

## Support

For issues or questions, refer to the documentation or contact your development team.
