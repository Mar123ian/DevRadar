# DevRadar

A Django-based web application for discovering software development services, categorized by types and technologies, and linked to programmers. It provides CRUD operations, clean navigation across apps, and a simple UI.

## Features

- Services directory with create/read/update/delete (CRUD)
- Category management:
  - Types (e.g., Web, Mobile, Data)
  - Technologies (e.g., Django, React, PostgreSQL)
- Programmers management with details and listings
- Comments system for services
- Slug-based detail pages for SEO-friendly URLs
- Pagination-ready class-based views (CBVs)
- Separated apps with clean URL routing and templates
- Static files and media support

## Tech Stack

- Python 3.11+
- Django 5.x
- PostgreSQL (default)
- HTML templates, CSS (static/styles.css)

## Project Structure

```
DevRadar/
├─ manage.py
├─ requirements.txt
├─ devradar/                # Project settings and root URLs
│  ├─ settings.py
│  └─ urls.py
├─ core/                    # Home page / base URLs
│  └─ urls.py
├─ categories/              # Types and Technologies
│  ├─ models.py
│  ├─ forms.py
│  ├─ urls.py
│  └─ views.py
├─ services/                # Services CRUD
│  ├─ models.py
│  ├─ forms.py
│  ├─ urls.py
│  └─ views.py
├─ programmers/             # Programmers CRUD
│  ├─ models.py
│  ├─ forms.py
│  ├─ urls.py
│  └─ views.py
├─ comments/                # Comments on services
│  ├─ models.py
│  ├─ urls.py
│  └─ views.py
├─ templates/               # All HTML templates grouped by app
├─ static/                  # Static assets (styles.css)
└─ media/                   # User-uploaded media (served in dev)
```

## URLs Overview

Root URLConf: `devradar/urls.py`

- `/` → core home
- `/categories/` → categories app
  - `/categories/type/all/` → list all types
  - `/categories/type/create/` → create type
  - `/categories/type/delete/<type_slug>/` → delete type
  - `/categories/type/<type_slug>/` → type details
  - `/categories/technology/create/` → create technology
- `/services/` → services app
  - `/services/all/` → list all services
  - `/services/create/` → create service
  - `/services/update/<service_slug>/` → update service
  - `/services/delete/<service_slug>/` → delete service
  - `/services/<service_slug>/` → service details
- `/programmers/` → programmers app
  - `/programmers/all/` → list all programmers
  - `/programmers/create/` → create programmer
  - `/programmers/update/<programmer_slug>/` → update programmer
  - `/programmers/delete/<programmer_slug>/` → delete programmer
  - `/programmers/<programmer_slug>/` → programmer details

Admin: `/admin/`

## Quick Start

1) Clone and enter the project directory

```
git clone https://github.com/Mar123ian/DevRadar.git
cd DevRadar
```

2) Create and activate a virtual environment (Windows PowerShell)

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Install dependencies
```
pip install -r requirements.txt
```

4) Create PostgreSQL database and configure `DATABASES` in `settings.py`:
```py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mydatabase", # replace with your database name
        "USER": "mydatabaseuser", # replace with your database username
        "PASSWORD": "mypassword", # replace with your database password
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}
```

5) Apply migrations and create a superuser

```
python manage.py migrate
python manage.py createsuperuser
```

6) Run the development server

```
python manage.py runserver
```

7) Open in browser

- App: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Configuration

All key settings are in `devradar/settings.py`.

- DEBUG: enabled by default for development
- Database: defaults to Postgres; change `DATABASES` for SQLite
- Static files:
  - STATIC_URL = `/static/`
  - In development Django serves static automatically when `DEBUG=True`
- Media files:
  - MEDIA_URL = `media/`
  - MEDIA_ROOT configured; served in development via `static()` in `urls.py`

### Environment variables (recommended for production)

- SECRET_KEY
- DEBUG (set to `False`)
- ALLOWED_HOSTS
- DATABASE_URL or discrete DB settings
- STATIC_ROOT and MEDIA_ROOT paths

## Apps and Templates

- Templates are organized under `templates/` by app:
  - `services/`: all, details, short details and forms (create/update)
  - `programmers/`: all, details, and forms (create/update/delete)
  - `categories/`: all types, type details, technology details
  - `core/`: base.html and home.html
- Styling lives in `static/styles.css`

## Development Notes

- Uses Django Class-Based Views extensively
- Slug fields are used for details routes for stable URLs
- `urls.py` per app with `include(...)` in project root URLs
- Add your app to `INSTALLED_APPS` when creating new modules
- Prefer forms in `forms.py` to keep views thin

## Testing

Basic manual testing via the browser. To add automated tests, create `tests.py` in each app and run:

```
python manage.py test
```

## Deployment Tips

- Collect static files:

```
python manage.py collectstatic
```

- Configure Gunicorn/Uvicorn + Nginx (or platform-specific config)
- Set environment variables and secure SECRET_KEY
- Use a managed database (PostgreSQL recommended)

## Contributing

- Fork the repository
- Create a feature branch: `git checkout -b feature/xyz`
- Commit changes: `git commit -m "Describe changes"`
- Push to branch: `git push origin feature/xyz`
- Open a Pull Request

## License

This project is licensed under the terms of the LICENSE file in this repository.
