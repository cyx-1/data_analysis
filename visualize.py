import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import plotly.express as px

# Find all CSV files matching the pattern
csv_files = sorted(Path('.').glob('workflow_data*.csv'))

if not csv_files:
    print("Error: No CSV files found matching 'workflow_data*.csv'")
    exit(1)

print(f"Found {len(csv_files)} CSV file(s):")
for f in csv_files:
    print(f"  • {f.name}")

# Read and process all CSV files
datasets = {}
for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    datasets[csv_file.name] = df

# Collect all unique values for filters across all datasets
all_teams = set()
all_titles = set()
all_locations = set()
all_workflows = set()
all_users = set()

for df in datasets.values():
    all_teams.update(df['team'].unique())
    all_titles.update(df['title'].unique())
    all_locations.update(df['location'].unique())
    all_workflows.update(df['workflow_name'].unique())
    all_users.update(df['user_name'].unique())

all_teams = sorted(all_teams)
all_titles = sorted(all_titles)
all_locations = sorted(all_locations)
all_workflows = sorted(all_workflows)
all_users = sorted(all_users)

# Calculate global axis ranges for viewport preservation
all_timestamps = []
all_durations = []
for df in datasets.values():
    all_timestamps.extend(df['timestamp'].tolist())
    all_durations.extend(df['duration'].tolist())

# Add padding to ranges
time_range = [min(all_timestamps), max(all_timestamps)]
time_padding = (time_range[1] - time_range[0]) * 0.05
time_range = [time_range[0] - time_padding, time_range[1] + time_padding]

duration_range = [min(all_durations), max(all_durations)]
duration_padding = (duration_range[1] - duration_range[0]) * 0.05
duration_range = [duration_range[0] - duration_padding, duration_range[1] + duration_padding]

# Create color mapping for users
color_map = {user: px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)]
             for i, user in enumerate(all_users)}

# Create figure
fig = go.Figure()

# Store trace metadata for filtering
trace_metadata = []

# Create traces for each dataset and user combination
for dataset_idx, (csv_name, df) in enumerate(datasets.items()):
    users = df['user_name'].unique()

    for user in users:
        user_df = df[df['user_name'] == user]

        # Get user attributes
        team = user_df['team'].iloc[0]
        title = user_df['title'].iloc[0]
        location = user_df['location'].iloc[0]

        # Create custom data for hover with all attributes
        customdata = user_df[['user_name', 'workflow_name', 'correlation_id', 'team', 'title', 'location']].values

        trace = go.Scatter(
            x=user_df['timestamp'],
            y=user_df['duration'],
            mode='markers',
            name=user,
            marker=dict(
                size=10,
                color=color_map.get(user, '#000000'),
                line=dict(width=1, color='white'),
                opacity=0.8
            ),
            customdata=customdata,
            hovertemplate='<b>%{customdata[1]}</b><br>' +
                         'User: %{customdata[0]}<br>' +
                         'Team: %{customdata[3]}<br>' +
                         'Title: %{customdata[4]}<br>' +
                         'Location: %{customdata[5]}<br>' +
                         'Time: %{x|%Y-%m-%d %H:%M:%S}<br>' +
                         'Duration: %{y:.2f}s<br>' +
                         'Correlation ID: %{customdata[2]}<br>' +
                         '<extra></extra>',
            visible=(dataset_idx == 0),  # Only first dataset visible initially
        )
        fig.add_trace(trace)

        # Store metadata for filtering
        trace_metadata.append({
            'dataset': csv_name,
            'user': user,
            'team': team,
            'title': title,
            'location': location
        })

# Helper function to create visibility list based on filters
def create_visibility(dataset_filter=None, team_filter=None, title_filter=None, location_filter=None):
    visibility = []
    for meta in trace_metadata:
        visible = True
        if dataset_filter and meta['dataset'] != dataset_filter:
            visible = False
        if team_filter and team_filter != 'All' and meta['team'] != team_filter:
            visible = False
        if title_filter and title_filter != 'All' and meta['title'] != title_filter:
            visible = False
        if location_filter and location_filter != 'All' and meta['location'] != location_filter:
            visible = False
        visibility.append(visible)
    return visibility

# Create dataset dropdown buttons
dataset_buttons = []
for csv_name in datasets.keys():
    visible = create_visibility(dataset_filter=csv_name)
    button = dict(
        label=csv_name,
        method='update',
        args=[
            {'visible': visible},
            {
                'title': f'Workflow Execution Dashboard - {csv_name}',
                'xaxis.range': time_range,
                'yaxis.range': duration_range
            }
        ]
    )
    dataset_buttons.append(button)

# Create team filter buttons
team_buttons = [dict(
    label='All Teams',
    method='update',
    args=[
        {'visible': create_visibility(dataset_filter=list(datasets.keys())[0])},
        {'xaxis.range': time_range, 'yaxis.range': duration_range}
    ]
)]
for team in all_teams:
    visible = create_visibility(dataset_filter=list(datasets.keys())[0], team_filter=team)
    button = dict(
        label=team,
        method='update',
        args=[
            {'visible': visible},
            {'xaxis.range': time_range, 'yaxis.range': duration_range}
        ]
    )
    team_buttons.append(button)

