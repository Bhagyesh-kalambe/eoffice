import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)


with app.app_context():

    username = "admin"
    password = "admin"

    full_name = "Main Officer"
    department = "all" #department name / all for admin 
    role = "admin"       #user/admin


    # Check duplicate
    if User.query.filter_by(username=username).first():
        print("Username already exists!")
        exit()


    hashed = bcrypt.generate_password_hash(password).decode()


    user = User(

        full_name=full_name,
        department=department,
        role=role,

        username=username,
        email=None,
        password=hashed
    )


    db.session.add(user)
    db.session.commit()

    print("User Created:", username)
