# Copilot Instructions for Elite Wealth Capital

## Project Overview
Django 4.2 investment platform with user authentication, KYC verification, crypto deposits, investment plans, and admin dashboard. Deployed on Render with PostgreSQL.

## Tech Stack
- **Backend:** Django 4.2, Celery, Redis
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **Deployment:** Docker, Render, Gunicorn

## Project Structure
```
├── accounts/        # User authentication & profiles
├── investments/     # Investment plans & transactions
├── dashboard/       # User dashboard views
├── kyc/            # KYC verification
├── notifications/  # Email & user notifications
├── tasks/          # Celery background tasks
├── templates/      # HTML templates (gold/dark theme)
├── static/         # CSS, JS, Images
└── elite_wealth/   # Django settings & URLs
```

## Code Conventions
- Follow PEP 8 and Django best practices
- Use class-based views where appropriate
- Keep business logic in models/services, not views
- Use Django's ORM for database queries
- Use Django's built-in security features (CSRF, XSS protection)
- Write tests for all new views, models, and services in the app's `tests.py` file

## Important Files
- `elite_wealth/settings.py` - Django configuration
- `elite_wealth/urls.py` - URL routing
- `elite_wealth/security_headers.py` - CSP & security middleware
- `requirements.txt` - Python dependencies
- `render.yaml` - Render deployment config
- `.github/workflows/django.yml` - CI/CD pipeline (runs tests on Python 3.10, 3.11, 3.12)

## Security Requirements
- Never commit `.env` files or secrets
- Use environment variables for sensitive data
- Follow OWASP guidelines for financial applications
- CSP headers are configured in `elite_wealth/security_headers.py`
- Always use Django's `@login_required` decorator or `LoginRequiredMixin` on protected views
- Validate and sanitize all user inputs using Django forms
- Use parameterized queries via Django ORM; avoid raw SQL

## Testing
```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test accounts
python manage.py test investments
python manage.py test kyc
python manage.py test notifications
python manage.py test tasks

# Required environment variables for testing
DATABASE_URL=sqlite:///db.sqlite3
SECRET_KEY=test-secret-key-for-ci
DEBUG=True
```

## Running Locally
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## CI/CD Workflow
- The CI pipeline is defined in `.github/workflows/django.yml`
- Tests run automatically on push/PR to `master` across Python 3.10, 3.11, and 3.12
- All tests must pass before merging a pull request
- If CI fails, check the workflow logs for the failing test or import error
- Common CI fix: ensure `requirements.txt` is up to date with any new dependencies

## Branch & Pull Request Guidelines
- Use descriptive branch names: `feature/<short-description>`, `fix/<issue-description>`, `chore/<task>`
- Keep pull requests focused on a single concern
- Add a clear description explaining what changed and why
- Reference related issues in the PR description (e.g., `Closes #12`)
- Ensure all CI checks pass before requesting a review

## Dependency Management
- Add new Python packages to `requirements.txt` with a minimum version pin (e.g., `somepackage>=1.0`)
- Do not pin to exact versions unless necessary to avoid conflicts
- After adding a dependency, run `pip install -r requirements.txt` locally and confirm tests still pass
- Keep `node_modules/` out of version control (already in `.gitignore`)

## Resolving Conflicts
- Always rebase or merge `master` into your branch before opening a PR
- For migration conflicts, run `python manage.py migrate` after resolving and re-test
- For `requirements.txt` conflicts, include all dependencies from both sides of the conflict

## Configuration & Workflow Management
- GitHub Actions workflows live in `.github/workflows/`
- Environment-specific settings use `python-dotenv` and `.env` files (never commit `.env`)
- Deployment configuration is in `render.yaml` and `Procfile`
- Docker configuration is in `Dockerfile` and `entrypoint.sh`

## Color Theme
- Primary Gold: `#d4af37`
- Dark Background: `#0a0a0a`
- Card Background: `rgba(20, 20, 20, 0.85)`
