import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User


with app.app_context():

    username = "admin1"   # CHANGE THIS


    user = User.query.filter_by(username=username).first()

    if not user:
        print("User not found!")
        exit()


    db.session.delete(user)
    db.session.commit()

    print("Deleted:", username)
