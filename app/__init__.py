from flask import Flask
from config import Config
from hashids import Hashids
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_humanize import Humanize
import os

# Flask extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
# For pages that require the user to login, send them to the login page (where
# the string 'login' is what is used in url_for(...) to get the URL)
login.login_view = 'auth.login'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(app.config['STORAGE'], exist_ok=True)
    db.init_app(app)
    humanize = Humanize(app)
    migrate.init_app(app, db)
    login.init_app(app)
    app.hashids = Hashids(
        alphabet=app.config['HASHIDS_ALPHABET'],
        min_length=app.config['HASHIDS_MIN_LEN'],
        salt=app.config['HASHIDS_SALT'])

    from app.auth import bp as auth_bp  # noqa: E402
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from app.misc_routes import bp as misc_routes_bp  # noqa: E402
    app.register_blueprint(misc_routes_bp)
    from app.profile import bp as profile_bp  # noqa: E402
    app.register_blueprint(profile_bp, url_prefix='/profile')
    from app.file import bp as file_bp  # noqa: E402
    app.register_blueprint(file_bp, url_prefix='/file')

    from app.auth import uid_str
    app.add_template_global(name='uid_str', f=uid_str)
    app.add_template_global(name='humanize', f=humanize)
    app.add_template_global(name='hashids_encode', f=app.hashids.encode)

    return app


# from app import routes  # noqa: W0611,E402
from app import models  # noqa: W0611,E402
