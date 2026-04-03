# PSU Traffic Management System
## Plateau State University, Bokkos — Django Web Application

A web-based Traffic Management System built with Django and SQLite, implementing
vehicle registration, incident reporting, traffic monitoring, and administrative
control as specified in the project document.

---

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Seed Sample Data (optional but recommended)
```bash
python seed_data.py
```

### 4. Start the Development Server
```bash
python manage.py runserver
```

Open your browser at: **http://127.0.0.1:8000**

---

## Test Login Credentials

| Role      | Username        | Password     |
|-----------|-----------------|--------------|
| Admin     | admin           | admin1234    |
| Staff     | dr.mwangi       | staff1234    |
| Student   | amina.ibrahim   | student1234  |
| Visitor   | john.visitor    | visitor1234  |

---

## System Features (from Project Document)

### All Users
- User registration and authentication
- Dashboard with summary statistics
- Report traffic incidents (congestion, parking, near-miss, violations)
- View own incident reports and their status
- Register vehicles and manage own vehicle records

### Admin Only
- View and manage all vehicles (approve / suspend)
- View and manage all incident reports (update status, add notes)
- Manage all user accounts (activate / suspend)
- Generate system-wide reports and statistics
- Full admin action log

---

## Project Structure

```
tms/
├── manage.py
├── seed_data.py
├── requirements.txt
├── db.sqlite3          ← created after migrations
├── tms/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── traffic/
    ├── models.py       ← UserProfile, Vehicle, IncidentReport, AdminAction
    ├── views.py        ← All view logic
    ├── urls.py         ← URL routing
    ├── forms.py        ← Django forms
    ├── admin.py        ← Django admin registration
    ├── context_processors.py
    ├── static/traffic/css/style.css
    └── templates/traffic/
        ├── base.html
        ├── login.html
        ├── register.html
        ├── dashboard.html
        ├── vehicle_list.html
        ├── vehicle_form.html
        ├── vehicle_detail.html
        ├── incident_list.html
        ├── incident_form.html
        ├── incident_detail.html
        ├── user_list.html
        ├── user_detail.html
        └── reports.html
```

## Database Models (ERD)

- **UserProfile** — extends Django User; stores role, department, ID, phone
- **Vehicle** — plate number, type, make, model, color, year, owner (FK User), category, status
- **IncidentReport** — type, location, priority, description, vehicle plate, reported_by (FK User), status, timestamps
- **AdminAction** — admin (FK User), action type, description, timestamp

## Tech Stack
- Backend: Python / Django 4.2
- Database: SQLite (via Django ORM)
- Frontend: HTML5, CSS3, vanilla JavaScript
- Authentication: Django built-in auth system
