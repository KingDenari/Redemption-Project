from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('views.home'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Basic validation
        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template("login.html")
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Verify password
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash(f'Welcome back, {user.first_name}!', 'success')
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password. Please try again.', 'danger')
        else:
            flash('No account found with that email. Please sign up first.', 'danger')
    
    return render_template("login.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # Redirect if already logged in
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('views.home'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        first_name = request.form.get('firstName', '').strip()
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')
        
        # Validate inputs
        errors = []
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            errors.append('An account with this email already exists.')
        
        # Email validation
        if not email or '@' not in email or '.' not in email:
            errors.append('Please enter a valid email address.')
        elif len(email) < 5:
            errors.append('Email is too short.')
        
        # Name validation
        if not first_name:
            errors.append('First name is required.')
        elif len(first_name) < 2:
            errors.append('First name must be at least 2 characters.')
        elif len(first_name) > 50:
            errors.append('First name is too long.')
        
        # Password validation
        if not password1 or not password2:
            errors.append('Both password fields are required.')
        elif password1 != password2:
            errors.append('Passwords do not match.')
        elif len(password1) < 8:
            errors.append('Password must be at least 8 characters long.')
        elif not any(char.isdigit() for char in password1):
            errors.append('Password must contain at least one number.')
        elif not any(char.isalpha() for char in password1):
            errors.append('Password must contain at least one letter.')
        
        # If there are errors, show them and return
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template("sign_up.html")
        
        # Create new user
        try:
            new_user = User(
                email=email,
                first_name=first_name,
                password=generate_password_hash(password1, method='sha256')
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Try to send welcome email
            try:
                msg = Message(
                    subject='Welcome to Academic Redemption!',
                    sender=current_app.config['MAIL_USERNAME'],
                    recipients=[email],
                    body=f"""Hello {first_name},

Welcome to Academic Redemption! Your account has been successfully created.

We're excited to help you on your journey to academic success. Log in to start setting goals and tracking your progress.

Best regards,
The Redemption Team
"""
                )
                mail.send(msg)
                flash('Welcome email sent! Check your inbox.', 'success')
            except Exception as e:
                print(f"Email sending failed: {e}")
                # Don't fail the signup if email fails
                pass
            
            # Log the user in
            login_user(new_user, remember=True)
            
            flash(f'Account created successfully! Welcome, {first_name}!', 'success')
            return redirect(url_for('views.home'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {e}")
            flash('An error occurred while creating your account. Please try again.', 'danger')
            return render_template("sign_up.html")
    
    return render_template("sign_up.html")
