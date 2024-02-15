from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash

# MongoDB Connection Function
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

def get_collection(database, collection_name):
    collection = database[collection_name]
    if collection_name in ['daily_calories', 'user_calories']:
        collection.create_index([('date', ASCENDING)], unique=True)
    return collection

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

def get_user_specific_collection(db, user_id, collection_type):
    collection_name = f'user_{user_id}_{collection_type}'
    return get_collection(db, collection_name)

def add_user(users_collection, email, username, password):
    existing_user_email = users_collection.find_one({'email': email})
    existing_user_username = users_collection.find_one({'username': username})

    if existing_user_email or existing_user_username:
        return False 

    try:
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user_data = {'email': email, 'username': username, 'password': hashed_password}
        users_collection.insert_one(user_data)
        return True
    except DuplicateKeyError:
        return False

# Function to find a user by email or username
def find_user_by_email(users_collection, email):
    return users_collection.find_one({'email': email})

def find_user_by_username(users_collection, username):
    return users_collection.find_one({'username': username})