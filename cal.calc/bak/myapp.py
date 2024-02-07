#!/usr/bin/python3

from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError
import csv
from io import StringIO
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'mysecretkey123fasfdsgdfbgawttttt+55194'
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Specify the login view

class User(UserMixin):
    def __init__(self, user_id, email, password):
        self.id = user_id
        self.email = email
        self.password = password
        self.calories_collection = None  # New field to store the user's calories collection

# Function to get MongoDB connection
def get_mongo_connection(database_name='calories_database', collection_name='daily_calories'):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[database_name]

    if collection_name == 'daily_calories':
        collection = db[collection_name]
        collection.create_index([('date', ASCENDING)], unique=True)
        users_collection = db['users']
        return client, db, collection, users_collection
    elif collection_name == 'users':
        collection = db[collection_name]
        return client, db, collection
    else:
        # Handle other collections if needed
        collection = db[collection_name]
        return client, db, collection

@login_manager.user_loader
def load_user(user_id):
    _, _, users_collection = get_mongo_connection(collection_name='users')
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})

    if user_data:
        user = User(str(user_data['_id']), user_data['email'], user_data['password'])
        user.calories_collection = get_user_calories_collection(user.id)  # Set calories collection
        return user

    return None  # Return None if user not found

def add_user(email, password):
    _, _, users_collection = get_mongo_connection(collection_name='users')

    # Check if the email already exists
    existing_user = users_collection.find_one({'email': email})
    if existing_user:
        return False  # User already exists

    try:
        # Hash the password before storing
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Store the new user in the 'users' collection without the 'date' field
        user_data = {'email': email, 'password': hashed_password}
        users_collection.insert_one(user_data)
        return True  # User added successfully

    except DuplicateKeyError as e:
        # Handle the case where a duplicate key error occurs
        print(f"Duplicate key error: {str(e)}")
        return False
    
def get_user_calories_collection(user_id):
    _, _, db, _ = get_mongo_connection()
    calories_collection_name = f'user_{user_id}_calories'
    collection = db[calories_collection_name]
    collection.create_index([('date', ASCENDING)], unique=True)
    return collection

def get_user_calorie_items_collection(user_id):
    _, _, db, _ = get_mongo_connection()
    calorie_items_collection_name = f'user_{user_id}_calorie_items'
    collection = db[calorie_items_collection_name]
    return collection

def get_user_by_email(email):
    _, _, users_collection = get_mongo_connection(collection_name='users')  # Updated unpacking
    print(f"Searching for user with email: {email}")
    user_data = users_collection.find_one({'email': email})

    if user_data:
        print(f"Found user data: {user_data}")
        user = User(str(user_data['_id']), user_data['email'], user_data['password'])
        return user
    else:
        print(f"User with email {email} not found.")
        return None

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
def calculate_average_calories(start_date, end_date, collection):
    entries = collection.find({'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lte': end_date.strftime('%Y-%m-%d')}})
    
    total_calories = 0
    count_entries = 0

    for entry in entries:
        total_calories += entry['total_calories']
        count_entries += 1

    return total_calories / count_entries if count_entries > 0 else 0

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_calories', methods=['GET', 'POST'])
@login_required
def add_calories():
    if request.method == 'POST':
        _, _, _, users_collection = get_mongo_connection()

        calories_str = request.form['calories']
        date_str = request.form['date']

        try:
            calories = int(calories_str)
        except ValueError:
            error_message = "Invalid input for calories. Please enter a valid number."
            return render_template('add_calories.html', error_message=error_message)

        try:
            # Convert the date to a datetime object for consistency
            date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')

            # Add a validation check to prevent adding data for dates in the future
            current_date = datetime.now().strftime('%Y-%m-%d')
            if date > current_date:
                error_message = "Invalid date. Future dates are not allowed."
                flash(error_message, 'error')  # Flash the error message
                return render_template('add_calories.html', error_message=error_message)

        except ValueError:
            error_message = "Invalid input for date. Please enter a valid date in the format YYYY-MM-DD."
            return render_template('add_calories.html', error_message=error_message)

        if current_user.calories_collection is None:
            # If calories collection is not set, set it
            current_user.calories_collection = get_user_calories_collection(current_user.id)

        user_calories_collection = current_user.calories_collection

        existing_entry = user_calories_collection.find_one({'date': date})

        if existing_entry:
            new_total_calories = existing_entry['total_calories'] + calories
            user_calories_collection.update_one({'date': date}, {'$set': {'total_calories': new_total_calories}})
            success_message = f"Added {calories} calories to the existing entry for {date}."
            flash(success_message, 'success')  # Flash the success message
            return redirect(url_for('add_calories'))
        else:
            daily_data = {
                'date': date,
                'total_calories': calories
            }
            user_calories_collection.insert_one(daily_data)
            success_message = f"Daily calories for {date} added to the MongoDB database."
            flash(success_message, 'success')  # Flash the success message
            return redirect(url_for('add_calories'))

    # Get the current date and format it
    current_date = datetime.now().strftime('%Y-%m-%d')

    return render_template('add_calories.html', current_date=current_date)

