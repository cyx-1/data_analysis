import pandas as pd
from pathlib import Path
import json

# Find all CSV files matching the pattern
csv_files = sorted(Path('.').glob('workflow_data*.csv'))

if not csv_files:
    print("Error: No CSV files found matching 'workflow_data*.csv'")
    exit(1)

print(f"Found {len(csv_files)} CSV file(s):")
for f in csv_files:
    print(f"  • {f.name}")

# Read CSV files and convert to JSON for embedding
all_teams = set()
all_titles = set()
all_locations = set()
all_users = set()
csv_file_names = [f.name for f in csv_files]
embedded_data = {}

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    all_teams.update(df['team'].unique())
    all_titles.update(df['title'].unique())
    all_locations.update(df['location'].unique())
    all_users.update(df['user_name'].unique())

    # Convert DataFrame to list of dictionaries for embedding
    embedded_data[csv_file.name] = df.to_dict('records')

all_teams = sorted(all_teams)
all_titles = sorted(all_titles)
all_locations = sorted(all_locations)
all_users = sorted(all_users)

# Generate HTML with embedded JavaScript
html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workflow Execution Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            display: flex;
            gap: 20px;
            max-width: 100%;
            margin: 0 auto;
        }}
        .chart-container {{
            flex: 1;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        .histogram-container {{
            width: 280px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            height: fit-content;
            position: sticky;
            top: 20px;
            transition: all 0.3s ease;
        }}
        .histogram-container.collapsed {{
            width: 50px;
            padding: 10px;
        }}
        .histogram-container.collapsed .histogram-content {{
            display: none;
        }}
        .filters-container {{
            width: 280px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            height: fit-content;
            position: sticky;
            top: 20px;
            transition: all 0.3s ease;
        }}
        .filters-container.collapsed {{
            width: 50px;
            padding: 10px;
        }}
        .filters-container.collapsed .filters-content {{
            display: none;
        }}
        .panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .panel-title {{
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }}
        .collapse-btn {{
            background: #f5f5f5;
            border: none;
            border-radius: 4px;
            width: 30px;
            height: 30px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            font-size: 16px;
        }}
        .collapse-btn:hover {{
            background: #e0e0e0;
        }}
        .collapsed .collapse-btn {{
            transform: rotate(180deg);
        }}
        .filter-section {{
            margin-bottom: 12px;
        }}
        .filter-section h3 {{
            margin: 0 0 12px 0;
            font-size: 14px;
            font-weight: 600;
            color: #333;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            cursor: pointer;
            user-select: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        .filter-section h3:hover {{
            background: #f5f5f5;
        }}
        .filter-section h3::after {{
            content: '▼';
            font-size: 10px;
            transition: transform 0.2s;
        }}
        .filter-section h3.collapsed::after {{
            transform: rotate(-90deg);
        }}
        .filter-content {{
            max-height: 300px;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }}
        .filter-content.collapsed {{
            max-height: 0;
        }}
        .filter-options {{
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 8px;
        }}
        .filter-option {{
            display: flex;
            align-items: center;
            padding: 6px 8px;
            cursor: pointer;
            border-radius: 3px;
            transition: background 0.2s;
        }}
        .filter-option:hover {{
            background: #f0f0f0;
        }}
        .filter-option input[type="checkbox"] {{
            margin-right: 8px;
            cursor: pointer;
        }}
        .filter-option label {{
            cursor: pointer;
            font-size: 13px;
            flex: 1;
            user-select: none;
        }}
        .filter-select {{
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 13px;
            cursor: pointer;
            background: white;
        }}
        .filter-select:focus {{
            outline: none;
            border-color: #007bff;
        }}
        .filter-actions {{
            display: flex;
            gap: 8px;
            margin-top: 8px;
        }}
        .btn {{
            padding: 6px 12px;
            font-size: 12px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn:hover {{
            background: #f0f0f0;
            border-color: #999;
        }}
        .btn-primary {{
            background: #007bff;
            color: white;
            border-color: #007bff;
        }}
        .btn-primary:hover {{
            background: #0056b3;
            border-color: #0056b3;
        }}
        #plot {{
            width: 100%;
            height: 700px;
        }}
        #histogram {{
            width: 100%;
            height: 700px;
        }}
        .percentile-info {{
            font-size: 11px;
            color: #666;
            margin-top: 10px;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 4px;
        }}
        .percentile-info div {{
            margin: 4px 0;
        }}
        .info-text {{
            font-size: 12px;
            color: #666;
            font-style: italic;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
        }}
        .info-text code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 11px;
            font-style: normal;
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin: 0 0 20px 0;
            font-size: 28px;
        }}
    </style>
