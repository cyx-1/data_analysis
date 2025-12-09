import pandas as pd
import yaml
from pathlib import Path
import json

# Read chart configuration
config_file = Path('chart.yaml')
if not config_file.exists():
    print("Error: chart.yaml not found")
    exit(1)

with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

chart_title = config.get('title', 'Dashboard')
datasets_config = config.get('datasets', [])

if not datasets_config:
    print("Error: No datasets configured in chart.yaml")
    exit(1)

print(f"Chart Title: {chart_title}")
print(f"Found {len(datasets_config)} dataset(s) in configuration:")

# Read CSV files and convert to JSON for embedding
embedded_data = {}
dataset_metadata = {}

for dataset_cfg in datasets_config:
    csv_file = Path(dataset_cfg['csv_file'])
    dataset_name = dataset_cfg['name']

    if not csv_file.exists():
        print(f"  ⚠️  Warning: {csv_file} not found, skipping...")
        continue

    print(f"  • {dataset_name} ({csv_file})")

    df = pd.read_csv(csv_file)

    # Convert DataFrame to list of dictionaries for embedding
    embedded_data[dataset_name] = df.to_dict('records')

    # Store all column names for this dataset
    dataset_metadata[dataset_name] = {
        'columns': list(df.columns)
    }

if not embedded_data:
    print("Error: No valid CSV files found")
    exit(1)

