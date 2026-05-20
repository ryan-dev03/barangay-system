# Barangay Management System

A web-based barangay management system built with **Flask** and **MySQL** that allows residents to submit requests, complaints, and emergency reports through QR code-linked unit pages, with an admin dashboard for monitoring and status management.

---

## Features

### Member (Resident) Portal
- **QR Code Access** - Each house unit has a unique QR code that links directly to its login/registration page
- **Registration & Login** - Residents register and log in under their assigned house unit
- **File Requests** - Submit requests for barangay documents (e.g., barangay clearance, certificates) with a delivery address
- **Complaints** - File complaints by type with a description
- **Emergency Reports** - Report emergencies with type, description, location, and contact number
- **My Submissions** - View a personal history of all submitted requests, complaints, and emergencies with their statuses

### Admin Portal
- **Secure Login** - Admin-only access to the dashboard
- **Dashboard** - View all file requests, complaints, and emergencies grouped by house unit
- **Status Management** - Update the status of any submission (e.g., pending → resolved)
- **QR Codes Page** - Access generated QR codes for each house unit

---

## Tech Stack

| Layer      | Technology                         |
|------------|------------------------------------|
| Backend    | Python, Flask                      |
| Database   | MySQL (via `flask-mysqldb`)        |
| Auth       | Werkzeug password hashing          |
| Frontend   | HTML, CSS (Jinja2 templates)       |
| QR Codes   | `qr_gen.py` (QR code generation)  |

---

## Project Structure

```
barangay-system/
├── app.py               # Main Flask application and all route definitions
├── qr_gen.py            # QR code generation script for house units
├── requirements.txt     # Python dependencies
├── static/              # Static assets (CSS, images, QR code files)
└── templates/
    ├── admin/
    │   ├── login.html
    │   ├── dashboard.html
    │   └── qrcodes.html
    └── member/
        ├── login.html
        ├── register.html
        ├── home.html
        ├── request_file.html
        ├── complaint.html
        ├── emergency.html
        └── my_submissions.html
```

---

## Database Schema

The application expects a MySQL database named `barangay_db` with the following tables:

- **`admins`** - Admin accounts (`id`, `username`, `password`)
- **`house_units`** - Registered house units (`id`, `unit_number`)
- **`members`** - Resident accounts (`id`, `house_unit_id`, `full_name`, `username`, `password_hash`)
- **`file_requests`** - Document requests (`id`, `member_id`, `file_type`, `details`, `delivery_address`, `status`, `created_at`)
- **`complaints`** - Resident complaints (`id`, `member_id`, `complaint_type`, `description`, `status`, `created_at`)
- **`emergencies`** - Emergency reports (`id`, `member_id`, `emergency_type`, `description`, `location`, `contact_number`, `status`, `created_at`)

---

## Getting Started

### Prerequisites

- Python 3.8+
- MySQL Server
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ryan-dev03/barangay-system.git
   cd barangay-system
   ```

2. **Install dependencies**
   ```bash
   pip install flask flask-mysqldb werkzeug qrcode
   ```

3. **Set up the database**

   Create the MySQL database and user:
   ```sql
   CREATE DATABASE barangay_db;
   CREATE USER 'brgy_user'@'localhost' IDENTIFIED BY 'gchbarangay';
   GRANT ALL PRIVILEGES ON barangay_db.* TO 'brgy_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

   Then create the required tables (see [Database Schema](#database-schema) above).

4. **Configure the app** *(optional)*

   Database credentials are set directly in `app.py`. Update these if your setup differs:
   ```python
   app.config['MYSQL_HOST'] = 'localhost'
   app.config['MYSQL_USER'] = 'brgy_user'
   app.config['MYSQL_PASSWORD'] = 'gchbarangay'
   app.config['MYSQL_DB'] = 'barangay_db'
   ```
   > ⚠️ For production, move credentials to environment variables or a config file.

5. **Generate QR codes for house units**
   ```bash
   python qr_gen.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

   The app will be available at `http://localhost:5000`.

---

## Usage

### Accessing a Resident Portal

Each house unit has a URL in the format:
```
http://<host>:5000/unit/<unit_number>
```
Scanning the unit's QR code will redirect to this URL. Residents can then register or log in.

### Admin Login

Navigate to:
```
http://<host>:5000/admin
```

---

## Routes Overview

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/unit/<unit_number>` | Redirect to member login for that unit |
| GET/POST | `/login/<unit>` | Member login |
| GET/POST | `/register/<unit>` | Member registration |
| GET | `/home` | Member home page |
| GET/POST | `/request-file` | Submit a document request |
| GET/POST | `/complaint` | Submit a complaint |
| GET/POST | `/emergency` | Submit an emergency report |
| GET | `/member/my-submissions` | View member's submission history |
| GET/POST | `/admin` | Admin login |
| GET | `/admin/dashboard` | Admin dashboard |
| POST | `/admin/update-status` | Update submission status |
| GET | `/admin/qrcodes` | View QR codes |
| GET | `/admin/logout` | Admin logout |
| GET | `/logout` | Member logout |

---

## Security Notes

- Member passwords are stored as hashed values using Werkzeug's `generate_password_hash`.
- Admin passwords are currently stored in plaintext in the database — it is recommended to hash these as well before deploying to production.
- The `app.secret_key` should be replaced with a strong, randomly generated key in production.

---

---

## 👥 Meet the Team

| Name | Role |
|---|---|
| Ardales, Rose Gabrielle M. | System Tester |
| Dela Rosa, Ryan | Lead Developer |
| Destacamento, Justin Ethan M. | Github Manager |
| Encarnation, Danica Noelle D. | Co-Designer |
| Sales, Karyn Alyssa S. | Project Lead |
| Sanchez, Shin Chelsy B. | UI/UX Designer |

**Instructor:** Engr. Kurt Cydrick A. Atienza

---

## 📄 License

This project was developed for academic purposes as part of CpEE 401.
This project is open source. Feel free to fork and adapt for your barangay's needs.