</head>
<body>
    <h1>Workflow Execution Dashboard</h1>
    <div class="container">
        <div class="chart-container">
            <div id="plot"></div>
        </div>
        <div class="histogram-container" id="histogram-panel">
            <div class="panel-header">
                <span class="panel-title">📊 Duration Distribution</span>
                <button class="collapse-btn" onclick="togglePanel('histogram-panel')" title="Collapse">◀</button>
            </div>
            <div class="histogram-content">
                <div id="histogram"></div>
                <div class="percentile-info" id="percentile-info"></div>
            </div>
        </div>
        <div class="filters-container" id="filters-panel">
            <div class="panel-header">
                <span class="panel-title">🔍 Filters</span>
                <button class="collapse-btn" onclick="togglePanel('filters-panel')" title="Collapse">◀</button>
            </div>
            <div class="filters-content">
            <div class="filter-section">
                <h3 onclick="toggleSection(this)">📁 Dataset</h3>
                <div class="filter-content">
                    <select id="dataset-select" class="filter-select" onchange="updateFiltersForDataset(this.value); applyFilters();">
                    </select>
                </div>
            </div>

            <div class="filter-section">
                <h3 onclick="toggleSection(this)">👥 Users</h3>
                <div class="filter-content">
                    <div class="filter-options" id="user-filters"></div>
                    <div class="filter-actions">
                        <button class="btn" onclick="selectAllUsers()">All</button>
                        <button class="btn" onclick="clearAllUsers()">None</button>
                    </div>
                </div>
            </div>

            <div class="filter-section">
                <h3 onclick="toggleSection(this)" class="collapsed">🏢 Teams</h3>
                <div class="filter-content collapsed">
                    <div class="filter-options" id="team-filters"></div>
                    <div class="filter-actions">
                        <button class="btn" onclick="selectAllTeams()">All</button>
                        <button class="btn" onclick="clearAllTeams()">None</button>
                    </div>
                </div>
            </div>

            <div class="filter-section">
                <h3 onclick="toggleSection(this)" class="collapsed">💼 Titles</h3>
                <div class="filter-content collapsed">
                    <div class="filter-options" id="title-filters"></div>
                    <div class="filter-actions">
                        <button class="btn" onclick="selectAllTitles()">All</button>
                        <button class="btn" onclick="clearAllTitles()">None</button>
                    </div>
                </div>
            </div>

            <div class="filter-section">
                <h3 onclick="toggleSection(this)" class="collapsed">📍 Locations</h3>
                <div class="filter-content collapsed">
                    <div class="filter-options" id="location-filters"></div>
                    <div class="filter-actions">
                        <button class="btn" onclick="selectAllLocations()">All</button>
                        <button class="btn" onclick="clearAllLocations()">None</button>
                    </div>
                </div>
            </div>

            <div class="info-text">
                💡 <strong>Click section headers</strong> to collapse/expand filters. Filters update dynamically.
                <br><br>
                📊 Each dataset has its own viewport and filter options specific to that dataset.
                <br><br>
                📈 Histogram shows duration distribution with percentile markers.
                <br><br>
                🔽 Click the collapse buttons to hide histogram or filters for full-screen chart view.
                <br><br>
                ℹ️ To add more CSV files: Place them in this folder and run <code>uv run visualize.py</code> to regenerate the HTML.
                <br><br>
                ✨ CSV data is embedded - no web server required! Just open this HTML file in your browser.
            </div>
            </div>
        </div>
    </div>

    <script>
        const CSV_FILES = {json.dumps(csv_file_names)};
        const TEAMS = {json.dumps(all_teams)};
        const TITLES = {json.dumps(all_titles)};
        const LOCATIONS = {json.dumps(all_locations)};
        const USERS = {json.dumps(all_users)};

        // Embedded CSV data (no need for external file loading)
        const EMBEDDED_DATA = {json.dumps(embedded_data)};

        const COLOR_PALETTE = [
            '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00',
            '#ffff33', '#a65628', '#f781bf', '#999999', '#66c2a5'
        ];

        let allData = [];
        let datasetAxisRanges = {{}};  // Store axis ranges per dataset
        let datasetMetadata = {{}};  // Store filter values per dataset

        // Toggle filter section collapse/expand
        function toggleSection(header) {{
            header.classList.toggle('collapsed');
            const content = header.nextElementSibling;
            content.classList.toggle('collapsed');
        }}

        // Toggle panel (histogram or filters) collapse/expand
        function togglePanel(panelId) {{
            const panel = document.getElementById(panelId);
            panel.classList.toggle('collapsed');
        }}

        // Calculate percentiles from array of durations
        function calculatePercentiles(durations, percentiles) {{
            const sorted = [...durations].sort((a, b) => a - b);
            const results = {{}};
            percentiles.forEach(p => {{
                const index = Math.ceil((p / 100) * sorted.length) - 1;
                results[p] = sorted[Math.max(0, index)];
            }});
            return results;
        }}

        // Update histogram with current filtered data
        function updateHistogram(filteredData) {{
            if (filteredData.length === 0) {{
                document.getElementById('histogram').innerHTML = '<p style="text-align: center; padding: 20px; color: #999;">No data to display</p>';
                document.getElementById('percentile-info').innerHTML = '';
                return;
            }}

            const durations = filteredData.map(d => parseFloat(d.duration));
            const percentiles = calculatePercentiles(durations, [50, 75, 95, 97]);

            // Create histogram trace
            const trace = {{
                x: durations,
                type: 'histogram',
                marker: {{
                    color: '#377eb8',
                    line: {{
                        color: 'white',
                        width: 1
                    }}
                }},
                nbinsx: 30
            }};

            // Create shapes for percentile lines
            const shapes = [
                {{ type: 'line', x0: percentiles[50], x1: percentiles[50], y0: 0, y1: 1, yref: 'paper',
                   line: {{ color: '#4daf4a', width: 2, dash: 'solid' }} }},
                {{ type: 'line', x0: percentiles[75], x1: percentiles[75], y0: 0, y1: 1, yref: 'paper',
                   line: {{ color: '#ff7f00', width: 2, dash: 'dash' }} }},
                {{ type: 'line', x0: percentiles[95], x1: percentiles[95], y0: 0, y1: 1, yref: 'paper',
                   line: {{ color: '#e41a1c', width: 2, dash: 'dash' }} }},
                {{ type: 'line', x0: percentiles[97], x1: percentiles[97], y0: 0, y1: 1, yref: 'paper',
                   line: {{ color: '#984ea3', width: 2, dash: 'dot' }} }}
            ];

            const layout = {{
                xaxis: {{ title: 'Duration (seconds)' }},
                yaxis: {{ title: 'Count' }},
                margin: {{ t: 20, b: 40, l: 40, r: 20 }},
                height: 500,
                showlegend: false,
                shapes: shapes
            }};

            const config = {{
                displayModeBar: false
            }};

            Plotly.newPlot('histogram', [trace], layout, config);

            // Update percentile info
            document.getElementById('percentile-info').innerHTML = `
                <div><strong>Percentiles:</strong></div>
                <div>🟢 50th: ${{percentiles[50].toFixed(2)}}s</div>
                <div>🟠 75th: ${{percentiles[75].toFixed(2)}}s</div>
                <div>🔴 95th: ${{percentiles[95].toFixed(2)}}s</div>
                <div>🟣 97th: ${{percentiles[97].toFixed(2)}}s</div>
            `;
        }}

        // Update filter options based on selected dataset
        function updateFiltersForDataset(datasetName) {{
            const metadata = datasetMetadata[datasetName];
            if (!metadata) return;

            // Update user filters
            const userContainer = document.getElementById('user-filters');
            userContainer.innerHTML = '';
            metadata.users.forEach(user => {{
                userContainer.appendChild(createCheckbox(user, 'user', true));
            }});

            // Update team filters
            const teamContainer = document.getElementById('team-filters');
            teamContainer.innerHTML = '';
            metadata.teams.forEach(team => {{
                teamContainer.appendChild(createCheckbox(team, 'team', true));
            }});

            // Update title filters
            const titleContainer = document.getElementById('title-filters');
            titleContainer.innerHTML = '';
            metadata.titles.forEach(title => {{
                titleContainer.appendChild(createCheckbox(title, 'title', true));
            }});

            // Update location filters
            const locationContainer = document.getElementById('location-filters');
            locationContainer.innerHTML = '';
            metadata.locations.forEach(location => {{
                locationContainer.appendChild(createCheckbox(location, 'location', true));
            }});
        }}

        // Initialize filter checkboxes
        function initializeFilters() {{
            // Dataset dropdown with change handler
            const datasetSelect = document.getElementById('dataset-select');
            CSV_FILES.forEach(file => {{
                const option = document.createElement('option');
                option.value = file;
                option.textContent = file;
                datasetSelect.appendChild(option);
            }});
        }}

        function createCheckbox(value, type, checked = true) {{
            const div = document.createElement('div');
            div.className = 'filter-option';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `${{type}}-${{value}}`;
            checkbox.checked = checked;
            checkbox.dataset.type = type;
            checkbox.dataset.value = value;

            // Auto-update on change
            checkbox.onchange = applyFilters;

            const label = document.createElement('label');
            label.htmlFor = checkbox.id;
            label.textContent = value;

            div.appendChild(checkbox);
            div.appendChild(label);

            // Click on div also toggles checkbox
            div.onclick = (e) => {{
                if (e.target !== checkbox) {{
                    checkbox.checked = !checkbox.checked;
                    applyFilters();
                }}
            }};

            return div;
        }}

        // Filter selection functions
        function selectAllUsers() {{
            document.querySelectorAll('[data-type="user"]').forEach(cb => cb.checked = true);
            applyFilters();
        }}
        function clearAllUsers() {{
            document.querySelectorAll('[data-type="user"]').forEach(cb => cb.checked = false);
            applyFilters();
        }}
        function selectAllTeams() {{
            document.querySelectorAll('[data-type="team"]').forEach(cb => cb.checked = true);
            applyFilters();
        }}
        function clearAllTeams() {{
            document.querySelectorAll('[data-type="team"]').forEach(cb => cb.checked = false);
            applyFilters();
        }}
        function selectAllTitles() {{
            document.querySelectorAll('[data-type="title"]').forEach(cb => cb.checked = true);
            applyFilters();
        }}
        function clearAllTitles() {{
            document.querySelectorAll('[data-type="title"]').forEach(cb => cb.checked = false);
            applyFilters();
        }}
        function selectAllLocations() {{
            document.querySelectorAll('[data-type="location"]').forEach(cb => cb.checked = true);
            applyFilters();
        }}
        function clearAllLocations() {{
            document.querySelectorAll('[data-type="location"]').forEach(cb => cb.checked = false);
            applyFilters();
        }}

        // Load embedded data (synchronous, no need for external files)
        function loadEmbeddedData() {{
            // Process embedded data and tag with dataset name
            allData = [];
            CSV_FILES.forEach(csvFile => {{
                const datasetData = EMBEDDED_DATA[csvFile];
                if (datasetData) {{
                    datasetData.forEach(row => {{
                        row._dataset = csvFile;
                        allData.push(row);
                    }});
                }}
            }});

            // Calculate axis ranges and metadata per dataset
            CSV_FILES.forEach(csvFile => {{
                const datasetData = allData.filter(row => row._dataset === csvFile);

                if (datasetData.length > 0) {{
                    const timestamps = datasetData.map(d => new Date(d.timestamp));
                    const durations = datasetData.map(d => parseFloat(d.duration));

                    const minTime = new Date(Math.min(...timestamps));
                    const maxTime = new Date(Math.max(...timestamps));
                    const minDuration = Math.min(...durations);
                    const maxDuration = Math.max(...durations);

                    const timePadding = (maxTime - minTime) * 0.05;
                    const durationPadding = (maxDuration - minDuration) * 0.05;

                    datasetAxisRanges[csvFile] = {{
                        xaxis: [new Date(minTime.getTime() - timePadding), new Date(maxTime.getTime() + timePadding)],
                        yaxis: [minDuration - durationPadding, maxDuration + durationPadding]
                    }};

                    // Build metadata (unique filter values) for this dataset
                    datasetMetadata[csvFile] = {{
                        users: [...new Set(datasetData.map(d => d.user_name))].sort(),
                        teams: [...new Set(datasetData.map(d => d.team))].sort(),
                        titles: [...new Set(datasetData.map(d => d.title))].sort(),
                        locations: [...new Set(datasetData.map(d => d.location))].sort()
                    }};
                }}
            }});

            return allData;
        }}

        // Get selected filter values
        function getSelectedFilters() {{
            const datasetSelect = document.getElementById('dataset-select');
            return {{
                dataset: datasetSelect.value,
                users: Array.from(document.querySelectorAll('[data-type="user"]:checked'))
                    .map(cb => cb.dataset.value),
                teams: Array.from(document.querySelectorAll('[data-type="team"]:checked'))
                    .map(cb => cb.dataset.value),
                titles: Array.from(document.querySelectorAll('[data-type="title"]:checked'))
                    .map(cb => cb.dataset.value),
                locations: Array.from(document.querySelectorAll('[data-type="location"]:checked'))
                    .map(cb => cb.dataset.value)
            }};
        }}

        // Apply filters and update plot
        function applyFilters() {{
            const filters = getSelectedFilters();

            // Filter data
            const filteredData = allData.filter(row => {{
                return row._dataset === filters.dataset &&
                       filters.users.includes(row.user_name) &&
                       filters.teams.includes(row.team) &&
                       filters.titles.includes(row.title) &&
                       filters.locations.includes(row.location);
            }});

            // Group by user
            const dataByUser = {{}};
            filteredData.forEach(row => {{
                if (!dataByUser[row.user_name]) {{
                    dataByUser[row.user_name] = [];
                }}
                dataByUser[row.user_name].push(row);
            }});

            // Create traces
            const traces = [];
            USERS.forEach((user, idx) => {{
                if (dataByUser[user]) {{
                    const userData = dataByUser[user];
                    traces.push({{
                        x: userData.map(d => d.timestamp),
                        y: userData.map(d => parseFloat(d.duration)),
                        mode: 'markers',
                        type: 'scatter',
                        name: user,
                        marker: {{
                            size: 10,
                            color: COLOR_PALETTE[idx % COLOR_PALETTE.length],
                            line: {{ width: 1, color: 'white' }},
                            opacity: 0.8
                        }},
                        customdata: userData.map(d => [
                            d.user_name, d.workflow_name, d.correlation_id,
                            d.team, d.title, d.location
                        ]),
                        hovertemplate:
                            '<b>%{{customdata[1]}}</b><br>' +
                            'User: %{{customdata[0]}}<br>' +
                            'Team: %{{customdata[3]}}<br>' +
                            'Title: %{{customdata[4]}}<br>' +
                            'Location: %{{customdata[5]}}<br>' +
                            'Time: %{{x}}<br>' +
                            'Duration: %{{y:.2f}}s<br>' +
                            'Correlation ID: %{{customdata[2]}}<br>' +
                            '<extra></extra>'
                    }});
                }}
            }});

            // Get axis ranges for the selected dataset
            const axisRanges = datasetAxisRanges[filters.dataset];

            const layout = {{
                xaxis: {{
                    title: 'Execution Time',
                    range: axisRanges.xaxis
                }},
                yaxis: {{
                    title: 'Duration (seconds)',
                    range: axisRanges.yaxis
                }},
                hovermode: 'closest',
                showlegend: false,
                template: 'plotly_white',
                height: 700,
                margin: {{ t: 20 }}
            }};

            const config = {{
                displayModeBar: true,
                displaylogo: false,
                toImageButtonOptions: {{
                    format: 'png',
                    filename: 'workflow_dashboard',
                    height: 700,
                    width: 1200,
                    scale: 2
                }}
            }};

            Plotly.newPlot('plot', traces, layout, config);

            // Update histogram with filtered data
            updateHistogram(filteredData);
        }}

        // Initialize on page load
        initializeFilters();
        loadEmbeddedData();

        // Update filters for first dataset after data is loaded
        if (CSV_FILES.length > 0) {{
            const datasetSelect = document.getElementById('dataset-select');
            updateFiltersForDataset(datasetSelect.value || CSV_FILES[0]);
        }}
        applyFilters();
        console.log('Dashboard loaded successfully');
    </script>