@app.route('/list_calories')
def list_calories():
    _, _, _, _ = get_mongo_connection()
    
    # Retrieve 'option' from the query string
    option = request.args.get('option', 'current_month')

    start_date = None
    end_date = None

    if option == 'current_month':
        start_date = get_start_of_month(datetime.now().year, datetime.now().month)
        end_date = get_end_of_month(datetime.now().year, datetime.now().month)

    if option == 'current_month':
        entries = current_user.calories_collection.find({'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lte': end_date.strftime('%Y-%m-%d')}}).sort('date')
    elif option == 'all_data':
        entries = current_user.calories_collection.find().sort('date')
    else:
        return "Invalid option"

    return render_template('list_calories.html', entries=entries, option=option, start_date=start_date, end_date=end_date)

@app.route('/download_csv')
@login_required
def download_csv():
    try:
        # Use current_user.calories_collection instead of collection
        entries_count = current_user.calories_collection.count_documents({})

        option = request.args.get('option', 'current_month')

        if option == 'current_month':
            # Get start and end dates for the current month
            current_date = datetime.now()
            start_date = get_start_of_month(current_date.year, current_date.month)
            end_date = get_end_of_month(current_date.year, current_date.month)

            entries = current_user.calories_collection.find({'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lte': end_date.strftime('%Y-%m-%d')}}).sort('date')
        elif option == 'all_data':
            # Get all data
            entries = current_user.calories_collection.find().sort('date')
        else:
            return "Invalid option"

        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)

        # Write CSV header
        csv_writer.writerow(['Date', 'Calories'])

        # Write CSV data
        for entry in entries:
            csv_writer.writerow([entry['date'], entry['total_calories']])

        response = Response(csv_data.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=calories_data.csv'

        return response
    except Exception as e:
        print("Error:", str(e))
        raise  # Re-raise the exception for Flask to handle and display in the browser

@app.route('/average_calories')
def average_calories():
    _, _, _, _ = get_mongo_connection()

    current_year = datetime.now().year
    current_month = datetime.now().month

    average_calories_month = calculate_average_calories(
        get_start_of_month(current_year, current_month),
        get_end_of_month(current_year, current_month),
        current_user.calories_collection
    )

    # Calculate average calories for the current year
    average_calories_year = calculate_average_calories(
        datetime(current_year, 1, 1),
        datetime(current_year, 12, 31),
        current_user.calories_collection
    )

    average_calories_year = calculate_average_calories(
        get_start_of_month(current_year, 1),  # Assuming 1 represents January
        get_end_of_month(current_year, 12),  # Assuming 12 represents December
        current_user.calories_collection
    )
    num_all_time_entries = current_user.calories_collection.count_documents({})
    total_all_time_calories = sum(entry['total_calories'] for entry in current_user.calories_collection.find())
    average_calories_all_time = total_all_time_calories / num_all_time_entries if num_all_time_entries > 0 else 0

    return render_template('average_calories.html',
                           average_calories_month=average_calories_month,
                           average_calories_year=average_calories_year,
                           average_calories_all_time=average_calories_all_time)

@app.route('/add_calorie_item', methods=['GET', 'POST'])
@login_required
def add_calorie_item():
    if request.method == 'POST':
        food_item = request.form['food_item']
        calorie_amount = float(request.form['calorie_amount'])

        if current_user.calories_collection is None:
            current_user.calories_collection = get_user_calories_collection(current_user.id)

        # Separate collection for calorie items
        calorie_items_collection = get_user_calorie_items_collection(current_user.id)

        existing_item = calorie_items_collection.find_one({'food_item': food_item})

        if existing_item:
            # Update the existing item
            calorie_items_collection.update_one({'food_item': food_item}, {'$set': {'calorie_amount': calorie_amount}})
            flash(f"Updated calorie amount for {food_item}.", 'success')
        else:
            # Add a new item with the food item as the custom name
            new_calorie_item = {'_id': food_item, 'food_item': food_item, 'calorie_amount': calorie_amount}
            calorie_items_collection.insert_one(new_calorie_item)
            flash(f"Added {food_item} to your calorie items.", 'success')

        return redirect(url_for('add_calorie_item'))

    return render_template('add_calorie_item.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        print(request.form)  # Print the form data

        email = request.form['email']
        password = request.form['password1']

        # Attempt to add the new user to the 'users' collection
        _, _, users_collection = get_mongo_connection(collection_name='users')  # Updated unpacking

        # Check if the email already exists
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            flash('Email already exists. Please choose a different email.', 'error')
        else:
            # Hash the password before storing
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # Store the new user in the 'users' collection
            user_data = {'email': email, 'password': hashed_password}
            users_collection.insert_one(user_data)
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('sign_up.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Retrieve the user from the users collection
        user = get_user_by_email(email)

        print(f"User: {user}")  # Add this line for debugging

        if user:
            # Add this line for debugging
            print(f"Password match: {check_password_hash(user.password, password)}")

            if check_password_hash(user.password, password):
                # Log in the user
                login_user(user)
                flash('Login successful.', 'success')
                return redirect(url_for('index'))
        
        # Add this line for debugging
        print("Login failed")

        flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/add_new_entry', methods=['GET', 'POST'])
@login_required
def add_new_entry():
    if request.method == 'POST':

        new_entry_data = {
            'date': request.form['new_entry_date'],
            'total_calories': int(request.form['new_entry_calories'])
        }
        current_user.calories_collection.insert_one(new_entry_data)

        flash('New entry added successfully.', 'success')
        return redirect(url_for('list_calories'))

    return render_template('add_new_entry.html')


@app.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    if request.method == 'POST':
        # Perform the double verification here
        password = request.form['password']

        if check_password_hash(current_user.password, password):
            # Password verification successful, proceed with user deletion

            # Check if the user is authenticated before accessing calories_collection
            if current_user.is_authenticated:
                user_id = current_user.id

                # Log out the user before deleting their account
                logout_user()

                _, _, users_collection = get_mongo_connection(collection_name='users')
                users_collection.delete_one({'_id': ObjectId(user_id)})

                # Check if calories_collection exists before trying to access it
                if hasattr(current_user, 'calories_collection'):
                    # Delete the user's calories collection
                    _, _, _, user_calories_collection = get_mongo_connection()
                    user_calories_collection_name = f'user_{user_id}_calories'
                    user_calories_collection = current_user.calories_collection
                    user_calories_collection.drop()

            flash('User account and related information successfully deleted. Log out.', 'success')
            return redirect(url_for('logout'))

        else:
            flash('Incorrect password. Deletion canceled.', 'error')
            return redirect(url_for('delete_user'))

    return render_template('delete_user.html')


@app.route('/confirm_delete_calories/<date>', methods=['POST'])
@login_required
def confirm_delete_calories(date):
    try:
        # Convert the date to a datetime object for consistency
        date_to_delete = datetime.strptime(date, '%Y-%m-%d')

        # Find the entry for the specified date and remove it
        result = current_user.calories_collection.delete_one({'date': date_to_delete.strftime('%Y-%m-%d')})

        if result.deleted_count == 1:
            flash(f'Data for {date_to_delete.strftime("%Y-%m-%d")} deleted successfully.', 'success')
        else:
            flash(f'No data found for {date_to_delete.strftime("%Y-%m-%d")}', 'error')

    except Exception as e:
        flash(str(e), 'error')

    return redirect(url_for('list_calories'))

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)