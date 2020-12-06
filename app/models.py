from app import db, login
from flask_login import UserMixin
# https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime
# https://docs.sqlalchemy.org/en/13/core/compiler.html#utc-timestamp-function
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime, TypeDecorator


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(utcnow, 'sqlite')
def sqlite_utcnow(element, compiler, **kw):
    return 'CURRENT_TIMESTAMP'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.uid} ({self.id})>'


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return f'<File {self.hash} ({self.id})>'


class UserFile(db.Model):
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    file_id = db.Column(db.ForeignKey('file.id'), nullable=False)
    fname = db.Column(db.String(128), nullable=False)
    ts = db.Column(db.DateTime, server_default=utcnow(), nullable=False)
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'file_id'),
    )
