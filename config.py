import os


class Config:
    TESTING = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'WjwyV26ZncUY8dW1IWBJSnMP00r'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    HASHIDS_ALPHABET = os.environ.get('HASHIDS_ALPHABET') or 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'  # noqa: E501
    HASHIDS_SALT = os.environ.get('HASHIDS_SALT') or '398742938645355498'
    HASHIDS_MIN_LEN = int(os.environ.get('HASHIDS_MIN_LEN') or 6)
    # Doesn't seem to actually do anything. Bug?
    # HUMANIZE_USE_UTC = True