# Generate HTML with embedded JavaScript
html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chart_title}</title>
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
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        .table-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-height: 400px;
            overflow: auto;
        }}
        .table-container h3 {{
            margin: 0 0 15px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .export-btn {{
            background: #4caf50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: background 0.2s;
        }}
        .export-btn:hover {{
            background: #45a049;
        }}
        .export-btn:disabled {{
            background: #ccc;
            cursor: not-allowed;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        .data-table th {{
            background: #f5f5f5;
            padding: 10px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #ddd;
            position: sticky;
            top: 0;
        }}
        .data-table td {{
            padding: 8px 10px;
            border-bottom: 1px solid #eee;
        }}
        .data-table tr:hover {{
            background: #f9f9f9;
        }}
        .empty-message {{
            text-align: center;
            padding: 40px;
            color: #999;
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
            transition: opacity 0.3s ease, transform 0.3s ease;
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
            transition: opacity 0.3s ease, transform 0.3s ease;
        }}
        .panel-title {{
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
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
            height: 500px;
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
        .settings-icon {{
            position: fixed;
            top: 20px;
            right: 20px;
            width: 44px;
            height: 44px;
            background: white;
            border-radius: 50%;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 22px;
            transition: all 0.2s;
            z-index: 1000;
        }}
        .settings-icon:hover {{
            background: #f5f5f5;
            transform: rotate(90deg);
        }}
        .settings-panel {{
            position: fixed;
            top: 75px;
            right: 20px;
            width: 250px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            padding: 20px;
            z-index: 1000;
            display: none;
        }}
        .settings-panel.active {{
            display: block;
        }}
        .settings-title {{
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
        }}
        .settings-option {{
            display: flex;
            align-items: center;
            padding: 10px 0;
            cursor: pointer;
        }}
        .settings-option input[type="checkbox"] {{
            width: 18px;
            height: 18px;
            cursor: pointer;
            margin-right: 10px;
        }}
        .settings-option label {{
            cursor: pointer;
            font-size: 14px;
            color: #333;
            flex: 1;
        }}
        .hidden-panel {{
            display: none !important;
        }}
    </style>
</head>
<body>
    <div class="settings-icon" onclick="toggleSettings()" title="Settings">⚙️</div>
    <div class="settings-panel" id="settings-panel">
        <div class="settings-title">Display Settings</div>
        <div class="settings-option">
            <input type="checkbox" id="show-histogram" checked onchange="togglePanelVisibility('histogram-panel', this.checked)">
            <label for="show-histogram">Performance Distribution</label>
        </div>
        <div class="settings-option">
            <input type="checkbox" id="show-filters" checked onchange="togglePanelVisibility('filters-panel', this.checked)">
            <label for="show-filters">Filters</label>
        </div>
    </div>
    <h1>{chart_title}</h1>
    <div class="container">
        <div class="main-content">
            <div class="chart-container">
                <div id="plot"></div>
            </div>
            <div class="table-container">
                <h3>
                    <span>📋 Selected Data Points (<span id="selected-count">0</span>)</span>
                    <button class="export-btn" id="export-btn" onclick="exportToCSV()" disabled>📥 Export CSV</button>
                </h3>
                <div id="data-table-container">
                    <div class="empty-message">Click on data points in the chart to select them</div>
                </div>
            </div>
        </div>
        <div class="histogram-container" id="histogram-panel">
            <div class="panel-title">📊 Performance Distribution</div>
            <div id="histogram"></div>
            <div class="percentile-info" id="percentile-info"></div>
        </div>
        <div class="filters-container" id="filters-panel">
            <div class="panel-title">🔍 Filters</div>
            <div class="filter-section">
                <h3 onclick="toggleSection(this)">📁 Dataset</h3>
                <div class="filter-content">
                    <select id="dataset-select" class="filter-select" onchange="onDatasetChange()">
                    </select>
                </div>
            </div>

            <div class="filter-section">
                <h3 onclick="toggleSection(this)">🎨 Color By</h3>
                <div class="filter-content">
                    <select id="color-by-select" class="filter-select" onchange="onColorByChange()">
                    </select>
                </div>
            </div>

            <div id="dynamic-filters"></div>

            <div class="info-text">
                💡 <strong>Click section headers</strong> to collapse/expand filters. Filters update dynamically.
                <br><br>
                📊 Each dataset has its own viewport and filter options specific to that dataset.
                <br><br>
                📈 Performance Distribution shows duration with percentile markers (50th, 75th, 95th, 97th).
                <br><br>
                ⚙️ <strong>Click the gear icon</strong> (top right) to show/hide panels for full-screen chart view.
                <br><br>
                🖱️ Click data points to select them. Selected points appear in the table below the chart.
                <br><br>
                ℹ️ To reconfigure: Edit <code>chart.yaml</code> and run <code>uv run visualize.py</code> to regenerate.
                <br><br>
                ✨ CSV data is embedded - no web server required! Just open this HTML file in your browser.
            </div>
            </div>
        </div>
    </div>

    <script>
        // Configuration from YAML
        const CHART_CONFIG = {json.dumps(config)};
        const EMBEDDED_DATA = {json.dumps(embedded_data)};
        const DATASET_METADATA = {json.dumps(dataset_metadata)};

        const COLOR_PALETTE = [
            '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00',
            '#ffff33', '#a65628', '#f781bf', '#999999', '#66c2a5'
        ];

        let allData = [];
        let datasetAxisRanges = {{}};
        let datasetFilterMetadata = {{}};
        let selectedPoints = new Set();
        let currentDatasetConfig = null;
        let colorGroupBy = null;  // Track which attribute determines color
        let colorMap = {{}};  // Map values to colors

        // Toggle filter section collapse/expand
        function toggleSection(header) {{
            header.classList.toggle('collapsed');
            const content = header.nextElementSibling;
            content.classList.toggle('collapsed');
        }}

        // Toggle settings panel
        function toggleSettings() {{
            const settingsPanel = document.getElementById('settings-panel');
            settingsPanel.classList.toggle('active');
        }}

        // Toggle panel visibility
        function togglePanelVisibility(panelId, isVisible) {{
            const panel = document.getElementById(panelId);
            if (isVisible) {{
                panel.classList.remove('hidden-panel');
            }} else {{
                panel.classList.add('hidden-panel');
            }}

            // Resize plot to take advantage of new space
            setTimeout(() => {{
                const plotDiv = document.getElementById('plot');
                if (plotDiv && plotDiv.data) {{
                    Plotly.Relayout('plot', {{
                        autosize: true
                    }}).then(() => {{
                        // Force a full redraw
                        window.dispatchEvent(new Event('resize'));
                    }});
                }}
            }}, 350); // Wait for CSS transition
        }}

        // Close settings panel when clicking outside
        document.addEventListener('click', function(event) {{
            const settingsPanel = document.getElementById('settings-panel');
            const settingsIcon = document.querySelector('.settings-icon');

            if (!settingsPanel.contains(event.target) && !settingsIcon.contains(event.target)) {{
                settingsPanel.classList.remove('active');
            }}
        }});

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
            if (!currentDatasetConfig || filteredData.length === 0) {{
                document.getElementById('histogram').innerHTML = '<p style="text-align: center; padding: 20px; color: #999;">No data to display</p>';
                document.getElementById('percentile-info').innerHTML = '';
                return;
            }}

            const yColumn = currentDatasetConfig.y_axis.column;
            const durations = filteredData.map(d => parseFloat(d[yColumn]));
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
                xaxis: {{ title: currentDatasetConfig.y_axis.label }},
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
                <div>🟢 50th: ${{percentiles[50].toFixed(2)}}</div>
                <div>🟠 75th: ${{percentiles[75].toFixed(2)}}</div>
                <div>🔴 95th: ${{percentiles[95].toFixed(2)}}</div>
                <div>🟣 97th: ${{percentiles[97].toFixed(2)}}</div>
            `;
        }}

        // Update filter options based on selected dataset
        function updateFiltersForDataset(datasetName) {{
            const datasetCfg = CHART_CONFIG.datasets.find(d => d.name === datasetName);
            if (!datasetCfg) return;

            currentDatasetConfig = datasetCfg;
            const metadata = datasetFilterMetadata[datasetName];
            if (!metadata) return;

            // Clear existing dynamic filters
            const dynamicFiltersContainer = document.getElementById('dynamic-filters');
            dynamicFiltersContainer.innerHTML = '';

            // Populate Color By dropdown
            const colorBySelect = document.getElementById('color-by-select');
            colorBySelect.innerHTML = '';
            datasetCfg.filters.forEach((filterCfg, index) => {{
                const option = document.createElement('option');
                option.value = filterCfg.column;
                option.textContent = filterCfg.label;
                colorBySelect.appendChild(option);
            }});
            // Set default to first filter column
            colorGroupBy = datasetCfg.filters[0]?.column;
            colorBySelect.value = colorGroupBy;

            // Create filter sections based on configuration
            datasetCfg.filters.forEach((filterCfg, index) => {{
                const column = filterCfg.column;
                const label = filterCfg.label;
                const icon = filterCfg.icon || '🔹';
                const values = metadata[column] || [];

                // Determine if this section should be expanded (first two) or collapsed
                const isCollapsed = index >= 2;
                const collapsedClass = isCollapsed ? 'collapsed' : '';

                const filterSection = `
                    <div class="filter-section">
                        <h3 onclick="toggleSection(this)" class="${{collapsedClass}}">${{icon}} ${{label}}</h3>
                        <div class="filter-content ${{collapsedClass}}">
                            <div class="filter-options" id="filter-${{column}}"></div>
                            <div class="filter-actions">
                                <button class="btn" onclick="selectAll('${{column}}')">All</button>
                                <button class="btn" onclick="clearAll('${{column}}')">None</button>
                            </div>
                        </div>
                    </div>
                `;
                dynamicFiltersContainer.innerHTML += filterSection;

                // Populate filter options
                const container = document.getElementById(`filter-${{column}}`);
                values.forEach(value => {{
                    container.appendChild(createCheckbox(value, column, true));
                }});
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
        function selectAll(column) {{
            document.querySelectorAll(`[data-type="${{column}}"]:not(:checked)`).forEach(cb => cb.checked = true);
            applyFilters();
        }}
        function clearAll(column) {{
            document.querySelectorAll(`[data-type="${{column}}"]:checked`).forEach(cb => cb.checked = false);
            applyFilters();
        }}

        // Load embedded data
        function loadEmbeddedData() {{
            allData = [];

            CHART_CONFIG.datasets.forEach(datasetCfg => {{
                const datasetName = datasetCfg.name;
                const datasetData = EMBEDDED_DATA[datasetName];

                if (datasetData) {{
                    datasetData.forEach(row => {{
                        row._dataset = datasetName;
                        allData.push(row);
                    }});
                }}
            }});

            // Calculate axis ranges and filter metadata per dataset
            CHART_CONFIG.datasets.forEach(datasetCfg => {{
                const datasetName = datasetCfg.name;
                const datasetData = allData.filter(row => row._dataset === datasetName);

                if (datasetData.length > 0) {{
                    const xColumn = datasetCfg.x_axis.column;
                    const yColumn = datasetCfg.y_axis.column;

                    const xValues = datasetData.map(d => new Date(d[xColumn]));
                    const yValues = datasetData.map(d => parseFloat(d[yColumn]));

                    const minX = new Date(Math.min(...xValues));
                    const maxX = new Date(Math.max(...xValues));
                    const minY = Math.min(...yValues);
                    const maxY = Math.max(...yValues);

                    const xPadding = (maxX - minX) * 0.05;
                    const yPadding = (maxY - minY) * 0.05;

                    datasetAxisRanges[datasetName] = {{
                        xaxis: [new Date(minX.getTime() - xPadding), new Date(maxX.getTime() + xPadding)],
                        yaxis: [minY - yPadding, maxY + yPadding]
                    }};

                    // Build filter metadata
                    const filterMetadata = {{}};
                    datasetCfg.filters.forEach(filterCfg => {{
                        const column = filterCfg.column;
                        filterMetadata[column] = [...new Set(datasetData.map(d => d[column]))].sort();
                    }});
                    datasetFilterMetadata[datasetName] = filterMetadata;
                }}
            }});

            return allData;
        }}

        // Get selected filter values
        function getSelectedFilters() {{
            const datasetSelect = document.getElementById('dataset-select');
            const datasetName = datasetSelect.value;
            const datasetCfg = CHART_CONFIG.datasets.find(d => d.name === datasetName);

            const filters = {{
                dataset: datasetName
            }};

            if (datasetCfg) {{
                datasetCfg.filters.forEach(filterCfg => {{
                    const column = filterCfg.column;
                    filters[column] = Array.from(document.querySelectorAll(`[data-type="${{column}}"]:checked`))
                        .map(cb => cb.dataset.value);
                }});
            }}

            return filters;
        }}

        // Apply filters and update plot
        function applyFilters() {{
            const filters = getSelectedFilters();
            const datasetCfg = CHART_CONFIG.datasets.find(d => d.name === filters.dataset);
            if (!datasetCfg) return;

            // Filter data
            let filteredData = allData.filter(row => row._dataset === filters.dataset);

            // Apply each configured filter
            datasetCfg.filters.forEach(filterCfg => {{
                const column = filterCfg.column;
                // Only filter if there are selected values (empty array means show all)
                if (filters[column] && filters[column].length > 0) {{
                    filteredData = filteredData.filter(row => filters[column].includes(row[column]));
                }}
            }});

            // Use colorGroupBy for grouping and coloring
            const groupColumn = colorGroupBy || datasetCfg.filters[0]?.column || 'user_name';

            // Group by the selected color attribute
            const dataByGroup = {{}};
            filteredData.forEach(row => {{
                const groupValue = row[groupColumn];
                if (!dataByGroup[groupValue]) {{
                    dataByGroup[groupValue] = [];
                }}
                dataByGroup[groupValue].push(row);
            }});

            // Get unique values for coloring
            const uniqueGroups = [...new Set(filteredData.map(r => r[groupColumn]))].sort();

            // Build color map for consistent coloring
            colorMap = {{}};
            uniqueGroups.forEach((value, idx) => {{
                colorMap[value] = COLOR_PALETTE[idx % COLOR_PALETTE.length];
            }});

            // Create traces
            const xColumn = datasetCfg.x_axis.column;
            const yColumn = datasetCfg.y_axis.column;
            const traces = [];

            uniqueGroups.forEach((groupValue, idx) => {{
                if (dataByGroup[groupValue]) {{
                    const groupData = dataByGroup[groupValue];

                    // Get all column names for customdata
                    const columns = DATASET_METADATA[filters.dataset].columns;

                    traces.push({{
                        x: groupData.map(d => d[xColumn]),
                        y: groupData.map(d => parseFloat(d[yColumn])),
                        mode: 'markers',
                        type: 'scatter',
                        name: groupValue,
                        marker: {{
                            size: 10,
                            color: COLOR_PALETTE[idx % COLOR_PALETTE.length],
                            line: {{ width: 1, color: 'white' }},
                            opacity: 0.8
                        }},
                        customdata: groupData.map(d => columns.map(col => d[col])),
                        hovertemplate: buildHoverTemplate(columns, xColumn, yColumn),
                        text: groupData.map((d, i) => i) // Store index for selection
                    }});
                }}
            }});

            // Get axis ranges for the selected dataset
            const axisRanges = datasetAxisRanges[filters.dataset];

            const layout = {{
                xaxis: {{
                    title: datasetCfg.x_axis.label,
                    range: axisRanges.xaxis
                }},
                yaxis: {{
                    title: datasetCfg.y_axis.label,
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

            // Add click handler for point selection
            document.getElementById('plot').on('plotly_click', function(data) {{
                const point = data.points[0];
                const pointData = {{}};
                const columns = DATASET_METADATA[filters.dataset].columns;
                columns.forEach((col, idx) => {{
                    pointData[col] = point.customdata[idx];
                }});

                // Create unique ID for this point
                const pointId = JSON.stringify(pointData);

                if (selectedPoints.has(pointId)) {{
                    selectedPoints.delete(pointId);
                }} else {{
                    selectedPoints.add(pointId);
                }}

                updateDataTable();
            }});

            // Update histogram with filtered data
            updateHistogram(filteredData);
        }}

        function buildHoverTemplate(columns, xColumn, yColumn) {{
            let template = '<b>%{{x}}</b><br>';
            columns.forEach((col, idx) => {{
                if (col !== xColumn) {{
                    template += `${{col}}: %{{customdata[${{idx}}]}}<br>`;
                }}
            }});
            template += '<extra></extra>';
            return template;
        }}

        // Update data table with selected points
        function updateDataTable() {{
            const container = document.getElementById('data-table-container');
            const countSpan = document.getElementById('selected-count');
            const exportBtn = document.getElementById('export-btn');

            countSpan.textContent = selectedPoints.size;
            exportBtn.disabled = selectedPoints.size === 0;

            if (selectedPoints.size === 0) {{
                container.innerHTML = '<div class="empty-message">Click on data points in the chart to select them</div>';
                return;
            }}

            // Convert selected points to array
            const selectedData = Array.from(selectedPoints).map(pointId => JSON.parse(pointId));

            // Get columns from first point
            const columns = Object.keys(selectedData[0]).filter(c => c !== '_dataset');

            // Build table
            let tableHTML = '<table class="data-table"><thead><tr>';
            columns.forEach(col => {{
                tableHTML += `<th>${{col}}</th>`;
            }});
            tableHTML += '</tr></thead><tbody>';

            selectedData.forEach(point => {{
                tableHTML += '<tr>';
                columns.forEach(col => {{
                    tableHTML += `<td>${{point[col] || ''}}</td>`;
                }});
                tableHTML += '</tr>';
            }});

            tableHTML += '</tbody></table>';
            container.innerHTML = tableHTML;
        }}

        // Export selected points to CSV
        function exportToCSV() {{
            if (selectedPoints.size === 0) return;

            const selectedData = Array.from(selectedPoints).map(pointId => JSON.parse(pointId));
            const columns = Object.keys(selectedData[0]).filter(c => c !== '_dataset');

            // Build CSV
            let csv = columns.join(',') + '\\n';
            selectedData.forEach(point => {{
                const row = columns.map(col => {{
                    const value = point[col] || '';
                    // Escape commas and quotes
                    if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {{
                        return '"' + value.replace(/"/g, '""') + '"';
                    }}
                    return value;
                }});
                csv += row.join(',') + '\\n';
            }});

            // Download
            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'selected_data.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}

        // Initialize dataset dropdown
        function initializeFilters() {{
            const datasetSelect = document.getElementById('dataset-select');
            CHART_CONFIG.datasets.forEach(datasetCfg => {{
                const option = document.createElement('option');
                option.value = datasetCfg.name;
                option.textContent = datasetCfg.label || datasetCfg.name;
                datasetSelect.appendChild(option);
            }});
        }}

        // Handle dataset change
        function onDatasetChange() {{
            const datasetSelect = document.getElementById('dataset-select');
            selectedPoints.clear(); // Clear selections when changing dataset
            updateFiltersForDataset(datasetSelect.value);
            applyFilters();
        }}

        // Handle color by change
        function onColorByChange() {{
            const colorBySelect = document.getElementById('color-by-select');
            colorGroupBy = colorBySelect.value;
            applyFilters();
        }}

        // Initialize on page load
        initializeFilters();
        loadEmbeddedData();

        // Update filters for first dataset after data is loaded
        if (CHART_CONFIG.datasets.length > 0) {{
            const datasetSelect = document.getElementById('dataset-select');
            updateFiltersForDataset(datasetSelect.value || CHART_CONFIG.datasets[0].name);
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
print(f"✓ Configuration from: chart.yaml")
print(f"✓ Datasets embedded: {len(embedded_data)}")

for dataset_cfg in datasets_config:
    if dataset_cfg['name'] in embedded_data:
        print(f"  • {dataset_cfg['label']} ({dataset_cfg['csv_file']})")

print("\nFeatures:")
print("  • YAML-based configuration (chart.yaml)")
print("  • Multi-select data points with click")
print("  • Selected points table with CSV export")
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
print("\n📝 To reconfigure: Edit chart.yaml and run 'uv run visualize.py'")
print("="*60)
