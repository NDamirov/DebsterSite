from flask import Flask
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import Configuration
from flask_login import LoginManager


mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'auth.main'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Configuration)

    if not app.debug:
        from flask_sslify import SSLify
        # sslify = SSLify(app)

    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('favicon.ico')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .about import about as about_blueprint
    app.register_blueprint(about_blueprint, url_prefix='/about')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/authorize')

    from .profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint, url_prefix='/profile')

    from .vaults import vaults as vaults_blueprint
    app.register_blueprint(vaults_blueprint, url_prefix='/vaults')

    from .vault import vault as vault_blueprint
    app.register_blueprint(vault_blueprint, url_prefix='/vault')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
