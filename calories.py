from datetime import datetime, timedelta
from pymongo import MongoClient
import sys

# Function to get MongoDB connection
def get_mongo_connection(database_name='calories_database', collection_name='daily_calories'):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[database_name]
    collection = db[collection_name]
    return client, db, collection

# Function to get the start of the month
def get_start_of_month(year, month):
    start_of_month = datetime(year, month, 1)
    return start_of_month

# Function to get the end of the month
def get_end_of_month(year, month):
    next_month = datetime(year, month, 28) + timedelta(days=4)
    end_of_month = next_month - timedelta(days=next_month.day)
    return end_of_month

# Function to calculate average calories per month
def calculate_average_calories(year, month, collection):
    start_date = get_start_of_month(year, month)
    end_date = get_end_of_month(year, month)

    entries = collection.find({'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lte': end_date.strftime('%Y-%m-%d')}})

    total_calories = 0
    count_entries = 0

    for entry in entries:
        total_calories += entry['total_calories']
        count_entries += 1

    return total_calories / count_entries if count_entries > 0 else 0

# Function to add daily calories to the database
def add_daily_calories(collection):
    calories_str = input("Enter the daily calories: ")

    try:
        calories = int(calories_str)
    except ValueError:
        print("Invalid input for calories. Please enter a valid number.")
        return

    current_date = datetime.now().strftime('%Y-%m-%d')
    existing_entry = collection.find_one({'date': current_date})

    if existing_entry:
        new_total_calories = existing_entry['total_calories'] + calories
        collection.update_one({'date': current_date}, {'$set': {'total_calories': new_total_calories}})
        print("Added {} calories to the existing entry for {}.".format(calories, current_date))
    else:
        daily_data = {
            'date': current_date,
            'total_calories': calories
        }
        collection.insert_one(daily_data)
        print("Daily calories for {} added to the MongoDB database.".format(current_date))

# Function to list calories for the current month
def list_calories_for_current_month(collection):
    start_date = get_start_of_month(datetime.now().year, datetime.now().month)
    end_date = get_end_of_month(datetime.now().year, datetime.now().month)

    entries = collection.find({'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lte': end_date.strftime('%Y-%m-%d')}}).sort('date')

    print("Dates and Calories for the Current Month:")
    for entry in entries:
        print("Date: {}, Calories: {}".format(entry['date'], entry['total_calories']))

# Function to show the average of this month's calories
def show_average_calories(collection):
    current_year = datetime.now().year
    current_month = datetime.now().month

    average_calories = calculate_average_calories(current_year, current_month, collection)
    print("Average Calories for the Current Month: {:.2f}".format(average_calories))

# Main function to start the program
def start():
    # Use the get_mongo_connection function to get the MongoDB connection
    client, db, collection = get_mongo_connection()

    while True:
        try:
            choice = int(input("Enter 1 to add calories to database:\nEnter 2 to list the calories of the current month:\nEnter 3 to show the average of this month's calories:\nEnter 4 to exit:\n"))
        except ValueError:
            print("Input is invalid...")
            continue

        if choice == 1:
            add_daily_calories(collection)
            print("\n")

        elif choice == 2:
            list_calories_for_current_month(collection)
            print("\n")

        elif choice == 3:
            show_average_calories(collection)
            print("\n")
            
        elif choice == 4:
            print("Exiting")
            client.close()
            sys.exit()

# Run the program
if __name__ == "__main__":
    start()
