from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.admin import admin_bp
from app.extensions import db
from app.models import FuelPrice, User


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = db.session.query(User).filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))

        flash('Invalid username or password.', 'error')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'success')
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    pagination = db.session.query(FuelPrice).order_by(
        FuelPrice.date.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/dashboard.html', pagination=pagination)


@admin_bp.route('/prices/add', methods=['GET', 'POST'])
@login_required
def add_price():
    if request.method == 'POST':
        error = _validate_price_form(request.form)
        if error:
            flash(error, 'error')
            return render_template('admin/price_form.html', editing=False)

        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        existing = db.session.query(FuelPrice).filter_by(date=date).first()
        if existing:
            flash(f'A price entry for {date.strftime("%d %B %Y")} already exists.', 'error')
            return render_template('admin/price_form.html', editing=False)

        price = FuelPrice(
            date=date,
            mogas=Decimal(request.form['mogas']),
            gasoil=Decimal(request.form['gasoil']),
        )
        db.session.add(price)
        db.session.commit()
        flash('Price entry added.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/price_form.html', editing=False)


@admin_bp.route('/prices/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_price(id):
    price = db.session.get(FuelPrice, id)
    if not price:
        flash('Price entry not found.', 'error')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        error = _validate_price_form(request.form)
        if error:
            flash(error, 'error')
            return render_template('admin/price_form.html', editing=True, price=price)

        new_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        existing = db.session.query(FuelPrice).filter_by(date=new_date).first()
        if existing and existing.id != price.id:
            flash(f'A price entry for {new_date.strftime("%d %B %Y")} already exists.', 'error')
            return render_template('admin/price_form.html', editing=True, price=price)

        price.date = new_date
        price.mogas = Decimal(request.form['mogas'])
        price.gasoil = Decimal(request.form['gasoil'])
        db.session.commit()
        flash('Price entry updated.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/price_form.html', editing=True, price=price)


@admin_bp.route('/prices/delete/<int:id>', methods=['POST'])
@login_required
def delete_price(id):
    price = db.session.get(FuelPrice, id)
    if not price:
        flash('Price entry not found.', 'error')
    else:
        db.session.delete(price)
        db.session.commit()
        flash('Price entry deleted.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/scrape', methods=['POST'])
@login_required
def scrape_prices():
    from app.scraper import scrape_stc_prices
    try:
        count = scrape_stc_prices()
        if count > 0:
            flash(f'Imported {count} new price entries.', 'success')
        else:
            flash('No new prices found.', 'info')
    except Exception as e:
        flash(f'Scraping failed: {str(e)}', 'error')
    return redirect(url_for('admin.dashboard'))


def _validate_price_form(form):
    date_str = form.get('date', '').strip()
    mogas_str = form.get('mogas', '').strip()
    gasoil_str = form.get('gasoil', '').strip()

    if not date_str or not mogas_str or not gasoil_str:
        return 'All fields are required.'

    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return 'Invalid date format.'

    try:
        mogas = Decimal(mogas_str)
        gasoil = Decimal(gasoil_str)
        if mogas <= 0 or gasoil <= 0:
            return 'Prices must be positive numbers.'
    except InvalidOperation:
        return 'Invalid price value.'

    return None
