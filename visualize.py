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
color_palettes = [px.colors.qualitative.Set1, px.colors.qualitative.Set2, px.colors.qualitative.Set3]

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    datasets[csv_file.name] = df

# Create figure with the first dataset
fig = go.Figure()

# Color mapping for consistent colors across users
all_users = set()
for df in datasets.values():
    all_users.update(df['user_name'].unique())
all_users = sorted(all_users)
color_map = {user: px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)]
             for i, user in enumerate(all_users)}

# Create traces for each dataset and user combination
dropdown_buttons = []

for dataset_idx, (csv_name, df) in enumerate(datasets.items()):
    users = df['user_name'].unique()

    for user in users:
        user_df = df[df['user_name'] == user]

        # Create custom data for hover
        customdata = user_df[['user_name', 'workflow_name', 'correlation_id']].values

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
                         'Time: %{x|%Y-%m-%d %H:%M:%S}<br>' +
                         'Duration: %{y:.2f}s<br>' +
                         'Correlation ID: %{customdata[2]}<br>' +
                         '<extra></extra>',
            visible=(dataset_idx == 0)  # Only first dataset visible initially
        )
        fig.add_trace(trace)

# Create dropdown menu buttons
current_trace_idx = 0
for dataset_idx, (csv_name, df) in enumerate(datasets.items()):
    num_users = len(df['user_name'].unique())

    # Create visibility list for this dataset
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
    dropdown_buttons.append(button)
    current_trace_idx += num_users

# Update layout with dropdown
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
    height=700,
    updatemenus=[
        dict(
            buttons=dropdown_buttons,
            direction='down',
            pad={'r': 10, 't': 10},
            showactive=True,
            x=0.01,
            xanchor='left',
            y=1.15,
            yanchor='top',
            bgcolor='white',
            bordercolor='#333',
            borderwidth=1,
            font=dict(size=12)
        )
    ],
    annotations=[
        dict(
            text='Select Dataset:',
            x=0,
            xref='paper',
            y=1.12,
            yref='paper',
            align='left',
            showarrow=False,
            font=dict(size=14, color='#333')
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
    print(f"  • {csv_name}: {len(df)} executions, {len(df['user_name'].unique())} users")
print("\nFeatures:")
print("  • Use dropdown menu to switch between datasets")
print("  • Click legend items to filter by user")
print("  • Hover over points to see details")
print("  • Use toolbar to zoom, pan, and export")
