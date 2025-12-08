# Workflow Execution Dashboard

A Tableau-like interactive data visualization tool for analyzing workflow execution data. Built with Python, Plotly, and uv for fast, modern Python dependency management.

## Features

- **Interactive Scatter Plot**: Time vs Duration visualization
- **Multiple Dataset Support**: Switch between different CSV files using a dropdown menu
- **User Filtering**: Click legend items to show/hide specific users
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
- **Self-Contained**: Generates a standalone HTML file that works in any browser

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

Open the generated HTML file in your browser:

```bash
# Linux
xdg-open workflow_dashboard.html

# macOS
open workflow_dashboard.html

# Windows
start workflow_dashboard.html
```

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

### Dataset Selection
- **Dropdown Menu**: Located at the top-left of the chart
- Click to switch between different CSV datasets
- The title updates to show which dataset is currently displayed

### User Filtering
- **Click once**: Hide/show data for a specific user
- **Double-click**: Isolate data for just that user
- **Click legend title**: Reset all filters

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
3. **Comparison**: Switch between datasets using the dropdown to compare different time periods or teams.
4. **Sharing**: The HTML file is self-contained and can be shared via email or hosted on any web server.

## License

This project is open source and available for use in your organization.

## Support

For issues or questions, refer to the documentation or contact your development team.
