# CollegeERP

A modern college / campus management system built with **Django** and **PostgreSQL**. It connects students, faculty and administrators in one place with features for **attendance**, **marks**, **timetables** and **reports**.

## Features

- **3 roles with dedicated dashboards**: Administrator, Student and Faculty
- **Attendance** — teachers mark attendance per class, students view per-subject attendance with 75% tracking
- **Marks** — enter and edit internal tests, events and semester end exam marks
- **Timetable** — weekly schedules for students and teachers, with a "free teachers" lookup
- **Reports** — per-subject reports showing each student's CIE and attendance
- **REST API** — JSON endpoints for detail, attendance, marks and timetable
- **Modern responsive UI** — clean card-based design, dashboards, badges and stat cards

## Tech Stack

| Layer    | Technology                      |
|----------|---------------------------------|
| Backend  | Python 3, Django 4.2            |
| Database | PostgreSQL                      |
| API      | Django REST Framework + Token auth |
| Frontend | Bootstrap 4, jQuery, Font Awesome |

## Prerequisites

- Python 3.10+
- PostgreSQL (running locally on port `5432`)
- `pip`

## Installation & Setup

```bash
# 1. Create and activate a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # Linux / macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the PostgreSQL database
#    In psql or pgAdmin create a database named: erpdb
#    e.g.  CREATE DATABASE erpdb;

# 4. Configure the database connection
#    Defaults are already set in CollegeERP/settings.py (erpdb / postgres / localhost:5432).
#    To override them, set these environment variables:
#      DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# 5. Run migrations
python manage.py migrate

# 6. Seed the database with demo data (admin, 4 students, 6 faculty, courses, timetable)
python manage.py seed_data

# 7. Start the server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

> To reset the database entirely, drop the tables and re-run `python manage.py migrate` then `python manage.py seed_data`.

## Deploy on Render

This repo ships with a `render.yaml` blueprint (web service + free PostgreSQL) and a `Procfile` for gunicorn. To deploy:

1. Push this repository to GitHub.
2. Go to **https://dashboard.render.com** → **New** → **Blueprint** and select this repo.
3. Render reads `render.yaml`, creates the PostgreSQL database and web service, installs dependencies, runs `collectstatic` + `migrate`, and starts gunicorn automatically.

Environment variables are handled automatically:

- `DATABASE_URL` — wired from the Render PostgreSQL instance
- `DJANGO_SECRET_KEY` — auto-generated
- `DJANGO_DEBUG` — `False` in production
- `DJANGO_ALLOWED_HOSTS` — `.onrender.com` and localhost

After the first deploy, open the service's **Shell** tab and run `python manage.py seed_data` to load the demo data (admin, students, faculty, courses, timetable).

## Login Credentials

### Administrator

| Role | Username | Password     |
|------|----------|--------------|
| Admin | `admin` | `Hitman@4165` |

The admin dashboard lets you add students and faculty and gives quick access to the Django admin panel at **http://127.0.0.1:8000/admin**.

### Sample logins for testing

The database is seeded with **4 students** and **6 faculty**. One sample login for each role is shared here so you can try the portal:

| Role    | Username      | Password        |
|---------|---------------|-----------------|
| Student | `rahul_001`   | `rahul_2004`    |
| Faculty | `anil_cs01`   | `anil_1980`     |

> For security, the credentials of the other seeded students/faculty are **not** listed here. They are auto-generated using the pattern `firstname_<last3-of-USN-or-ID>` with password `firstname_<birth-year>` (e.g. student `1BY21CS002` → `sneha_002` / `sneha_2004`). You can change any password from the Django admin panel.

## URL Map

| URL                        | Description                            |
|----------------------------|----------------------------------------|
| `/`                        | Role-based dashboard (login required)  |
| `/accounts/login/`         | Login page                             |
| `/accounts/logout/`        | Logout                                 |
| `/student/<usn>/attendance/`  | Student attendance summary          |
| `/student/<usn>/marks_list/`   | Student marks                      |
| `/student/<class>/timetable/`  | Student timetable                  |
| `/teacher/<id>/1/Classes/`    | Faculty attendance entry            |
| `/teacher/<id>/2/Classes/`    | Faculty marks entry                 |
| `/teacher/<id>/3/Classes/`    | Faculty reports                     |
| `/add-student/`             | Admin — add a student                   |
| `/add-teacher/`             | Admin — add a faculty member             |
| `/admin/`                   | Django admin panel                      |

## REST API

| Endpoint          | Method | Auth | Description                      |
|-------------------|--------|------|----------------------------------|
| `/api/login/`     | POST   | None | `{"username","password"}` → token |
| `/api/detail/`    | GET    | Token | Logged-in student/teacher detail |
| `/api/attendance/`| GET    | Token | Attendance totals for the user   |
| `/api/marks/`     | GET    | Token | Marks for the user               |
| `/api/timetable/` | GET    | Token | Weekly timetable for the user    |

Use the token from `/api/login/` as an `Authorization: Token <token>` header on the other endpoints.

## Project Structure

```
CollegeERP/            # Project settings (PostgreSQL config, URLs)
info/                  # Main app: models, views, admin, templates
  management/commands/seed_data.py   # Demo data seeder
  static/info/         # Bootstrap assets + custom.css
  templates/info/      # All page templates
apis/                  # DRF serializers + REST views
```

## Troubleshooting

- **`django.db.utils.OperationalError`** — PostgreSQL isn't running, or the DB name/user/password are wrong. Verify with `psql -U postgres -d erpdb` and check the `DB_*` environment variables.
- **No classes appear** — the attendance date range is set by `seed_data`. You can reset the date range from the Django admin (Attendance → Reset Attendance).
- **Static styles missing** — make sure you run through the dev server (`python manage.py runserver`) which serves static files automatically.
