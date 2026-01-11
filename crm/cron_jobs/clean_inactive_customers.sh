#!/bin/bash

# Customer Cleanup Script
# Deletes customers with no orders in the past year

# Change to project directory
cd /c/Users/HP/Desktop/alx_backend_graphql_crm

# Get timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Run Django command to delete inactive customers
DELETED_COUNT=$(python manage.py shell << PYTHON_EOF
from crm.models import Customer, Order
from datetime import datetime, timedelta
from django.utils import timezone

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders in the past year
inactive_customers = Customer.objects.exclude(
    orders__created_at__gte=one_year_ago
)

# Count and delete
count = inactive_customers.count()
inactive_customers.delete()

print(count)
PYTHON_EOF
)

# Log the result
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt
