from flask import jsonify, render_template

from app.extensions import db
from app.models import FuelPrice
from app.public import public_bp


@public_bp.route('/')
def index():
    latest = db.session.query(FuelPrice).order_by(
        FuelPrice.date.desc()
    ).first()
    return render_template('public/index.html', latest=latest)


@public_bp.route('/api/prices')
def get_prices():
    prices = db.session.query(FuelPrice).order_by(
        FuelPrice.date.asc()
    ).all()
    return jsonify([p.to_dict() for p in prices])
