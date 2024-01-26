from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB (make sure MongoDB server is running)
client = MongoClient('mongodb://localhost:27017/')
db = client['calories_database']
collection = db['daily_calories']

def get_current_date():
    return datetime.now().strftime('%Y-%m-%d')

def get_total_calories_for_date(date):
    entry = collection.find_one({'date': date})
    return entry['total_calories'] if entry else 0

# Get the daily calorie input from the user
calories_str = input("Enter the daily calories: ")

# Validate input and convert calories to an integer
try:
    calories = int(calories_str)
except ValueError:
    print("Invalid input for calories. Please enter a valid number.")
    client.close()
    exit()

# Get the current date
current_date = get_current_date()

# Check if an entry for the current date already exists
existing_entry = collection.find_one({'date': current_date})

if existing_entry:
    # If an entry exists, update the total calories
    new_total_calories = existing_entry['total_calories'] + calories
    collection.update_one({'date': current_date}, {'$set': {'total_calories': new_total_calories}})
    print("Added {} calories to the existing entry for {}.".format(calories, current_date))
else:
    # If no entry exists, create a new entry
    daily_data = {
        'date': current_date,
        'total_calories': calories
    }
    collection.insert_one(daily_data)
    print("Daily calories for {} added to the MongoDB database.".format(current_date))

# Close the MongoDB connection
client.close()
