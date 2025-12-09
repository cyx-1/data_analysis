import csv
import random
from datetime import datetime, timedelta

# Generate 100 dummy data points
users = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
workflows = ['Data Processing', 'Model Training', 'ETL Pipeline', 'Report Generation', 'Data Validation']
teams = ['Engineering', 'Data Science', 'Analytics', 'Operations']
titles = ['Data Engineer', 'ML Engineer', 'Senior Analyst', 'Data Scientist', 'DevOps Engineer']
locations = ['New York', 'San Francisco', 'London', 'Tokyo', 'Remote']

# User profiles with consistent attributes
user_profiles = {
    'Alice': {'team': 'Engineering', 'title': 'Data Engineer', 'location': 'New York'},
    'Bob': {'team': 'Data Science', 'title': 'ML Engineer', 'location': 'San Francisco'},
    'Charlie': {'team': 'Analytics', 'title': 'Senior Analyst', 'location': 'London'},
    'Diana': {'team': 'Data Science', 'title': 'Data Scientist', 'location': 'Remote'},
    'Eve': {'team': 'Operations', 'title': 'DevOps Engineer', 'location': 'Tokyo'}
}

start_date = datetime(2025, 11, 1)
data = []

for i in range(100):
    user = random.choice(users)
    workflow = random.choice(workflows)
    timestamp = start_date + timedelta(
        days=random.randint(0, 30),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    duration = round(random.uniform(5, 300), 2)  # Duration in seconds (5s to 5 minutes)
    correlation_id = f"corr-{i+1:04d}-{random.randint(1000, 9999)}"

    # SLA attributes
    expected_duration = round(random.uniform(150, 250), 2)  # Expected SLA duration
    is_sla_met = 'Yes' if duration <= expected_duration else 'No'

    data.append({
        'user_name': user,
        'workflow_name': workflow,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': duration,
        'correlation_id': correlation_id,
        'team': user_profiles[user]['team'],
        'title': user_profiles[user]['title'],
        'location': user_profiles[user]['location'],
        'expected_duration': expected_duration,
        'is_sla_met': is_sla_met
    })

# Write to CSV
with open('workflow_data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['user_name', 'workflow_name', 'timestamp', 'duration', 'correlation_id', 'team', 'title', 'location', 'expected_duration', 'is_sla_met'])
    writer.writeheader()
    writer.writerows(data)

print("Generated workflow_data.csv with 100 data points")
