from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

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
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.auth import bp as auth_bp  # noqa: E402
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from app.misc_routes import bp as misc_routes_bp  # noqa: E402
    app.register_blueprint(misc_routes_bp)
    from app.profile import bp as profile_bp  # noqa: E402
    app.register_blueprint(profile_bp, url_prefix='/profile')

    from app.auth import uid_str
    app.add_template_global(name='uid_str', f=uid_str)

    return app


# from app import routes  # noqa: W0611,E402
from app import models  # noqa: W0611,E402