</body>
</html>'''

# Write HTML file
with open('workflow_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n✓ Interactive dashboard created: workflow_dashboard.html")
print(f"✓ CSV data embedded from {len(csv_file_names)} file(s):")
print(f"  • {', '.join(csv_file_names)}")
print(f"\n✓ Filter options available:")
print(f"  • Teams: {len(all_teams)} ({', '.join(all_teams)})")
print(f"  • Titles: {len(all_titles)} ({', '.join(all_titles[:3])}{'...' if len(all_titles) > 3 else ''})")
print(f"  • Locations: {len(all_locations)} ({', '.join(all_locations)})")
print(f"  • Users: {len(all_users)} ({', '.join(all_users)})")
print("\nFeatures:")
print("  • Multi-select filters on the right side")
print("  • Duration histogram with percentile markers (50th, 75th, 95th, 97th)")
print("  • Collapsible histogram and filter panels for full-screen chart view")
print("  • CSV data embedded directly in HTML (no external files needed)")
print("  • Dataset-specific filter options")
print("  • Per-dataset viewport optimization")
print("  • Dynamic filter updates (no apply button needed)")
print("\n" + "="*60)
print("  🚀 How to View the Dashboard")
print("="*60)
print("\n✨ Simply open the file in your browser:")
print("  • Double-click workflow_dashboard.html")
print("  • Or open it from your browser's File menu")
print("\n✅ No web server required! Data is embedded in the HTML.")
print("="*60)
