import csv
import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from website.models import User
import qrcode
import smtplib
from email.message import EmailMessage
from datetime import datetime

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
    premium_emails= ["abeldena123@gmail.com", "austinmvera@gmail.com"]

    if request.method == 'POST':
        entered_email2 = request.form.get("email")

        if entered_email2 in premium_emails:
            flash("Access granted! You now have access.", category="success")
            
            try:
                msg = EmailMessage()
                msg['Subject'] = '🚀 Your Goals Await – Time to Make Magic Happen!'
                msg['From'] = 'redemptioncutomercare1@gmail.com'
                msg['To'] = entered_email2
                now2= datetime.now().strftime('%Y-%m-%d %H:%M')
                msg.set_content(
                    f"Hello User!,\n\n🎉 Now, it’s time to turn your dreams into reality with our premium goal-setting features.\nStart making your goals a reality with our premium features.\nNew sign in on {now2}\n\nCheers to new achievements, The Redemption Team ✨")
                

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login('redemptioncustomercare1@gmail.com', 'gufo zvxi fnvn dnyq')
                    smtp.send_message(msg)
            except Exception as e:
                flash(f"Notification email failed: {e}", category="danger")

            return redirect(url_for('views.unlocked_goals'))
        
        else:
            flash("Access denied. Invalid email.", category="danger")


    return render_template("egoals.html", user=current_user)


@views.route('/unlocked_goals')
@login_required
def unlocked_goals():
    return render_template("unlocked_goals.html", user=current_user)

@views.route('/premium', methods=['GET', 'POST'])
@login_required
def premium():
    allowed_code = ["qwerty", "1234", "1379K", "2468"]  # just a string, not a list
    allowed_emails = ["abeldena123@gmail.com", "austinmvera@gmail.com", "alpcustomercare1@gmail.com", "kingsukuna922@gmail.com", "simplyaep5@gmail.com"]

    if request.method == "POST":
        entered_code = request.form.get("code")
        entered_email = request.form.get("email")

        if entered_code in allowed_code and entered_email in allowed_emails:
            flash("Access granted! You now have premium access.", category="success")

            # Send notification email
            try:
                msg = EmailMessage()
                msg['Subject'] = 'New Premium Sign In'
                msg['From'] = 'redemptioncustomercare@gmail.com'
                msg['To'] = entered_email
                now = datetime.now().strftime('%Y-%m-%d %H:%M')
                msg.set_content(
                    f"Hello Premium User!,\n\nYou are now eligible for free downloadable Exams, Notes, and Blueprints.\n\nNew Premium sign in on {now}"
                )

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login('redemptioncustomercare1@gmail.com', 'gufo zvxi fnvn dnyq')
                    smtp.send_message(msg)
            except Exception as e:
                flash(f"Notification email failed: {e}", category="danger")

            return redirect(url_for('views.unlocked_premium'))
        else:
            flash("Access denied. Invalid code or email.", category="danger")

    return render_template("premium.html", user=current_user)


@views.route('/unlocked_premium')
@login_required
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
@login_required
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
            sender='redemptioncustomercare1@gmail.com',
            recipients=['redemptioncustomercare1@gmail.com'],
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
                    msg['From'] = 'redemptioncustomercare1@gmail.com'
                    msg['To'] = user_email
                    msg.set_content(f"Here is your QR code for {selected_file}.")

                    with open(filepath, 'rb') as f:
                        file_data = f.read()
                        msg.add_attachment(file_data, maintype='image', subtype='png', filename=filename)

                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login('redemptioncustomercare1@gmail.com', 'gufo zvxi fnvn dnyq')
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
