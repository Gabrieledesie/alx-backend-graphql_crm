#!/usr/bin/env python3
"""
Order Reminders Script
Queries GraphQL for pending orders in the last 7 days and logs reminders
"""

import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Django setup
sys.path.append('/path/to/alx-backend-graphql_crm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')

import django
django.setup()

# GraphQL client setup
transport = RequestsHTTPTransport(url='http://localhost:8000/graphql')
client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date 7 days ago
seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

# GraphQL query for recent orders
query = gql('''
    query GetRecentOrders($startDate: Date!) {
        allOrders(orderDate_Gte: $startDate) {
            id
            customer {
                email
            }
            orderDate
        }
    }
''')

# Execute query
variables = {'startDate': seven_days_ago}
result = client.execute(query, variable_values=variables)

# Get timestamp
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Log reminders
log_file = '/tmp/order_reminders_log.txt'
with open(log_file, 'a') as f:
    f.write(f"[{timestamp}] Order reminders batch started\n")
    
    if result.get('allOrders'):
        for order in result['allOrders']:
            order_id = order['id']
            customer_email = order['customer']['email']
            order_date = order['orderDate']
            
            log_entry = f"[{timestamp}] Order ID: {order_id}, Customer: {customer_email}, Date: {order_date}\n"
            f.write(log_entry)
    else:
        f.write(f"[{timestamp}] No orders found in the last 7 days\n")
    
    f.write(f"[{timestamp}] Order reminders batch completed\n\n")

# Print confirmation
print("Order reminders processed!")
