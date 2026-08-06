# Trekk App :- Trekking Management Application
A completely Flask-based web-application to manage trekking activities involving trek organizers, staff, and users. This app solves the problem of  individuals and many trekking groups rely on spreadsheets, phone calls, or manual coordination, by providing trek approvals, track bookings, avoid overbooking, and maintain trek history. Staffs can manage participants efficiently and user can effortlessly book and track their trekking.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)](https://www.sqlite.org/)
---

## System - Features

### Role-Based Access Control
Three distinct user portals with specific permissions:

#### Admin Portal
- Comprehensive dashboard with system-wide statistics
- Complete user and staff management
  - View, search, and manage registered users and staff members
  - Approve or Reject or blacklist users and staff
- Complete Trek lifecycle management
  - Create, edit, and delete treks
  - Assign specific trek to specific staff members to guide treks
- Search Staff/User/Treks within every module

#### Staff Portal
- Dedicated dashboard displaying assigned treks, open treks & total treks
- Dynamic slot tracking and management
- Update trek statuses (e.g., Open, Closed or Completed)
- View and manage participant for specific treks slot
- Update Profile for Validity


#### User Portal 
- Browse and Explore available treks with inbulid search and filter funcitonallity (by Difficulty and Location)
- One Click Trek Booking and Management
- View Active Bookings Of Treks, also cancel (if needed) 
- View Complete History Of Completed Treks 
- Update Profile (user preference)

---

## 🛠 Technology Stack
### Frontend
- **HTML5 / CSS3**  — Structure and Styling Web Pages
- **Jinja2** — Template engine
- **Bootstrap 5** — Responsive UI framework 

### Backend
- **Flask** — Lightweight Python web framework
- **Flask-SQLAlchemy** — ORM for database operations
- **Werkzeug** — Password hashing and security utilities

### Database
- **SQLite** — Lightweight Relational Database 

---
## 🗄 Database Schema

### Entity Relationship Diagram
```
┌─────────────────┐
│      USER       │
│─────────────────│
│ user_id (PK)    |
│ username        │
│ email (UNIQUE)  │
│ full_name       │
│ password        │
│ role            │
│ status          │
└─────────────────┘
        │
   ─────┴─────
   │         │
   │ 1:N     │ 1:N
   ▼         ▼
┌────────────────┐    ┌──────────────────┐
│   BOOKING      │    │      TREKK       │
│────────────────│    │──────────────────│
│ booking_id(PK) │    │ trek_id (PK)     │
│ user_id (FK)   │    │ difficulty       │
│ trek_id (FK)   │    │ name             │
│ status         │    │ duration         |
| assigned_staff |    │ assigned staff   |
| booking_date   |    | location         |       
│    │           |    │ total_slots      │
└────────────────┘    │ status           |
                      | price            |
                      └──────────────────┘
```
## 📡 Route Structure

### Authentication
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET, POST | `/login` | (User/Admin) Login | Public |
| GET, POST | `/register` | New Trekker Registration | Public |
| GET | `/logout` | Terminate session | Authenticated |

### Admin's Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/admin/admin_dashboard` | Admin Dashboard  | Admin |
| GET |  `/admin/treks` | Treks Page | Admin |
| GET, POST | `/admin/treks/Add_Treks` | Create a new trek | Admin |
| GET, POST | `/admin/treks/<t_id>/edit_trek` | Edit trek | Admin |
| POST | `/admin//treks/<t_id>/delete_trek` | Delete trek | Admin |
| GET |  `/admin/staff` | Staff Page | Admin |
| GET, POST | `/admin/staff/validate_staff` | Validate new staff member | Admin |

| POST | `/admin/staff/<user_id>/approve_staff` | Approve Staff | Admin |
| POST | `/admin/staff/<user_id>/reject_staff` | Reject Staff | Admin |
| POST | `/admin/staff/<user_id>/blacklist_staff` | Blacklist Staff | Admin |
| POST | `/admin/staff/<user_id>/delete_staff` | Delete Staff | Admin |
| GET |  `/admin/user` | User Page | Admin |
| GET, POST | `/admin/user/validate_staff` | Validate new User member | Admin |

| POST | `/admin/user/<user_id>/approve_staff` | Approve User | Admin |
| POST | `/admin/user/<user_id>/reject_staff` | Reject User | Admin |
| POST | `/admin/user/<user_id>/blacklist_staff` | Blacklist User | Admin |
| POST | `/admin/user/<user_id>/delete_staff` | Delete User | Admin |
| GET | `/admin/bookings` | View bookings | Admin |



### Staff's Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/staff_dashboard` | Staff dashboard | Staff |
| GET, POST | `/staff/trek/<t_id>` | Manage assigned trek by status & Avilable Slots | Staff |
| GET, POST | `/staff/profile` | Manage & Update Profile | Staff |


### User's Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/user/user_dashboard` | User dashboard with Filter Searched Treks & Bookings | User |
| POST | `/user/treks/<t_id>/book_trek` | Book a Trek Slot | User |
| GET | `/user/<t_id>/treks` | View Booked Trek Details | User |
| POST | `/user/bookings/<b_id>/cancel_booking` | Cancel Booked Treks | User |
| GET | `/user/user_bookings` | View All Bookings | User |
| GET | `/user/history` | View All Completed Treks | User |
| GET, POST | `/user/profile` | Manage & Update Profile | User |


## 📁 Project File-Structure

```
Modern_Application__Development/
│
├── app.py                      # Application entry point
├── models.py                   # SQLAlchemy models
├── data.py                     # Demo data generator
│
├── routes/                     # Blueprint definitions
│   ├── __init__.py
│   ├── admin_routes.py
│   ├── auth_routes.py
│   ├── staff_routes.py
│   └── user_routes.py
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html
│   ├── mainpage.html
│   ├── admin/
│   ├── auth/
│   ├── staff/
│   └── user/
│
├── static/
│   └── css/style.css           # Custom Stylesheets
│
└── instance/                   # SQLite Database
```
