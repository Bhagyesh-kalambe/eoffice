import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User

with app.app_context():

    users = User.query.all()

    print("\n--- ALL USERS ---\n")

    for u in users:

        print(f"""
ID        : {u.id}
Name      : {u.full_name}
Username  : {u.username}
Role      : {u.role}
Department: {u.department}
-------------------------
""")
