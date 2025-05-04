from website import create_app, db  # replace `yourapp` with your package name
from website.models import User     # adjust if models is elsewhere

app = create_app()

with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"Email: {user.email}, First Name: {user.first_name}, ID: {user.id}")



