from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from .database import get_mongo_connection, get_user_calories_collection, get_user_calorie_items_collection
from .utils import get_start_of_month, get_end_of_month, calculate_average_calories
from datetime import datetime
from io import StringIO
import csv
from decimal import Decimal
from werkzeug.security import check_password_hash
from bson import ObjectId
from .auth_routes import logout_user

# Blueprint for calorie tracking routes
calorie_bp = Blueprint('calorie_bp', __name__)

# MongoDB setup
client, db, _, _ = get_mongo_connection()