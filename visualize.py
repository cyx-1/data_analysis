import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Read the CSV data
df = pd.read_csv('workflow_data.csv')

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Sort by timestamp for better visualization
df = df.sort_values('timestamp')

# Create interactive scatter plot
fig = px.scatter(
    df,
    x='timestamp',
    y='duration',
    color='user_name',
    title='Workflow Execution Dashboard',
    labels={
        'timestamp': 'Execution Time',
        'duration': 'Duration (seconds)',
        'user_name': 'User'
    },
    hover_data={
        'user_name': True,
        'workflow_name': True,
        'timestamp': '|%Y-%m-%d %H:%M:%S',
        'duration': ':.2f',
        'correlation_id': True
    },
    template='plotly_white',
    height=700
)

# Customize the layout
fig.update_layout(
    title={
        'text': 'Workflow Execution Dashboard',
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
    }
)

# Customize markers
fig.update_traces(
    marker=dict(
        size=10,
        line=dict(width=1, color='white'),
        opacity=0.8
    ),
    selector=dict(mode='markers')
)

# Customize hover template
fig.update_traces(
    hovertemplate='<b>%{customdata[1]}</b><br>' +
                  'User: %{customdata[0]}<br>' +
                  'Time: %{x}<br>' +
                  'Duration: %{y:.2f}s<br>' +
                  'Correlation ID: %{customdata[4]}<br>' +
                  '<extra></extra>',
    customdata=df[['user_name', 'workflow_name', 'timestamp', 'duration', 'correlation_id']].values
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

print("✓ Interactive dashboard created: workflow_dashboard.html")
print(f"✓ Visualized {len(df)} workflow executions")
print(f"✓ Users: {', '.join(df['user_name'].unique())}")
print("\nFeatures:")
print("  • Click legend items to filter by user")
print("  • Hover over points to see details")
print("  • Use toolbar to zoom, pan, and export")
