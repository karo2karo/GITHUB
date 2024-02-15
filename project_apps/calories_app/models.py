from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, email, username, password):
        self.id = user_id
        self.email = email
        self.username = username
        self.password = password
        self.calories_collection = None