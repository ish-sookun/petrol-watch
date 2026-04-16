from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class FuelPrice(db.Model):
    __tablename__ = 'fuel_prices'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True, index=True)
    mogas = db.Column(db.Numeric(6, 2), nullable=False)
    gasoil = db.Column(db.Numeric(6, 2), nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            'date': self.date.isoformat(),
            'mogas': float(self.mogas),
            'gasoil': float(self.gasoil),
        }

    def __repr__(self):
        return f'<FuelPrice {self.date}: Mogas={self.mogas}, GasOil={self.gasoil}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
