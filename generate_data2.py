import csv
import random
from datetime import datetime, timedelta

# Generate 100 dummy data points for a different team/project
users = ['Frank', 'Grace', 'Henry', 'Isabel', 'Jack']
workflows = ['API Testing', 'Database Migration', 'Security Scan', 'Code Review', 'Deployment']

start_date = datetime(2025, 12, 1)
data = []

for i in range(100):
    user = random.choice(users)
    workflow = random.choice(workflows)
    timestamp = start_date + timedelta(
        days=random.randint(0, 7),  # Just one week of data
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    duration = round(random.uniform(10, 450), 2)  # Duration in seconds (10s to 7.5 minutes)
    correlation_id = f"corr-{i+1:04d}-{random.randint(1000, 9999)}"

    data.append({
        'user_name': user,
        'workflow_name': workflow,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': duration,
        'correlation_id': correlation_id
    })

# Write to CSV
with open('workflow_data2.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['user_name', 'workflow_name', 'timestamp', 'duration', 'correlation_id'])
    writer.writeheader()
    writer.writerows(data)

print("Generated workflow_data2.csv with 100 data points")
