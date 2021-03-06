import os


class Config:
    TESTING = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'WjwyV26ZncUY8dW1IWBJSnMP00r'
    STORAGE = os.environ.get('STORAGE')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}/data.db'.format(
        os.environ.get('STORAGE'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    HASHIDS_ALPHABET = os.environ.get('HASHIDS_ALPHABET') or 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'  # noqa: E501
    HASHIDS_SALT = os.environ.get('HASHIDS_SALT') or '398742938645355498'
    HASHIDS_MIN_LEN = int(os.environ.get('HASHIDS_MIN_LEN') or 6)
    HUMANIZE_USE_UTC = True
    ANON_UID = int(os.environ.get('ANON_UID') or 4684191711925202)
