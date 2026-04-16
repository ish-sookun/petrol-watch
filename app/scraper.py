import re
from datetime import datetime
from decimal import Decimal

import requests
from bs4 import BeautifulSoup

from app.extensions import db
from app.models import FuelPrice

STC_URL = 'https://www.stcmu.com/ppm/retail-prices'
USER_AGENT = (
    'Mozilla/5.0 (compatible; PetrolWatch/1.0; '
    '+https://github.com/petrol-watch)'
)


def parse_stc_date(date_str):
    """Parse STC date formats: '16-April-2026', '3-Oct-04', etc."""
    date_str = date_str.strip()

    # Skip non-date rows like "Before APM (01 July 2002)"
    if 'before' in date_str.lower() or 'apm' in date_str.lower():
        return None

    # Try full month name with 4-digit year: 16-April-2026
    try:
        return datetime.strptime(date_str, '%d-%B-%Y').date()
    except ValueError:
        pass

    # Try abbreviated month with 2-digit year: 3-Oct-04
    try:
        return datetime.strptime(date_str, '%d-%b-%y').date()
    except ValueError:
        pass

    # Try full month name with 2-digit year: 5-January-06
    try:
        return datetime.strptime(date_str, '%d-%B-%y').date()
    except ValueError:
        pass

    return None


def parse_price(price_str):
    """Extract numeric price from string like '64.25' or 'Rs 64.25'."""
    cleaned = re.sub(r'[^\d.]', '', price_str.strip())
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except Exception:
        return None


def scrape_stc_prices():
    """Scrape STC retail prices page. Returns count of new rows inserted."""
    response = requests.get(STC_URL, timeout=15, headers={
        'User-Agent': USER_AGENT
    })
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if not table:
        raise ValueError('Could not find price table on STC page.')

    rows = table.find_all('tr')[1:]  # Skip header row
    new_count = 0

    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 3:
            continue

        date_str = cells[0].get_text(strip=True)
        mogas_str = cells[1].get_text(strip=True)
        gasoil_str = cells[2].get_text(strip=True)

        parsed_date = parse_stc_date(date_str)
        if parsed_date is None:
            continue

        mogas = parse_price(mogas_str)
        gasoil = parse_price(gasoil_str)
        if mogas is None or gasoil is None:
            continue

        existing = db.session.query(FuelPrice).filter_by(
            date=parsed_date
        ).first()
        if not existing:
            db.session.add(FuelPrice(
                date=parsed_date,
                mogas=mogas,
                gasoil=gasoil,
            ))
            new_count += 1

    db.session.commit()
    return new_count
