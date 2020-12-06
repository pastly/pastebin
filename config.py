import os


class Config:
    TESTING = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'WjwyV26ZncUY8dW1IWBJSnMP00r'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
