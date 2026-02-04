import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from app import app, db, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)


with app.app_context():

    username = "admin1"   # CHANGE


    user = User.query.filter_by(username=username).first()

    if not user:
        print("User not found!")
        exit()


    # ===== CHANGE WHAT YOU WANT =====

    new_role = "user"        # admin / user / None
    new_department = "AYUSHMAN BHARAT"   # None if no change
    new_password = ""  # None if no change


    # ===============================


    if new_role:
        user.role = new_role

    if new_department:
        user.department = new_department

    if new_password:
        user.password = bcrypt.generate_password_hash(
            new_password
        ).decode()


    db.session.commit()

    print("Updated:", username)
