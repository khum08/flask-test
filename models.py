from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Document ,UserMixin):
    username = db.StringField()
    nickname = db.StringField()
    floder = db.StringField()
    password_hash = db.StringField()

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.save()
    
    def verify_password(self, password):
        print("password " + password)
        return check_password_hash(self.password_hash, password)