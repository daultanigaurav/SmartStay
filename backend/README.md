HostelEase Backend (Django + DRF)

Prerequisites
- Python 3.11+
- PostgreSQL 14+

Setup
1) Create and activate a virtual environment
   - Windows (PowerShell):
     - python -m venv venv
     - .\venv\Scripts\Activate.ps1
   - macOS/Linux:
     - python3 -m venv venv
     - source venv/bin/activate

2) Install dependencies
   - pip install --upgrade pip
   - pip install -r requirements.txt

3) Environment variables
   - Copy .env.example to .env and fill values

4) Run migrations and start server
   - python manage.py makemigrations
   - python manage.py migrate
   - python manage.py createsuperuser
   - python manage.py runserver

API Base: http://127.0.0.1:8000/api/

Auth (JWT)
- POST /api/auth/token/ (username, password)
- POST /api/auth/token/refresh/

Apps
- core: users, rooms, attendance, complaints, payments, feedback


