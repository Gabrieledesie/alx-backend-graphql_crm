"""
CRM Cron Jobs
Heartbeat logger to monitor application health
"""

from datetime import datetime
import requests


def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes to confirm CRM health.
    Optionally queries GraphQL hello field to verify endpoint responsiveness.
    """
    # Get current timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    # Base log message
    log_message = f"{timestamp} CRM is alive"
    
    # Optional: Query GraphQL hello field to verify endpoint
    try:
        graphql_query = {
            'query': '{ hello }'
        }
        response = requests.post(
            'http://localhost:8000/graphql',
            json=graphql_query,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('hello'):
                log_message += " - GraphQL endpoint responsive"
        else:
            log_message += " - GraphQL endpoint not responding"
    except Exception as e:
        log_message += f" - GraphQL check failed: {str(e)}"
    
    # Append to log file
    log_file = '/tmp/crm_heartbeat_log.txt'
    with open(log_file, 'a') as f:
        f.write(log_message + '\n')
    
    print(log_message)
