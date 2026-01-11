"""
CRM Cron Jobs
Heartbeat logger to monitor application health
"""

from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes to confirm CRM health.
    Queries GraphQL hello field to verify endpoint responsiveness.
    """
    # Get current timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    # Base log message
    log_message = f"{timestamp} CRM is alive"
    
    # Query GraphQL hello field to verify endpoint
    try:
        # Setup GraphQL client
        transport = RequestsHTTPTransport(url='http://localhost:8000/graphql')
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # Query hello field
        query = gql('''
            query {
                hello
            }
        ''')
        
        result = client.execute(query)
        
        if result.get('hello'):
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
