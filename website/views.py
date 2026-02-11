import csv
import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from website.models import User
import qrcode
import smtplib
from email.message import EmailMessage
from datetime import datetime
from datetime import datetime, timedelta  # Add timedelta here

views = Blueprint('views', __name__)




@views.route('/')
@login_required
def home():
    theme = session.get('theme', 'light')
    return render_template("home.html", user=current_user, theme=theme)

@views.route('/plan')
@login_required
def plan():
    return render_template('plan.html', User=current_user)

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        theme = request.form.get('theme')
        session['theme'] = theme
        flash(f"Theme set to {theme}", category='success')
        return redirect(url_for('views.settings'))

    theme = session.get('theme', 'light')
    return render_template("settings.html", user=current_user, theme=theme)


@views.route('/egoals', methods=['GET', 'POST'])
@login_required
def egoals():
    # Premium email list - consider moving this to database or config file
    premium_emails = [
        "abeldena123@gmail.com",
        "austinmvera@gmail.com",
        "taherhussein572@gmail.com",
        "malonepost725@gmail.com",
        "clivenezekiel@gmail.com"
    ]

    # Add session-based attempt tracking for security
    if 'egoals_attempts' not in session:
        session['egoals_attempts'] = 0
    
    # Check if user is locked out
    if session.get('egoals_locked_until'):
        lock_time = session['egoals_locked_until']
        if datetime.now() < lock_time:
            remaining = (lock_time - datetime.now()).seconds // 60
            flash(f"Too many failed attempts. Please try again in {remaining} minutes.", "danger")
            return render_template("egoals.html", user=current_user)
        else:
            # Reset if lock time has passed
            session.pop('egoals_locked_until', None)
            session['egoals_attempts'] = 0

    if request.method == 'POST':
        # Sanitize and validate input
        entered_email = request.form.get("email", "").strip().lower()
        
        # Basic validation
        if not entered_email:
            flash("Please enter an email address.", "danger")
            return render_template("egoals.html", user=current_user)
        
        # Simple email format validation
        if '@' not in entered_email or '.' not in entered_email:
            flash("Please enter a valid email address.", "danger")
            return render_template("egoals.html", user=current_user)
        
        # Check against premium list
        if entered_email in premium_emails:
            # Reset attempts on successful login
            session['egoals_attempts'] = 0
            session.pop('egoals_locked_until', None)
            
            # Get current user info for personalization
            user_name = current_user.first_name if current_user.first_name else "User"
            
            flash("Access granted! You now have access to premium goal tracking.", "success")
            
            # Send notification email with improved error handling
            try:
                msg = EmailMessage()
                msg['Subject'] = '🎯 Goals Access Granted - Start Achieving!'
                msg['From'] = 'Academic Redemption <abeldena123@gmail.com>'
                msg['To'] = entered_email
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Create HTML email with better formatting
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
                        .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin-top: 10px; }}
                        .features {{ margin: 20px 0; }}
                        .feature-item {{ background: white; padding: 10px; margin: 5px 0; border-left: 4px solid #4CAF50; }}
                        .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 0.9em; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🎯 Goals Access Activated!</h1>
                        </div>
                        <div class="content">
                            <p>Hello {user_name},</p>
                            <p>Great news! Your access to our premium goal-setting features has been activated.</p>
                            
                            <p><strong>Access Details:</strong></p>
                            <ul>
                                <li>Email: {entered_email}</li>
                                <li>Access Time: {now}</li>
                                <li>Status: <span style="color: #4CAF50;">ACTIVE</span></li>
                            </ul>
                            
                            <div class="features">
                                <p><strong>What you can now do:</strong></p>
                                <div class="feature-item">✅ Set and track academic goals</div>
                                <div class="feature-item">✅ Create custom deadlines</div>
                                <div class="feature-item">✅ Receive progress notifications</div>
                                <div class="feature-item">✅ Access goal analytics</div>
                            </div>
                            
                            <p>Start turning your academic dreams into reality today!</p>
                            
                            <p>
                                <a href="{url_for('views.unlocked_goals', _external=True)}" 
                                   style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                   🚀 Start Setting Goals
                                </a>
                            </p>
                        </div>
                        <div class="footer">
                            <p>Best regards,<br>
                            <strong>The Academic Redemption Team</strong></p>
                            <p><small>This is an automated message. Please do not reply to this email.</small></p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # Plain text version for email clients that don't support HTML
                text_content = f"""Hello {user_name},

🎉 Great news! Your access to our premium goal-setting features has been activated.

Access Details:
• Email: {entered_email}
• Access Time: {now}
• Status: ACTIVE

What you can now do:
✅ Set and track academic goals
✅ Create custom deadlines
✅ Receive progress notifications
✅ Access goal analytics

Start making your goals a reality with our premium features!

Start here: {url_for('views.unlocked_goals', _external=True)}

Cheers to new achievements,
The Academic Redemption Team ✨

---
This is an automated message. Please do not reply to this email.
"""

                # Set both HTML and plain text content
                msg.set_content(text_content)
                msg.add_alternative(html_content, subtype='html')
                
                # Send email with timeout
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as smtp:
                    smtp.login('abeldena123@gmail.com', 'wphv ckth viop jmtx ')
                    smtp.send_message(msg)
                    
                # Log successful email send
                print(f"Goals access email sent to: {entered_email} at {now}")
                
            except smtplib.SMTPAuthenticationError:
                flash("Access granted! Welcome email could not be sent due to server configuration.", "warning")
                print("SMTP Authentication Error - Check email credentials")
            except smtplib.SMTPException as e:
                flash("Access granted! Welcome email could not be sent.", "warning")
                print(f"SMTP Error: {e}")
            except Exception as e:
                flash("Access granted! There was an issue sending the welcome email.", "warning")
                print(f"Email sending error: {e}")
            
            # Log the access (consider adding to database)
            print(f"Goals access granted to: {entered_email} at {datetime.now()}")
            
            return redirect(url_for('views.unlocked_goals'))
        
        else:
            # Increment failed attempts
            session['egoals_attempts'] = session.get('egoals_attempts', 0) + 1
            attempts_made = session['egoals_attempts']
            
            # Implement temporary lockout after 3 failed attempts
            if attempts_made >= 3:
                # Lock for 15 minutes
                lock_until = datetime.now() + timedelta(minutes=15)
                session['egoals_locked_until'] = lock_until
                flash("Too many failed attempts. Access locked for 15 minutes.", "danger")
            else:
                attempts_left = 3 - attempts_made
                flash(f"Access denied. Invalid email. {attempts_left} attempts remaining.", "danger")
            
            # Log failed attempt (consider adding to database)
            print(f"Failed egoals access attempt: {entered_email} at {datetime.now()}")
            
            return render_template("egoals.html", user=current_user)
    
    # For GET request, show the form
    return render_template("egoals.html", user=current_user)


@views.route('/unlocked_goals')
@login_required
def unlocked_goals():
    return render_template("unlocked_goals.html", user=current_user)

@views.route('/premium', methods=['GET', 'POST'])
@login_required
def premium():
    allowed_codes = ["qwerty", "1234", "1379K", "2468", "2025"]
    allowed_emails = ["abeldena123@gmail.com", "austinmvera@gmail.com", 
                     "alpcustomercare1@gmail.com", "clivenezekiel@gmail.com", 
                     "taherhussein572@gmail.com", "simplyaep5@gmail.com", 
                     "malonepost725@gmail.com"]

    if request.method == "POST":
        entered_code = request.form.get("code", "").strip()
        entered_email = request.form.get("email", "").strip().lower()
        
        # Enhanced validation
        if not entered_email or not entered_code:
            flash("Both email and access code are required.", "danger")
            return render_template("premium.html", user=current_user)
        
        # Rate limiting simulation (you should implement proper rate limiting)
        session.setdefault('premium_attempts', 0)
        session['premium_attempts'] += 1
        
        if session.get('premium_attempts', 0) > 5:
            flash("Too many attempts. Please try again later.", "danger")
            return render_template("premium.html", user=current_user)
        
        # Validate credentials
        if entered_email in allowed_emails and entered_code in allowed_codes:
            # Reset attempts on success
            session['premium_attempts'] = 0
            
            # Log successful access
            print(f"Premium access granted to: {entered_email}")
            
            flash("Access granted! You now have premium access.", "success")

            # Send notification email
            try:
                msg = EmailMessage()
                msg['Subject'] = '🎉 Premium Access Activated'
                msg['From'] = 'redemptioncustomercare@gmail.com'
                msg['To'] = entered_email
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                msg.set_content(f"""Hello Premium User!

Congratulations! Your premium access has been successfully activated.

📊 Access Details:
• Activated on: {now}
• Features unlocked: All premium content
• Account: {entered_email}

You now have access to:
✅ Free downloadable Exams & Notes
✅ Study Blueprints
✅ Advanced Analytics
✅ Priority Support

Start exploring your premium features now!

Best regards,
The Academic Redemption Team
""")
                
                msg.add_alternative(f"""\
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .feature {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Premium Access Activated!</h1>
        </div>
        <div class="content">
            <p>Hello Premium User!</p>
            <p>Your premium access has been successfully activated on <strong>{now}</strong>.</p>
            
            <h3>🎯 What's Now Available:</h3>
            <div class="feature">✅ Free downloadable Exams & Notes</div>
            <div class="feature">✅ Study Blueprints & Strategies</div>
            <div class="feature">✅ Advanced Progress Analytics</div>
            <div class="feature">✅ Priority 24/7 Support</div>
            
            <p>Start exploring your premium features and take your academic journey to the next level!</p>
            
            <p>Best regards,<br>
            <strong>The Academic Redemption Team</strong></p>
        </div>
    </div>
</body>
</html>
""", subtype='html')

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login('abeldena123@gmail.com', 'wphv ckth viop jmtx ')
                    smtp.send_message(msg)
                    
                flash("Welcome email sent to your inbox!", "success")
                
            except Exception as e:
                print(f"Email sending failed: {e}")
                flash("Premium access granted, but welcome email failed to send.", "warning")

            return redirect(url_for('views.unlocked_premium'))
        else:
            attempts_left = 5 - session.get('premium_attempts', 0)
            if attempts_left > 0:
                flash(f"Invalid credentials. {attempts_left} attempts remaining.", "danger")
            else:
                flash("Too many failed attempts. Access temporarily locked.", "danger")
            
            return render_template("premium.html", user=current_user)
    
    return render_template("premium.html", user=current_user)


@views.route('/unlocked_premium')
def unlocked_premium():
    return render_template("unlocked_premium.html", user=current_user)

@views.route('/terms')
@login_required
def terms():
    return render_template("terms.html", user=current_user)
from flask_mail import Mail, Message

# Initialize Flask-Mail
mail = Mail()


@views.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        grade = request.form['grade']
        subject = request.form.get('subject', 'N/A')
        feedback_text = request.form['feedback']

        email_body = f"""
        🎓 Grade: {grade}
        📘 Subject: {subject}
        💬 Feedback:
        {feedback_text}
        """

        msg = Message(
            subject="📥 New Feedback Received",
            sender='abeldena123@gmail.com',
            recipients=['abeldena123@gmail.com'],
            body=email_body
        )

        mail.send(msg)  # ✅ Use Flask-Mail's send function instead of smtplib

        flash("✅ Thanks! Your feedback has been sent.", "success")
        return redirect(url_for('views.feedback'))

    return render_template('feedback.html')

@views.route('/about')
@login_required
def about():
    return render_template("about.html", user=current_user)

@views.route('/acknowledgments')
@login_required
def acknowledgments():
    return render_template("acknowledgments.html", user=current_user)

@views.route('/generate_qr', methods=['GET', 'POST'])
@login_required
def generate_qr():
    file_links = {
        "Academic Redemption Guide": "https://drive.google.com/file/d/107QaGGRn47HPa_6REe59R_n-oh5vveG7/view?usp=sharing",
        "English G9": "https://drive.google.com/file/d/1ismEoxPPJGA4NPPV-FFedjtEu5EVHrov/view?usp=sharing",
        "Math G9": "https://drive.google.com/file/d/1DAMaQNYJ_MzL7bSJ5GObJsrg8BLrRjcS/view?usp=sharing",
        "I.Sci G9": "https://drive.google.com/file/d/154cIUSMtU-63zbJts2_4fSB_QIzhywKA/view?usp=sharing",
        "Agriculture PP1 G9": "https://drive.google.com/file/d/1TX85rHtK30MKeueeyIWdWl1SNjepkNZz/view?usp=sharing",
        "C.R.E G9": "https://drive.google.com/file/d/1r7cGozpR4bsb6vLu0I03l7zxCpvoFn4-/view?usp=sharing",
        "CAS G9": "https://drive.google.com/file/d/1GcFWY3mPB8w2WjvMBxXRuFdaqbsGBIA8/view?usp=sharing",
        "Kiswahili PP1 G9": "https://drive.google.com/file/d/1kyUwHcrY-KNYo6i3TvH8aA8IxRMxi2lW/view?usp=sharing",
        "Social Studies G9": "https://drive.google.com/file/d/1aYnAIH09fCnL3GCcHA-OGvXi7S15dVwA/view?usp=sharing",
        "English Exam G8": "https://drive.google.com/file/d/1URHcw0j6i_ImwyIC6tJ24i_oOt2-Wfmb/view?usp=sharing",
        "I.Sci Exam G8": "https://drive.google.com/file/d/1suZnpCrSp4hoGg8ojWAvOh9q2R3mXKTq/view?usp=sharing",
        "Math Exam G8": "https://drive.google.com/file/d/161s-cc2eFPKruG560Nlg7S9eHRHr4z_I/view?usp=sharing",
        "Pre-Technical Studies G8": "https://drive.google.com/file/d/1Y6kg4xL7tctSPLWFzQj_4r4TdHIU84ku/view?usp=sharing",
        "Social Studies Exam G8": "https://drive.google.com/file/d/1aYnAIH09fCnL3GCcHA-OGvXi7S15dVwA/view?usp=sharing",
        "Kiswahili Exam G8": "https://drive.google.com/file/d/1pRM_l_cCL2YvSWVb25hqMI3YrEaWNMim/view?usp=sharing",
        "Creativie Arts and Sports G8": "https://drive.google.com/file/d/1fk6ilwVmhyqzmzv-XsM5LDl7Q31K6_LH/view?usp=sharing",
        "C.R.E G8": "https://drive.google.com/file/d/18-IkL7xQsbX_5z4OGeDtT8LCJBGNMYCE/view?usp=sharing"
    }

    if request.method == 'POST':
        selected_file = request.form.get('file_choice')
        qr_name = request.form.get('qr_name')
        user_email = request.form.get('email')

        if selected_file and qr_name and user_email:
            pdf_link = file_links.get(selected_file)
            if pdf_link:
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(pdf_link)
                qr.make(fit=True)
                img = qr.make_image(fill='black', back_color='white')

                folder = os.path.join('static', 'qr_codes')
                os.makedirs(folder, exist_ok=True)
                filename = f"{qr_name}.png"
                filepath = os.path.join(folder, filename)
                img.save(filepath)

                try:
                    msg = EmailMessage()
                    msg['Subject'] = 'Your Requested QR Code'
                    msg['From'] = 'abeldena123@gmail.com'
                    msg['To'] = user_email
                    msg.set_content(f"Here is your QR code for {selected_file}.")

                    with open(filepath, 'rb') as f:
                        file_data = f.read()
                        msg.add_attachment(file_data, maintype='image', subtype='png', filename=filename)

                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login('abeldena123@gmail.com', 'wphv ckth viop jmtx ')
                        smtp.send_message(msg)

                    flash("QR code sent to your email!", category='success')
                except Exception as e:
                    flash(f"Failed to send email: {e}", category='danger')

                log_file = os.path.join('logs', 'qr_requests.csv')
                os.makedirs('logs', exist_ok=True)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with open(log_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([user_email,current_user, selected_file, qr_name, timestamp, request.remote_addr, request.headers.get('User-Agent')])
            else:
                flash("Selected file not found.", category='danger')

    return render_template("generate_qr.html", user=current_user)
