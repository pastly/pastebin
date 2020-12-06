from app import db, login
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.uid} ({self.id})>'
