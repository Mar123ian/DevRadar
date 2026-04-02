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

## API

The DevRadar API allows authenticated users to programmatically interact with the Services platform. It is built using Django REST Framework and provides full CRUD (Create, Read, Update, Delete) capabilities for Services.

### Authentication

The API requires Token-based authentication. Unauthenticated requests will be rejected.

**1. How to get your API Token:**
1. Log in to your DevRadar account via the web interface (you must be with Editor group).
2. Navigate to the API Info page (`/api/info/` accessible via the main menu).
3. Click the **"ВЗЕМИ API ТОКЕН"** (GET API TOKEN) button to generate a new token.
4. *Note: If you already have a token and believe it has been compromised, you can click the button again to revoke the old one and generate a new one.*

**2. How to use your API Token:**
Include your token in the HTTP headers of every API request. Use the `Authorization` header with the `Token` keyword prefix.

**Header format:**
`http
Authorization: Token YOUR_SECRET_TOKEN_HERE
`

### Endpoints

Base URL: `/api/services/` *(Note: Adjust this if your URLs are prefixed with something like `/api/` in your main `urls.py`)*

* `GET /api/services/` - Retrieve a list of all services.
* `POST /api/services/` - Create a new service.
* `GET /api/services/{id}/` - Retrieve details of a specific service.
* `PUT /api/services/{id}/` - Update a specific service (requires all writable fields).
* `PATCH /api/services/{id}/` - Partially update a specific service.
* `DELETE /api/services/{id}/` - Delete a specific service.

### Fields and Schema

Because the API uses complex relational data, the payload you send (Write) differs from the payload you receive (Read). Read-only fields are ignored if you try to submit them, and write-only fields will never be returned in a GET response.

| Field Name | Type | Access | Description |
| :--- | :--- | :--- | :--- |
| `name` | String | **Read / Write** | The title or name of the service. |
| `description` | String | **Read / Write** | Detailed description of the service. |
| `min_price` | Decimal/Float | **Read / Write** | The minimum price for the service. |
| `max_price` | Decimal/Float | **Read / Write** | The maximum price for the service. |
| `image` | URL | **Read-Only** | The path/URL to the stored image file on the server. Returned when fetching data. |
| `image_url` | String (URL) | **Write-Only** | A direct URL to an external image. Used when creating/updating. *(See "Handling Images" below)*. |
| `programmer_info` | Object | **Read-Only** | A nested object containing details about the programmer (`id`, `username`, `first_name`, `last_name`, `email`). |
| `programmer` | Integer (ID) | **Write-Only** | The Primary Key (ID) of the programmer assigned to this service. |
| `type_info` | Object | **Read-Only** | A nested object containing the full details of the service Type. |
| `type` | Integer (ID) | **Write-Only** | The Primary Key (ID) of the Type category for this service. |
| `technologies_info` | Array of Objects | **Read-Only** | A list of nested objects detailing the associated technologies. |
| `technologies` | Array of Integers | **Write-Only** | A list of Primary Keys (IDs) of the Technologies associated with this service. |
| `comments` | Array of Objects | **Read-Only** | A list of comments attached to the service. Includes `id`, `author`, `content`, and `created_at`. |

### Handling Images (The `image_url` field)

This API does **not** accept raw file uploads (e.g., `multipart/form-data` with binary files). Instead, it fetches images from external URLs.

**How to upload an image:**
When making a `POST` (create) or `PUT/PATCH` (update) request, pass a direct, publicly accessible link to the image using the `image_url` field.

**What the API does:**
1. The backend will intercept your `image_url`.
2. It will automatically download the image from the provided link.
3. It renames the downloaded file to a unique `UUID.jpg`.
4. It saves the file locally to the server's storage.
5. In future `GET` requests, you will see the `image` field populated with the server's local path to this newly saved file.

*Example format for uploading an image:*
`json
"image_url": "https://example.com/path/to/my-public-image.png"
`

### Examples

#### Example Request: Creating a Service (POST)
You can use curl or Postman
```bash
curl -X POST http://127.0.0.1:8000/api/services/ -H "Authorization: Token dca4a7268c17a909fa61e7f58d6f141ab48378f3" -H "Content-Type: application/json" -d @data.json
```
data.json:
```json
{
    "name": "Fullstack Web Development",
    "description": "I will build a complete web application from scratch.",
    "min_price": 500.00,
    "max_price": 2000.00,
    "programmer": 3,
    "type": 1,
    "technologies": [2, 5, 8],
    "image_url": "https://example.com/my-portfolio-cover.jpg"
}
```

#### Example Response: Fetching a Service (GET)

```json
{
    "name": "Fullstack Web Development",
    "description": "I will build a complete web application from scratch.",
    "min_price": 500.00,
    "max_price": 2000.00,
    "image": "/media/services/a1b2c3d4-e5f6-7890.jpg",
    "programmer_info": {
        "id": 3,
        "username": "dev_guru",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
    },
    "type_info": {
        "id": 1,
        "name": "Web Development"
    },
    "technologies_info": [
        { "id": 2, "name": "Django" },
        { "id": 5, "name": "React" },
        { "id": 8, "name": "PostgreSQL" }
    ],
    "comments": []
}
```

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
