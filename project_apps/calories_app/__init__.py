from flask import Flask, render_template
from flask_login import LoginManager
from .models import User
from .database import get_mongo_connection, get_user_specific_collection
from bson import ObjectId
from .auth_routes import auth_bp
from .calorie_routes import calorie_bp
from .calorie_item_routes import calorie_item_bp
from .user_calorie_routes import user_calorie_bp

app = Flask(__name__)
app.secret_key = 'plius+-minus4816237mousymouse####'

login_manager = LoginManager(app)
login_manager.login_view = 'auth_bp.login' 

# Initialize MongoDB connection
client, db, _, _ = get_mongo_connection()

@app.route('/')
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    users_collection = db['users']
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})

    if user_data:
        user = User(str(user_data['_id']), user_data['email'], user_data.get('username', ''), user_data['password'])
        user.calories_collection = get_user_specific_collection(db, user.id, 'calories')
        return user

    return None

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(calorie_bp)
app.register_blueprint(calorie_item_bp)
app.register_blueprint(user_calorie_bp)