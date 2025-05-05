import csv
import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from .models import User
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

@views.route('/terms')
@login_required
def terms():
    return render_template("terms.html", user=current_user)

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
        "English Exam G8": "https://drive.google.com/file/d/1URHcw0j6i_ImwyIC6tJ24i_oOt2-Wfmb/view?usp=sharing",
        "I.Sci Exam G8": "https://drive.google.com/file/d/1suZnpCrSp4hoGg8ojWAvOh9q2R3mXKTq/view?usp=sharing",
        "Math Exam G8": "https://drive.google.com/file/d/161s-cc2eFPKruG560Nlg7S9eHRHr4z_I/view?usp=sharing",
        "Pre-Technical Studies G8": "https://drive.google.com/file/d/1Y6kg4xL7tctSPLWFzQj_4r4TdHIU84ku/view?usp=sharing",
        "Social Studies Exam G8": "https://drive.google.com/file/d/1aYnAIH09fCnL3GCcHA-OGvXi7S15dVwA/view?usp=sharing",
        "Kiswahili Exam G8": "https://drive.google.com/file/d/1pRM_l_cCL2YvSWVb25hqMI3YrEaWNMim/view?usp=sharing",
        "Creativie Arts and Sports G8": "https://drive.google.com/file/d/1fk6ilwVmhyqzmzv-XsM5LDl7Q31K6_LH/view?usp=sharing",
        "C.R.E G8": "https://drive.google.com/file/d/18-IkL7xQsbX_5z4OGeDtT8LCJBGNMYCE/view?usp=sharing",
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

                # Send email
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
                        smtp.login('abeldena123@gmail.com', 'kxto ddfp tpoq tjtv')  # Use app password
                        smtp.send_message(msg)

                    flash("QR code sent to your email!", category='success')
                except Exception as e:
                    flash(f"Failed to send email: {e}", category='danger')

                # Log the request in a CSV file
                log_file = os.path.join('logs', 'qr_requests.csv')
                os.makedirs('logs', exist_ok=True)

                # Get the current timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Open the CSV file and append the log entry
                with open(log_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([user_email,current_user, selected_file, qr_name, timestamp, request.remote_addr, request.headers.get('User-Agent'),
])

            else:
                flash("Selected file not found.", category='danger')

    return render_template("generate_qr.html", user=current_user)
