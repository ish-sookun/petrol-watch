# Petrol Watch - Mauritius Fuel Price Tracker

A web application that tracks the evolution of Gasoline (Mogas) and Diesel (Gas Oil) retail prices in Mauritius. Price data is sourced from the [State Trading Corporation (STC)](https://www.stcmu.com/ppm/retail-prices).

This application is built for demo purposes to teach university students about containerizing and deploying Python applications on the Google Cloud Platform. It aims to introduce students to Cloud Native Technologies such as Cloud Run and Google Kubernetes Engine (GKE).

## Features

- **Price Dashboard** - Interactive line chart showing Gasoline and Diesel price history from 2004 to present
- **Current Prices** - Prominently displayed current fuel prices
- **Admin Backoffice** - Login-protected panel to add, edit, and delete price entries
- **STC Scraper** - One-click import of the latest prices from the STC website
- **Mobile Responsive** - Fully responsive design with a mobile hamburger menu

## Technology Stack

| Layer        | Technology                                                  |
|-------------|-------------------------------------------------------------|
| Backend     | Python 3.14, Flask                                          |
| Database    | PostgreSQL 16 with SQLAlchemy ORM                           |
| Frontend    | HTML5, CSS3, JavaScript (ES6)                               |
| Charts      | Chart.js with date-fns adapter                              |
| Auth        | Flask-Login with Werkzeug password hashing                  |
| Sessions    | Flask-Session (server-side, stored in PostgreSQL)           |
| Scraper     | Requests + BeautifulSoup4                                   |
| WSGI Server | Gunicorn                                                    |
| Container   | Docker (multi-stage build)                                  |
| Deployment  | Google Cloud Run + Cloud SQL                                |

## Project Structure

```
petrol-watch/
├── app/
│   ├── __init__.py          # App factory & CLI commands
│   ├── config.py            # Configuration (dev/prod)
│   ├── models.py            # Database models (FuelPrice, User)
│   ├── extensions.py        # Flask extensions (SQLAlchemy, Login)
│   ├── scraper.py           # STC website scraper
│   ├── public/              # Public blueprint (homepage, API)
│   ├── admin/               # Admin blueprint (CRUD, scraper)
│   ├── static/              # CSS, JavaScript
│   └── templates/           # Jinja2 HTML templates
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── Dockerfile               # Production container image
├── docker-compose.yml       # Local development setup
└── README.md
```

## Development Setup

### Option A: Docker Compose (Recommended)

This is the easiest way to get started — it runs both the app and PostgreSQL in containers.

```bash
# Clone the repository
git clone <repo-url>
cd petrol-watch

# Start the application and database
docker-compose up --build

# In a separate terminal, seed the database with historical prices
docker-compose exec web flask seed

# Create an admin user
docker-compose exec web flask create-admin admin password123
```

The app is now running at **http://localhost:5000**

### Option B: Local Python

Requires Python 3.10+ and a running PostgreSQL instance.

```bash
# Clone the repository
git clone <repo-url>
cd petrol-watch

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env if your PostgreSQL credentials differ

# Create the database
createdb petrol_watch

# Seed with historical prices from STC
flask seed

# Create an admin user
flask create-admin admin password123

# Run the development server
flask run
```

The app is now running at **http://localhost:5000**

### Environment Variables

| Variable       | Description                  | Default                                       |
|---------------|------------------------------|-----------------------------------------------|
| `FLASK_ENV`   | Environment (development/production) | `development`                          |
| `SECRET_KEY`  | Flask secret key             | `dev-secret-change-me`                        |
| `DATABASE_URL`| PostgreSQL connection string | `postgresql+psycopg://root:@127.0.0.1:5432/petrol_watch` |

### CLI Commands

| Command                               | Description                              |
|---------------------------------------|------------------------------------------|
| `flask seed`                          | Import all historical prices from STC    |
| `flask create-admin <user> <pass>`    | Create an admin user                     |

## Production Deployment on Google Cloud Run

### Prerequisites

- Google Cloud account with billing enabled
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and authenticated
- Docker installed locally

### Step 1: Create a GCP Project and Enable APIs

```bash
gcloud projects create petrol-watch --name="Petrol Watch"
gcloud config set project petrol-watch
gcloud services enable run.googleapis.com cloudbuild.googleapis.com sqladmin.googleapis.com
```

### Step 2: Create a Cloud SQL PostgreSQL Instance

```bash
gcloud sql instances create petrol-watch-db \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region=us-central1

gcloud sql databases create petrol_watch --instance=petrol-watch-db

gcloud sql users set-password postgres \
  --instance=petrol-watch-db \
  --password=YOUR_SECURE_PASSWORD
```

### Step 3: Build and Push the Container Image

```bash
gcloud builds submit --tag gcr.io/petrol-watch/petrol-watch-app
```

### Step 4: Deploy to Cloud Run

```bash
gcloud run deploy petrol-watch \
  --image gcr.io/petrol-watch/petrol-watch-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --add-cloudsql-instances petrol-watch:us-central1:petrol-watch-db \
  --set-env-vars "DATABASE_URL=postgresql+psycopg://postgres:YOUR_SECURE_PASSWORD@/petrol_watch?host=/cloudsql/petrol-watch:us-central1:petrol-watch-db" \
  --set-env-vars "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" \
  --set-env-vars "FLASK_ENV=production"
```

### Step 5: Seed the Database

```bash
gcloud run jobs create seed-db \
  --image gcr.io/petrol-watch/petrol-watch-app \
  --command "flask" \
  --args "seed" \
  --add-cloudsql-instances petrol-watch:us-central1:petrol-watch-db \
  --set-env-vars "DATABASE_URL=postgresql+psycopg://postgres:YOUR_SECURE_PASSWORD@/petrol_watch?host=/cloudsql/petrol-watch:us-central1:petrol-watch-db"

gcloud run jobs execute seed-db
```

### Step 6: Create Admin User

```bash
gcloud run jobs create create-admin \
  --image gcr.io/petrol-watch/petrol-watch-app \
  --command "flask" \
  --args "create-admin,admin,YOUR_ADMIN_PASSWORD" \
  --add-cloudsql-instances petrol-watch:us-central1:petrol-watch-db \
  --set-env-vars "DATABASE_URL=postgresql+psycopg://postgres:YOUR_SECURE_PASSWORD@/petrol_watch?host=/cloudsql/petrol-watch:us-central1:petrol-watch-db"

gcloud run jobs execute create-admin
```

Your application is now live at the URL printed by the `gcloud run deploy` command.

## Database Notes

### Migrations

This project uses `db.create_all()` to create tables automatically on startup. There is no migration tool — when you add or change models, the new tables are created but existing tables are not altered. For a production application with evolving schemas, consider using [Flask-Migrate](https://flask-migrate.readthedocs.io/) (Alembic) for proper migration management.

### Sessions

User sessions are stored server-side in the `sessions` table via Flask-Session. The browser cookie only holds a signed session ID.

Expired sessions are **not** automatically cleaned up and will accumulate over time. In production, you should periodically delete expired rows:

```sql
DELETE FROM sessions WHERE expiry < NOW();
```

Or schedule this as a cron job / Cloud Run job.

## Data Source

Price data is scraped from the [STC Retail Prices](https://www.stcmu.com/ppm/retail-prices) page, which publishes fuel prices determined by the Petroleum Pricing Committee under Government Notice No. 9 of 2011.

## License

MIT
