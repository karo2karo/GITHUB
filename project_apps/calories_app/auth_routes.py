from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User
from .database import get_mongo_connection, find_user_by_email, find_user_by_username, add_user
from bson import ObjectId

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

@auth_bp.route('/user_settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    if request.method == 'POST':
        _, _, _, users_collection = get_mongo_connection()
        action = request.form.get('action')

        if action == 'change_email':
            new_email = request.form.get('new_email')
            current_password = request.form.get('current_password_email')  # Assuming you add a password field for email verification

            if check_password_hash(current_user.password, current_password):
                result = users_collection.update_one({"_id": ObjectId(current_user.id)}, {"$set": {"email": new_email}})
                print("Update result:", result.matched_count, result.modified_count)

                if result.modified_count > 0:
                    flash('Email updated successfully.', 'success')
                else:
                    flash('No update made. Please try again with a different email.', 'info')
            else:
                flash('Current password is incorrect.', 'error')

        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_new_password = request.form.get('confirm_new_password')

            if new_password != confirm_new_password:
                flash('New passwords do not match.', 'error')
                return redirect(url_for('auth_bp.user_settings'))
            
            if check_password_hash(current_user.password, current_password):
                hashed_new_password = generate_password_hash(new_password)
                result = users_collection.update_one({"_id": ObjectId(current_user.id)}, {"$set": {"password": hashed_new_password}})

                if result.modified_count > 0:
                    flash('Password updated successfully.', 'success')
                else:
                    flash('Password update failed. Please try again.', 'error')
            else:
                flash('Current password is incorrect.', 'error')
        
        elif action == 'delete_account':
            password = request.form.get('delete_password')
            confirm_delete_password = request.form.get('confirm_delete_password')

            if password != confirm_delete_password:
                flash('Passwords do not match.', 'error')
                return redirect(url_for('auth_bp.user_settings'))
            
            if check_password_hash(current_user.password, password):
                user_id = current_user.id
                logout_user()

                users_collection.delete_one({'_id': ObjectId(user_id)})
                # Handle deletion of user-specific data, if any

                flash('User account and related information successfully deleted.', 'success')
                return redirect(url_for('auth_bp.login'))
            else:
                flash('Incorrect password. Deletion canceled.', 'error')

    return render_template('user_settings.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))