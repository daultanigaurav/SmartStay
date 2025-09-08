# SmartStay – Hostel Management System

SmartStay is a full‑stack hostel management system built with Django REST Framework and React (Vite). It helps wardens/admins manage rooms, students, payments, complaints, maintenance, notices, and more. Students can register, log in, view notices, submit complaints/maintenance requests, mark attendance, request visitor passes, browse/transfer rooms, and manage their profile.

## Tech Stack

- Backend: Django 5, Django REST Framework, Simple JWT, Channels (optional)
- Frontend: React (Vite), Axios
- DB: SQLite by default (PostgreSQL ready via `DATABASE_URL`)

## Major Features (current)

- Authentication with JWT (login/register)
- Profile management
  - Update profile fields
  - Change password
  - Upload/remove profile picture
- Notices
  - List with read/unread state per user
  - Mark read / unread
- Complaints
  - Create complaints, threaded comments
  - Warden can update status (open/in_progress/resolved)
- Maintenance requests
  - Create requests
  - Warden assign and update status (pending/in_progress/completed/cancelled)
- Rooms
  - Browse available rooms
  - Book a room (student)
  - Request transfer to another room
- Attendance
  - Mark “today”
  - Month view (present/absent per day)
- Visitor passes
  - Request pass (student)
  - Approve pass (warden/admin)

## Repository Layout

```
SmartStay/
  backend/               # Django project (hostelease) + core app
  frontend/              # Vite React app
```

## Quick Start

Prerequisites
- Python 3.10+
- Node.js 18+

### 1) Backend

Install dependencies (SQLite mode; no Postgres required):

```bash
cd backend
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt || true
# If psycopg2 build fails, it is safe to ignore in SQLite mode
pip install Django==5.0.7 djangorestframework==3.15.2 djangorestframework-simplejwt==5.3.1 django-cors-headers==4.4.0 django-filter==24.3 dj-database-url==2.2.0
```

Run migrations and (optionally) seed:

```bash
python manage.py migrate
# optional demo data
python manage.py seed_data  # if the command exists
```

Create a superuser (for admin/warden tasks):

```bash
python manage.py createsuperuser
```

Start dev server (note: to avoid some environments’ autoreload issues, run without reloader):

```bash
python manage.py runserver 0.0.0.0:8000 --insecure --noreload
```

Backend will be at `http://localhost:8000`.

### 2) Frontend

```bash
cd frontend
npm install

# Some environments may block node_modules/.bin/vite.
# If you see “Permission denied”, you can run:
chmod +x node_modules/.bin/vite || true

# Start Vite (bind to all interfaces for LAN testing)
npm run dev -- --host --port 5173
# or
npx vite --host --port 5173
```

Frontend will be at `http://localhost:5173`.

## Environment Configuration

Backend (`backend/hostelease/settings.py`) supports env vars:

- `SECRET_KEY` – Django secret (default dev key)
- `DEBUG` – `True`/`False` (default `True`)
- `ALLOWED_HOSTS` – comma list (default `127.0.0.1,localhost`)
- DB via either:
  - `DATABASE_URL` (e.g., `postgres://...`) or
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`
- CORS/CSRF
  - `FRONTEND_ORIGIN` (default `http://localhost:5173`)
  - `CSRF_TRUSTED_ORIGINS` (comma list; defaults to `FRONTEND_ORIGIN`)

When no DB env is set, SmartStay falls back to SQLite at `backend/db.sqlite3`.

## Default API Routes (key ones)

Base API path: `http://localhost:8000/api/`

Auth
- `POST auth/token/` – obtain JWT (`username`, `password`)

Users
- `GET users/me/` – current user
- `PATCH users/me/` – update own profile
- `POST users/change-password/` – change password
- `POST|DELETE users/me/avatar/` – upload/remove profile picture

Notices
- `GET notices/` – list (filtered by role, active)
- `POST notices/{id}/read/` – mark read
- `POST notices/{id}/unread/` – mark unread

Complaints
- `GET|POST complaints/`
- `PATCH complaints/{id}/update_status/` (warden)
- `POST complaints/{id}/comments/`

Maintenance
- `GET|POST maintenance/`
- `PATCH maintenance/{id}/assign/` (warden)
- `PATCH maintenance/{id}/update_status/` (warden)

Rooms & Allocations
- `GET rooms/available/`
- `GET allocations/active/`
- `POST allocations/` – book (student)
- `POST allocations/transfer/` – end current, start new (student)

Attendance
- `GET attendance/`
- `POST attendance/mark/` – mark today (student)

Visitors
- `GET|POST visitors/`
- `PATCH visitors/{id}/` – update status (e.g., approve as warden)

Payments (sandbox)
- `GET payments/stats/`
- `POST payments/create_order/` – create a pending record

## Frontend Pages (src/components)

- `Login.jsx` – login/register
- `Dashboard.jsx` – key stats
- `Profile.jsx` – profile edit, password change, avatar upload
- `Notices.jsx` – list + read/unread
- `Complaints.jsx` – create/list + comments
- `Maintenance.jsx` – create/list + status update
- `Rooms.jsx` – browse/book/transfer
- `Attendance.jsx` – mark today + month view
- `Visitors.jsx` – request pass + approve (warden)

## Tips & Troubleshooting

- Vite “Permission denied”:
  - Run `chmod +x frontend/node_modules/.bin/vite` or start with `npx vite --host`.

- Django autoreload spawning issues in some shells:
  - Use: `python manage.py runserver --noreload`.

- PostgreSQL optional:
  - If `psycopg2` build fails and you don’t need Postgres, stick to SQLite (no action needed).

- CORS/CSRF:
  - Set `FRONTEND_ORIGIN` to your dev URL if you change ports/hosts.

## Production Notes (high‑level)

- Put real `SECRET_KEY` and `DEBUG=False` in env
- Use Postgres via `DATABASE_URL`
- Serve the React build (Vite `npm run build`) behind a reverse proxy
- Configure static/media in Django (`collectstatic`, proper storage)
- Add HTTPS, secure cookies, CSRF settings

## Roadmap

- Rich calendar UI for attendance
- Payments flow enhancements and receipts
- Role management UI (admin)
- Documents vault verification UX
- Real‑time updates (Channels/WebSockets)

## License

This project is released under the MIT License. See `LICENSE` for details.
