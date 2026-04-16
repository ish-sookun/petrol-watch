import os

import click
from dotenv import load_dotenv
from flask import Flask

from app.config import config
from app.extensions import db, login_manager, sess

load_dotenv()


def create_app():
    app = Flask(__name__)

    env = os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[env])

    app.config['SESSION_SQLALCHEMY'] = db
    db.init_app(app)
    sess.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.public import public_bp
    from app.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()

    @app.cli.command('seed')
    def seed_command():
        """Import all historical prices from STC."""
        from app.seed import seed_prices
        count = seed_prices()
        click.echo(f'Seeded {count} price entries.')

    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('password')
    def create_admin(username, password):
        """Create an admin user."""
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f'Admin user "{username}" created.')

    return app
