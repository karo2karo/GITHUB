from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from .models import User
from .database import get_mongo_connection, find_user_by_email, find_user_by_username, add_user

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form['login_id']
        password = request.form['password']
        _, db, _, _ = get_mongo_connection()
        users_collection = db['users']

        if "@" in login_id:
            user_document = find_user_by_email(users_collection, login_id)
        else:
            user_document = find_user_by_username(users_collection, login_id)

        if user_document and check_password_hash(user_document['password'], password):
            user = User(str(user_document['_id']), user_document['email'], user_document.get('username', ''), user_document['password'])
            login_user(user)
            flash('Login successful.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid login credentials.', 'error')

    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if password1 != password2:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('auth_bp.signup'))

        _, db, _, _ = get_mongo_connection()
        users_collection = db['users']

        user_added = add_user(users_collection, email, username, password1)
        if user_added:
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('auth_bp.login'))
        else:
            flash('Email or Username already exists. Please choose a different email or username.', 'error')
            return redirect(url_for('auth_bp.signup'))

    return render_template('sign_up.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))