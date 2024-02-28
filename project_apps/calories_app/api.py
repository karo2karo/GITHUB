from flask import Flask, render_template, request, Blueprint
from flask_login import login_required
import requests

app = Flask(__name__)
api_bp = Blueprint('api', __name__)

def get_food_nutrients(fdc_id, api_key):
    details_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
    params = {"api_key": api_key}
    response = requests.get(details_url, params=params)
    food_details = response.json()
    
    nutrients_info = {}
    for nutrient in food_details.get('foodNutrients', []):
        if nutrient['nutrient']['name'] == 'Energy':
            nutrients_info['calories'] = nutrient['amount']
            break
    return nutrients_info

def get_calories_for_vegetable(food_item_name, api_key):
    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": food_item_name,
        "pageSize": 5,
        "api_key": api_key,
    }
    response = requests.get(search_url, params=params)
    response_data = response.json()
    
    calories_list = []
    if response_data and "foods" in response_data:
        for food in response_data['foods']:
            fdc_id = food.get('fdcId')
            food_data = get_food_nutrients(fdc_id, api_key)
            calories_list.append({
                "description": food.get('description'),
                "fdcId": fdc_id,
                "calories": food_data.get('calories', 'Not available')
            })
    return calories_list

@api_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        food_item_name = request.form.get('foodItem')
        api_key = 'KMLplo6EsMcCqJthOAUBzBvkFkllDcf1yD8p97Fj'
        calories_data = get_calories_for_vegetable(food_item_name, api_key)
    else:
        calories_data = []
        food_item_name = ''
    return render_template('food_results.html', calories_data=calories_data, query=food_item_name)