from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask.cli import with_appcontext
import click
import os
import datetime
from user_agents import parse

# Database initialization
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    session_id = db.Column(db.String(200), unique=True, nullable=False)

    def get_id(self):
        return self.id

class VisitorStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    browser = db.Column(db.String(50), nullable=False)
    device = db.Column(db.String(50), nullable=False)
    operating_system = db.Column(db.String(50), nullable=False)
    is_bot = db.Column(db.Boolean, nullable=False)

# Blueprints
from app.views.auth import auth
from app.views.home import home
from app.views.admin import admin
from app.views.settings import settings_bp

# Commands
@click.command(name='create_admin_user')
@with_appcontext
def create_admin_user():
    admin_user = User(
        name='admin',
        email='admin@example.com',
        password=generate_password_hash('admin', method='sha256'),
        session_id=generate_id('admin', 'admin@example.com', generate_password_hash('admin', method='sha256'))
    )
    db.session.add(admin_user)
    db.session.commit()
    click.echo('Admin user created.')

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "NOTHING_IS_SECRET")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI", "sqlite:///master.sqlite3")
    app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=7)

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.auth_index'  # Make sure this matches the correct view function

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(home)
    app.register_blueprint(admin)
    app.register_blueprint(settings_bp)

    @app.after_request
    def after_request_(response):
        if request.endpoint != "static":
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    @app.before_request
    def app_before_data():
        if request.endpoint != "static":
            user_agent = parse(request.user_agent.string)
            browser = user_agent.browser.family
            device = user_agent.device.family
            operating_system = user_agent.os.family
            bot = user_agent.is_bot

            stat = VisitorStats(
                browser=browser,
                device=device,
                operating_system=operating_system,
                is_bot=bot
            )
            db.session.add(stat)
            db.session.commit()

    app.cli.add_command(create_admin_user)

    return app