# Create title filter buttons
title_buttons = [dict(
    label='All Titles',
    method='update',
    args=[
        {'visible': create_visibility(dataset_filter=list(datasets.keys())[0])},
        {'xaxis.range': time_range, 'yaxis.range': duration_range}
    ]
)]
for title in all_titles:
    visible = create_visibility(dataset_filter=list(datasets.keys())[0], title_filter=title)
    button = dict(
        label=title,
        method='update',
        args=[
            {'visible': visible},
            {'xaxis.range': time_range, 'yaxis.range': duration_range}
        ]
    )
    title_buttons.append(button)

# Create location filter buttons
location_buttons = [dict(
    label='All Locations',
    method='update',
    args=[
        {'visible': create_visibility(dataset_filter=list(datasets.keys())[0])},
        {'xaxis.range': time_range, 'yaxis.range': duration_range}
    ]
)]
for location in all_locations:
    visible = create_visibility(dataset_filter=list(datasets.keys())[0], location_filter=location)
    button = dict(
        label=location,
        method='update',
        args=[
            {'visible': visible},
            {'xaxis.range': time_range, 'yaxis.range': duration_range}
        ]
    )
    location_buttons.append(button)

# Update layout with multiple filter dropdowns
fig.update_layout(
    title={
        'text': f'Workflow Execution Dashboard - {csv_files[0].name}',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 24}
    },
    xaxis_title='Execution Time',
    yaxis_title='Duration (seconds)',
    xaxis=dict(range=time_range),
    yaxis=dict(range=duration_range),
    hovermode='closest',
    showlegend=True,
    legend={
        'title': 'User (click to filter)',
        'orientation': 'v',
        'yanchor': 'top',
        'y': 1,
        'xanchor': 'left',
        'x': 1.01
    },
    template='plotly_white',
    height=800,
    updatemenus=[
        # Dataset selector
        dict(
            buttons=dataset_buttons,
            direction='down',
            pad={'r': 10, 't': 10},
            showactive=True,
            x=0.01,
            xanchor='left',
            y=1.22,
            yanchor='top',
            bgcolor='white',
            bordercolor='#333',
            borderwidth=1,
            font=dict(size=10)
        ),
        # Team filter
        dict(
            buttons=team_buttons,
            direction='down',
            pad={'r': 10, 't': 10},
            showactive=True,
            x=0.18,
            xanchor='left',
            y=1.22,
            yanchor='top',
            bgcolor='white',
            bordercolor='#333',
            borderwidth=1,
            font=dict(size=10)
        ),
        # Title filter
        dict(
            buttons=title_buttons,
            direction='down',
            pad={'r': 10, 't': 10},
            showactive=True,
            x=0.35,
            xanchor='left',
            y=1.22,
            yanchor='top',
            bgcolor='white',
            bordercolor='#333',
            borderwidth=1,
            font=dict(size=10)
        ),
        # Location filter
        dict(
            buttons=location_buttons,
            direction='down',
            pad={'r': 10, 't': 10},
            showactive=True,
            x=0.52,
            xanchor='left',
            y=1.22,
            yanchor='top',
            bgcolor='white',
            bordercolor='#333',
            borderwidth=1,
            font=dict(size=10)
        )
    ],
    annotations=[
        dict(
            text='<b>Dataset:</b>',
            x=0.01,
            xref='paper',
            y=1.19,
            yref='paper',
            align='left',
            showarrow=False,
            font=dict(size=11, color='#333')
        ),
        dict(
            text='<b>Team:</b>',
            x=0.18,
            xref='paper',
            y=1.19,
            yref='paper',
            align='left',
            showarrow=False,
            font=dict(size=11, color='#333')
        ),
        dict(
            text='<b>Title:</b>',
            x=0.35,
            xref='paper',
            y=1.19,
            yref='paper',
            align='left',
            showarrow=False,
            font=dict(size=11, color='#333')
        ),
        dict(
            text='<b>Location:</b>',
            x=0.52,
            xref='paper',
            y=1.19,
            yref='paper',
            align='left',
            showarrow=False,
            font=dict(size=11, color='#333')
        ),
        dict(
            text='<i>Use dropdowns to filter data. Legend filters by user. Hover for details. Viewport stays fixed when filtering.</i>',
            x=0.5,
            xref='paper',
            y=-0.12,
            yref='paper',
            xanchor='center',
            showarrow=False,
            font=dict(size=10, color='#666')
        )
    ]
)

# Save to HTML with enhanced interactivity
fig.write_html(
    'workflow_dashboard.html',
    config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': ['hoverclosest', 'hovercompare'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'workflow_dashboard',
            'height': 700,
            'width': 1200,
            'scale': 2
        }
    }
)

print("\n✓ Interactive dashboard created: workflow_dashboard.html")
print(f"✓ Datasets included: {len(datasets)}")
for csv_name, df in datasets.items():
    teams = df['team'].unique()
    locations = df['location'].unique()
    print(f"  • {csv_name}: {len(df)} executions")
    print(f"    - {len(df['user_name'].unique())} users, {len(teams)} teams, {len(locations)} locations")
print(f"\n✓ Filter options available:")
print(f"  • Teams: {len(all_teams)} ({', '.join(all_teams)})")
print(f"  • Titles: {len(all_titles)} ({', '.join(all_titles[:3])}{'...' if len(all_titles) > 3 else ''})")
print(f"  • Locations: {len(all_locations)} ({', '.join(all_locations)})")
print("\nFeatures:")
print("  • Use dropdown menus to filter by dataset, team, title, or location")
print("  • Click legend items to filter by user")
print("  • Viewport stays fixed when filtering (only dots disappear)")
print("  • Hover over points to see all details")
print("  • Use toolbar to zoom, pan, and export")
