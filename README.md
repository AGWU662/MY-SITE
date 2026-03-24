# Elite Wealth Capital

Django 4.2 investment platform with user authentication, KYC verification, crypto deposits, investment plans, and admin dashboard.

## Tech Stack
- **Backend:** Django 4.2, Celery, Redis
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Admin:** Django Jazzmin (Bootstrap-based)
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **Deployment:** Docker, Render, Gunicorn

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Project Structure
```
├── accounts/        # User authentication & profiles
├── investments/     # Investment plans & transactions  
├── dashboard/       # User dashboard views
├── kyc/            # KYC verification
├── notifications/  # Email & user notifications
├── tasks/          # Celery background tasks
├── templates/      # HTML templates
├── static/         # CSS, JS, Images
└── elite_wealth/   # Django settings & URLs
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgres://...
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

## Admin Panel

Access at `/admin/` with superuser credentials. Features:
- User management with balance controls
- KYC document review
- Deposit/Withdrawal approval
- Investment plan management
- Financial statistics dashboard

## Deployment

Configured for Render deployment via `render.yaml`. See Render dashboard for environment configuration.

## License

Proprietary - Elite Wealth Capital Ltd.
