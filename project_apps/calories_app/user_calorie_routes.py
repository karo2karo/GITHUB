from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from .database import get_mongo_connection, get_user_calories_collection
from .utils import get_start_of_month, get_end_of_month, calculate_average_calories
from datetime import datetime
from io import StringIO
import csv, math
from decimal import Decimal
from werkzeug.security import check_password_hash
from bson import ObjectId
from .auth_routes import logout_user
from pymongo import ASCENDING

# Blueprint for calorie tracking routes
user_calorie_bp = Blueprint('user_calorie_bp', __name__)

# MongoDB setup
client, db, _, _ = get_mongo_connection()


@user_calorie_bp.route('/add_calories', methods=['GET', 'POST'])
@login_required
def add_calories():
    current_date = datetime.now()

    if request.method == 'POST':
        _, _, _, users_collection = get_mongo_connection()

        calories_str = request.form['calories']
        date_str = request.form['date']

        try:
            calories = float(calories_str)
        except ValueError:
            error_message = "Invalid input for calories. Please enter a valid number."
            return render_template('add_calories.html', error_message=error_message, current_date=current_date)

        try:
            # Convert the date to a datetime object for consistency
            date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')

        except ValueError:
            error_message = "Invalid input for date. Please enter a valid date in the format YYYY-MM-DD."
            return render_template('add_calories.html', error_message=error_message, current_date=current_date)

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
            return redirect(url_for('user_calorie_bp.add_calories'))
        else:
            daily_data = {
                'date': date,
                'total_calories': calories
            }
            user_calories_collection.insert_one(daily_data)
            success_message = f"Daily calories for {date} added to the MongoDB database."
            flash(success_message, 'success')  # Flash the success message
            return redirect(url_for('user_calorie_bp.add_calories'))

    current_date = datetime.now()

    return render_template('add_calories.html', current_date=current_date)

@user_calorie_bp.route('/list_calories')
@login_required
def list_calories():
    _, _, _, _ = get_mongo_connection()
    option = request.args.get('option', 'current_month')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of records per page

    # Initialize variables
    entries = None
    start_date = None
    end_date = None
    average_data = None

    try:
        if option == 'current_month':
            start_date = get_start_of_month(datetime.now().year, datetime.now().month)
            end_date = get_end_of_month(datetime.now().year, datetime.now().month)
            entries = current_user.calories_collection.find(
                {'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lte': end_date.strftime('%Y-%m-%d')}}
            ).sort('date').skip((page - 1) * per_page).limit(per_page)

        elif option == 'all_data':
            entries = current_user.calories_collection.find().sort('date').skip((page - 1) * per_page).limit(per_page)

        elif option == 'averages':
            start_of_month = get_start_of_month(datetime.now().year, datetime.now().month)
            end_of_month = get_end_of_month(datetime.now().year, datetime.now().month)
            average_calories_month = calculate_average_calories(start_of_month, end_of_month, current_user.calories_collection)

            start_of_year = get_start_of_month(datetime.now().year, 1)
            end_of_year = get_end_of_month(datetime.now().year, 12)
            average_calories_year = calculate_average_calories(start_of_year, end_of_year, current_user.calories_collection)

            num_all_time_entries = current_user.calories_collection.count_documents({})
            total_all_time_calories = sum(entry['total_calories'] for entry in current_user.calories_collection.find())
            average_calories_all_time = total_all_time_calories / num_all_time_entries if num_all_time_entries > 0 else 0

            average_data = {
                'average_calories_month': average_calories_month,
                'average_calories_year': average_calories_year,
                'average_calories_all_time': average_calories_all_time
            }

        else:
            flash("Invalid option selected.", "error")
            return redirect(url_for('user_calorie_bp.list_calories'))

        # Calculate the total number of pages
        total_entries = current_user.calories_collection.count_documents({})
        total_pages = math.ceil(total_entries / per_page)

    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for('user_calorie_bp.list_calories'))

    # Render the template with all necessary data
    return render_template('list_calories.html', entries=entries, option=option,
                           start_date=start_date, end_date=end_date, average_data=average_data,
                           page=page, total_pages=total_pages)

@user_calorie_bp.route('/download_csv')
@login_required
def download_csv():
    try:
        option = request.args.get('option', 'current_month')

        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)

        if option == 'current_month':
            current_date = datetime.now()
            start_date = get_start_of_month(current_date.year, current_date.month)
            end_date = get_end_of_month(current_date.year, current_date.month)
            entries = current_user.calories_collection.find({'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lte': end_date.strftime('%Y-%m-%d')}}).sort('date')
            csv_writer.writerow(['Date', 'Calories'])
            for entry in entries:
                csv_writer.writerow([entry['date'], entry['total_calories']])

        elif option == 'all_data':
            entries = current_user.calories_collection.find().sort('date')
            csv_writer.writerow(['Date', 'Calories'])
            for entry in entries:
                csv_writer.writerow([entry['date'], entry['total_calories']])

        elif option == 'averages':
            # Logic to handle averages
            csv_writer.writerow(['Period', 'Average Calories'])

            # Calculate average calories for the current month
            start_of_month = get_start_of_month(datetime.now().year, datetime.now().month)
            end_of_month = get_end_of_month(datetime.now().year, datetime.now().month)
            average_calories_month = calculate_average_calories(start_of_month, end_of_month, current_user.calories_collection)

            # Calculate average calories for the current year
            start_of_year = get_start_of_month(datetime.now().year, 1)
            end_of_year = get_end_of_month(datetime.now().year, 12)
            average_calories_year = calculate_average_calories(start_of_year, end_of_year, current_user.calories_collection)

            # Calculate average calories for all time
            num_all_time_entries = current_user.calories_collection.count_documents({})
            total_all_time_calories = sum(entry['total_calories'] for entry in current_user.calories_collection.find())
            average_calories_all_time = total_all_time_calories / num_all_time_entries if num_all_time_entries > 0 else 0

            # Format the averages to two decimal places
            average_calories_month = Decimal(average_calories_month).quantize(Decimal('0.00'))
            average_calories_year = Decimal(average_calories_year).quantize(Decimal('0.00'))
            average_calories_all_time = Decimal(average_calories_all_time).quantize(Decimal('0.00'))

            # Write averages to CSV
            csv_writer.writerow(['Current Month', average_calories_month])
            csv_writer.writerow(['Current Year', average_calories_year])
            csv_writer.writerow(['All Time', average_calories_all_time])

        else:
            return "Invalid option"

        response = Response(csv_data.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=calories_data.csv'
        return response

    except Exception as e:
        print("Error:", str(e))
        raise

@user_calorie_bp.route('/delete_user', methods=['GET', 'POST'])
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
            return redirect(url_for('auth_bp.logout'))

        else:
            flash('Incorrect password. Deletion canceled.', 'error')
            return redirect(url_for('delete_user'))

    return render_template('delete_user.html')

@user_calorie_bp.route('/confirm_delete_calories/<date>', methods=['POST'])
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

    return redirect(url_for('user_calorie_bp.list_calories'))

@user_calorie_bp.route('/your_route')
@login_required
def your_route():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Set the number of items per page

    # Assuming `calories_collection` is your MongoDB collection
    total_entries = current_user.calories_collection.count_documents({})
    entries = current_user.calories_collection.find()\
             .sort('date', ASCENDING)\
             .skip((page - 1) * per_page)\
             .limit(per_page)

    total_pages = total_entries // per_page + (total_entries % per_page > 0)
    
    return render_template('your_template.html', entries=entries, page=page, total_pages=total_pages)