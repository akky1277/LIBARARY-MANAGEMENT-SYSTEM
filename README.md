#  Library Management System (LMS)
> B.Tech Final Year Project | Python Flask + SQLite + HTML/CSS/JS

---

##  Project Structure

```
library_lms/
├── app.py              ← Main Flask application (all routes + logic)
├── schema.sql          ← SQL schema + sample data reference
├── library.db          ← SQLite database (auto-created on first run)
├── requirements.txt    ← Python dependencies
├── README.md           ← This file
└── templates/
    ├── base.html       ← Shared layout with sidebar navigation
    ├── login.html      ← Admin login page
    ├── dashboard.html  ← Stats + recent activity
    ├── books.html      ← Book catalogue with search
    ├── book_form.html  ← Add / Edit book form
    ├── members.html    ← Member directory with search
    ├── member_form.html← Add / Edit member form
    ├── issue.html      ← Issue book (AJAX live search)
    ├── issued.html     ← All issue records
    └── return.html     ← Return book + fine preview
```

---

##  Quick Start

### 1. Install Python (3.8+)
Download from https://python.org

### 2. Install Flask
```bash
pip install flask
```

### 3. Run the Application
```bash
cd library_lms
python app.py
```

### 4. Open Browser
Visit → **http://127.0.0.1:5000**

### 5. Login
| Field    | Value      |
|----------|-----------|
| Username | `admin`   |
| Password | `admin123`|

The database (`library.db`) is created automatically with sample data.

---

##  Features

| Feature              | Details                                    |
|---------------------|--------------------------------------------|
| **Auth**            | Admin login/logout, SHA-256 password hash  |
| **Books**           | Add, Edit, Delete, Search by title/author/category |
| **Members**         | Add, Edit, Delete, Search                  |
| **Issue Books**     | AJAX live search, auto due-date (14 days)  |
| **Return Books**    | Live fine preview, updates availability    |
| **Fine Calculation**| ₹5/day after due date, auto-calculated     |
| **Dashboard**       | 6 stat cards + recent activity + category chart |

---

##  Database Tables

| Table          | Purpose                              |
|----------------|--------------------------------------|
| `admin`        | Admin credentials                    |
| `books`        | Book catalogue                       |
| `members`      | Library members                      |
| `issued_books` | Issue/return transactions            |

---

##  Advanced Features to Add (Future Scope)

1. **Barcode Scanning** – Use `python-barcode` or `pyzbar` + webcam
2. **Email Notifications** – `Flask-Mail` for overdue reminders
3. **Analytics Dashboard** – Charts with Chart.js or Plotly
4. **PDF Reports** – Export with `ReportLab` or `WeasyPrint`
5. **Multi-admin** – Role-based access (Super Admin / Staff)
6. **Book Reservations** – Reserve before availability
7. **QR Code Generation** – Auto-generate QR for each book
8. **SMS Alerts** – Twilio API for due-date reminders
9. **REST API** – Expose endpoints for mobile app
10. **Docker Deployment** – Containerize for production

---

##  Layout Description (Screenshots)

### Login Page
- Dark background with golden grid
- Centered card with logo icon
- Username + password fields
- Demo credentials hint

### Dashboard
- Left sidebar with navigation links
- 6 stat cards: Books, Members, Issued, Overdue, Fine, Quick Add
- Recent activity table (last 8 transactions)
- Category bar chart on the right

### Books Page
- Search bar (title/author/ISBN) + category filter
- Sortable table with ISBN, copies, availability badges
- Edit (pencil) + Delete (trash) buttons per row

### Issue Book Page
- Live AJAX search for books (type → dropdown)
- Live AJAX search for members
- Auto-calculates 14-day due date
- Fallback dropdown selects

### Return Book Page
- Shows all issue details
- Red fine box if overdue (updates live when date changes)
- Confirm return button

---

##  Tech Stack

- **Backend**: Python 3.x + Flask 3.x
- **Database**: SQLite (built-in, no setup needed)
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Icons**: Font Awesome 6
- **Fonts**: Google Fonts (Playfair Display + DM Sans)
- **Password**: SHA-256 hashing (use bcrypt in production)
