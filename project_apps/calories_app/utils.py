from datetime import datetime, timedelta
from decimal import Decimal

# Function to get the start of the month
def get_start_of_month(year, month):
    return datetime(year, month, 1)

# Function to get the end of the month
def get_end_of_month(year, month):
    next_month = datetime(year, month, 28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)

# Function to calculate average calories
def calculate_average_calories(start_date, end_date, collection):
    entries = collection.find({'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lte': end_date.strftime('%Y-%m-%d')}})
    
    total_calories = 0
    count_entries = 0

    for entry in entries:
        total_calories += entry['total_calories']
        count_entries += 1

    return total_calories / count_entries if count_entries > 0 else 0