from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from .database import get_mongo_connection, get_user_calories_collection, get_user_calorie_items_collection
from datetime import datetime
from io import StringIO
import csv, math

# Blueprint for calorie tracking routes
calorie_item_bp = Blueprint('calorie_item_bp', __name__)

# MongoDB setup
client, db, _, _ = get_mongo_connection()


@calorie_item_bp.route('/add_calorie_item', methods=['GET', 'POST'])
@login_required
def add_calorie_item():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page

    calorie_items_collection = get_user_calorie_items_collection(current_user.id)

    if request.method == 'POST':
        food_item = request.form['food_item']
        calorie_amount = float(request.form['calorie_amount'])

        if current_user.calories_collection is None:
            current_user.calories_collection = get_user_calories_collection(current_user.id)

        existing_item = calorie_items_collection.find_one({'food_item': food_item})

        if existing_item:
            # Update the existing item
            calorie_items_collection.update_one({'food_item': food_item}, {'$set': {'calorie_amount': calorie_amount}})
            flash(f"Updated calorie amount for {food_item}.", 'success')
        else:
            # Add a new item
            new_calorie_item = {'food_item': food_item, 'calorie_amount': calorie_amount}
            calorie_items_collection.insert_one(new_calorie_item)
            flash(f"Added {food_item} to your calorie items.", 'success')

    total_items = calorie_items_collection.count_documents({})
    total_pages = math.ceil(total_items / per_page)
    user_calorie_items = calorie_items_collection.find({}).skip((page - 1) * per_page).limit(per_page)

    return render_template('add_calorie_item.html', 
                           user_calorie_items=user_calorie_items, 
                           total_pages=total_pages, 
                           current_page=page)

# @calorie_item_bp.route('/list_calorie_items')
# @login_required
# def list_calorie_items():
#     if current_user.calories_collection is None:
#         current_user.calories_collection = get_user_calories_collection(current_user.id)

#     # Collection for calorie items
#     calorie_items_collection = get_user_calorie_items_collection(current_user.id)
    
#     # Retrieve all calorie items
#     calorie_items = calorie_items_collection.find({})
    
#     return render_template('add_calorie_item.html', calorie_items=calorie_items)

@calorie_item_bp.route('/download_calorie_items_csv')
@login_required
def download_calorie_items_csv():
    calorie_items_collection = get_user_calorie_items_collection(current_user.id)
    calorie_items = calorie_items_collection.find()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Food Item', 'Calories per 100g'])  # CSV header

    for item in calorie_items:
        cw.writerow([item['food_item'], item['calorie_amount']])

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=calorie_items.csv"}
    )

@calorie_item_bp.route('/manage_calorie_items', methods=['GET', 'POST'])
@login_required
def manage_calorie_items():
    if request.method == 'POST':
        selected_item = request.form['selected_item']
        amount = float(request.form['amount'])

        if current_user.calories_collection is None:
            current_user.calories_collection = get_user_calories_collection(current_user.id)

        # Separate collection for calorie items
        calorie_items_collection = get_user_calorie_items_collection(current_user.id)

        selected_calorie_item = calorie_items_collection.find_one({'food_item': selected_item})

        if selected_calorie_item:
            # Add the selected calorie item and amount to the user's daily calories collection
            date = datetime.now().strftime('%Y-%m-%d')
            existing_entry = current_user.calories_collection.find_one({'date': date})

            if existing_entry:
                new_total_calories = existing_entry['total_calories'] + (selected_calorie_item['calorie_amount'] * amount)
                current_user.calories_collection.update_one({'date': date}, {'$set': {'total_calories': new_total_calories}})
                flash(f"Added {amount} servings of {selected_item} to the existing entry for {date}.", 'success')
            else:
                daily_data = {
                    'date': date,
                    'total_calories': selected_calorie_item['calorie_amount'] * amount
                }
                current_user.calories_collection.insert_one(daily_data)
                flash(f"Daily calories for {date} added to the MongoDB database.", 'success')

        return redirect(url_for('calorie_item_bp.manage_calorie_items'))
    
    # Fetch the user's calorie items for display
    calorie_items_collection = get_user_calorie_items_collection(current_user.id)
    user_calorie_items = list(calorie_items_collection.find())
    current_date = datetime.now()

    return render_template('manage_calorie_items.html', user_calorie_items=user_calorie_items, current_date=current_date)

@calorie_item_bp.route('/delete_calorie_item/<item_id>', methods=['POST'])
@login_required
def delete_calorie_item(item_id):
    # Logic to delete the item from the database
    # Assuming `calorie_items_collection` is your MongoDB collection
    calorie_items_collection = get_user_calorie_items_collection(current_user.id)
    calorie_items_collection.delete_one({'_id': item_id})

    flash('Calorie item deleted successfully.', 'success')
    return redirect(url_for('calorie_item_bp.add_calorie'))