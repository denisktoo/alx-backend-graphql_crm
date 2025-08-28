#!/bin/bash

# Move to the project root
cd "$(dirname "$0")/../.."

# Activate virtual environment
source env/bin/activate

# Run Python code and extract only the Deleted message
log_message=$(python manage.py shell -c "
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)
customers_to_delete = Customer.objects.exclude(orders__order_date__gte=one_year_ago)
deleted_count = customers_to_delete.count()
customers_to_delete.delete()

print(f'Deleted {deleted_count} customers with no orders earlier than {one_year_ago.date()}')
" | grep '^Deleted')

timestamp=$(date '+%Y-%m-%d %H:%M:%S')
echo "$timestamp - $log_message" >> tmp/customer_cleanup_log.txt

echo "$timestamp - $log_message"
