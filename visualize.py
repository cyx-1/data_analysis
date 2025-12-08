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

# Create color mapping for users
color_map = {user: px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)]
             for i, user in enumerate(all_users)}

# Create figure
fig = go.Figure()

# Create traces for each dataset and user combination
for dataset_idx, (csv_name, df) in enumerate(datasets.items()):
    users = df['user_name'].unique()

    for user in users:
        user_df = df[df['user_name'] == user]

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
            # Store metadata for filtering
            meta={'dataset': csv_name,
                  'team': user_df['team'].iloc[0],
                  'title': user_df['title'].iloc[0],
                  'location': user_df['location'].iloc[0]}
        )
        fig.add_trace(trace)

# Create dataset dropdown buttons
dataset_buttons = []
current_trace_idx = 0
dataset_trace_ranges = {}

for dataset_idx, (csv_name, df) in enumerate(datasets.items()):
    num_users = len(df['user_name'].unique())
    dataset_trace_ranges[csv_name] = (current_trace_idx, current_trace_idx + num_users)

    visible = [False] * len(fig.data)
    for i in range(current_trace_idx, current_trace_idx + num_users):
        visible[i] = True

    button = dict(
        label=csv_name,
        method='update',
        args=[
            {'visible': visible},
            {'title': f'Workflow Execution Dashboard - {csv_name}'}
        ]
    )
    dataset_buttons.append(button)
    current_trace_idx += num_users

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
    height=750,
    updatemenus=[
        # Dataset selector
        dict(
            buttons=dataset_buttons,
            direction='down',
            pad={'r': 10, 't': 10},
            showactive=True,
            x=0.01,
            xanchor='left',
            y=1.18,
            yanchor='top',
            bgcolor='white',
            bordercolor='#333',
            borderwidth=1,
            font=dict(size=11)
        )
    ],
    annotations=[
        dict(
            text='<b>Dataset:</b>',
            x=0,
            xref='paper',
            y=1.15,
            yref='paper',
            align='left',
            showarrow=False,
            font=dict(size=12, color='#333')
        ),
        dict(
            text='<i>Use legend to filter by user. Hover over points for details including team, title, and location.</i>',
            x=0.5,
            xref='paper',
            y=-0.15,
            yref='paper',
            xanchor='center',
            showarrow=False,
            font=dict(size=11, color='#666')
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
print(f"\n✓ Attributes available: team, title, location, workflow, user")
print("\nFeatures:")
print("  • Use dropdown menu to switch between datasets")
print("  • Click legend items to filter by user")
print("  • Hover over points to see all details (team, title, location, etc.)")
print("  • Use toolbar to zoom, pan, and export")
