"""
=============================================================
  LIBRARY MANAGEMENT SYSTEM - Main Application File
  Technology: Python (Flask) + SQLite + HTML/CSS/JS
  Author: B.Tech Final Year Project
  Description: A complete LMS with Admin Auth, Book & Member
               Management, Issue/Return System, Fine Calc,
               and a live Dashboard.
=============================================================
"""

import sqlite3
import os
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify)
from datetime import datetime, timedelta
import hashlib

# ── App Configuration ──────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'lms_secret_key_2024'   # Change in production
DATABASE = os.path.join(os.path.dirname(__file__), 'library.db')

# ── Database Helpers ───────────────────────────────────────
def get_db():
    """Open a database connection for the current request."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row   # allows dict-like access: row['column']
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password):
    """SHA-256 hash a password (use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """
    Create all tables and seed sample data if DB is fresh.
    Run once at startup.
    """
    conn = get_db()
    cur = conn.cursor()

    # ── Table: admin ─────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            name     TEXT    NOT NULL
        )
    """)

    # ── Table: books ─────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT    NOT NULL,
            author       TEXT    NOT NULL,
            category     TEXT    NOT NULL,
            isbn         TEXT    UNIQUE,
            publisher    TEXT,
            year         INTEGER,
            total_copies INTEGER NOT NULL DEFAULT 1,
            available    INTEGER NOT NULL DEFAULT 1,
            added_on     TEXT    DEFAULT (DATE('now'))
        )
    """)

    # ── Table: members ───────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            email      TEXT    UNIQUE,
            phone      TEXT,
            address    TEXT,
            member_type TEXT   DEFAULT 'Student',
            joined_on  TEXT    DEFAULT (DATE('now')),
            active     INTEGER DEFAULT 1
        )
    """)

    # ── Table: issued_books ──────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS issued_books (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id     INTEGER NOT NULL REFERENCES books(id),
            member_id   INTEGER NOT NULL REFERENCES members(id),
            issue_date  TEXT    NOT NULL DEFAULT (DATE('now')),
            due_date    TEXT    NOT NULL,
            return_date TEXT,
            fine        REAL    DEFAULT 0,
            status      TEXT    DEFAULT 'Issued'
        )
    """)

    # ── Seed: default admin ───────────────────────────────
    cur.execute("SELECT COUNT(*) FROM admin")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO admin (username, password, name) VALUES (?,?,?)",
            ('admin', hash_password('admin123'), 'Library Administrator')
        )

    # ── Seed: sample books ────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM books")
    if cur.fetchone()[0] == 0:
        sample_books = [
            ('Data Structures & Algorithms', 'Thomas H. Cormen',   'Computer Science', '978-0262046305', 'MIT Press',       2022, 5, 5),
            ('Clean Code',                  'Robert C. Martin',    'Computer Science', '978-0132350884', 'Prentice Hall',   2008, 3, 3),
            ('The Pragmatic Programmer',    'Andrew Hunt',         'Computer Science', '978-0135957059', 'Addison-Wesley',  2019, 4, 4),
            ('Introduction to Python',      'Mark Lutz',           'Programming',      '978-1449355739', "O'Reilly",        2013, 6, 6),
            ('Database Management Systems', 'Raghu Ramakrishnan',  'Database',         '978-0072465631', 'McGraw-Hill',     2002, 3, 3),
            ('Operating System Concepts',   'Abraham Silberschatz','Computer Science', '978-1119800361', 'Wiley',           2021, 4, 4),
            ('Computer Networks',           'Andrew S. Tanenbaum', 'Networking',       '978-0133499452', 'Pearson',         2010, 3, 3),
            ('Artificial Intelligence',     'Stuart Russell',      'AI/ML',            '978-0134610993', 'Pearson',         2020, 5, 5),
            ('Machine Learning',            'Tom M. Mitchell',     'AI/ML',            '978-0070428072', 'McGraw-Hill',     1997, 2, 2),
            ('The Art of War',             'Sun Tzu',             'Philosophy',        '978-1599869773', 'Filiquarian',     2007, 3, 3),
            ('Wings of Fire',              'APJ Abdul Kalam',     'Biography',         '978-8173711466', 'Universities Press',2015, 4, 4),
            ('Rich Dad Poor Dad',          'Robert Kiyosaki',     'Finance',           '978-1612680194', 'Plata Publishing',2017, 3, 3),
        ]
        cur.executemany(
            "INSERT INTO books (title,author,category,isbn,publisher,year,total_copies,available) VALUES (?,?,?,?,?,?,?,?)",
            sample_books
        )

    # ── Seed: sample members ──────────────────────────────
    cur.execute("SELECT COUNT(*) FROM members")
    if cur.fetchone()[0] == 0:
        sample_members = [
            ('Aarav Sharma',   'aarav@example.com',   '9876543210', 'Lucknow, UP',    'Student'),
            ('Priya Verma',    'priya@example.com',   '9123456780', 'Varanasi, UP',   'Student'),
            ('Rahul Gupta',    'rahul@example.com',   '9988776655', 'Gorakhpur, UP',  'Student'),
            ('Sneha Patel',    'sneha@example.com',   '9012345678', 'Agra, UP',       'Student'),
            ('Vikram Singh',   'vikram@example.com',  '9876012345', 'Kanpur, UP',     'Faculty'),
            ('Anjali Mishra',  'anjali@example.com',  '9765432109', 'Allahabad, UP',  'Faculty'),
            ('Mohit Yadav',    'mohit@example.com',   '9654321098', 'Meerut, UP',     'Student'),
            ('Kavita Tiwari',  'kavita@example.com',  '9543210987', 'Bareilly, UP',   'Student'),
        ]
        cur.executemany(
            "INSERT INTO members (name,email,phone,address,member_type) VALUES (?,?,?,?,?)",
            sample_members
        )

    # ── Seed: a few issued books (some overdue for fine demo) ──
    cur.execute("SELECT COUNT(*) FROM issued_books")
    if cur.fetchone()[0] == 0:
        today = datetime.today()
        sample_issues = [
            (1, 1, (today - timedelta(days=10)).strftime('%Y-%m-%d'),
                   (today - timedelta(days=3)).strftime('%Y-%m-%d'),  None, 0,  'Issued'),
            (2, 2, (today - timedelta(days=20)).strftime('%Y-%m-%d'),
                   (today - timedelta(days=6)).strftime('%Y-%m-%d'),  None, 0,  'Issued'),
            (3, 3, (today - timedelta(days=5)).strftime('%Y-%m-%d'),
                   (today + timedelta(days=9)).strftime('%Y-%m-%d'),  None, 0,  'Issued'),
            (4, 4, (today - timedelta(days=30)).strftime('%Y-%m-%d'),
                   (today - timedelta(days=16)).strftime('%Y-%m-%d'),
                   (today - timedelta(days=10)).strftime('%Y-%m-%d'),  30, 'Returned'),
        ]
        cur.executemany(
            "INSERT INTO issued_books (book_id,member_id,issue_date,due_date,return_date,fine,status) VALUES (?,?,?,?,?,?,?)",
            sample_issues
        )
        # Fix available counts after seeding issued books
        cur.execute("UPDATE books SET available = available - 1 WHERE id IN (1,2,3)")

    conn.commit()
    conn.close()

# ── Auth Decorator ─────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ══════════════════════════════════════════════════════════
#  AUTH ROUTES
# ══════════════════════════════════════════════════════════

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if 'admin_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = hash_password(request.form['password'])
        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()
        if admin:
            session['admin_id']   = admin['id']
            session['admin_name'] = admin['name']
            flash(f"Welcome back, {admin['name']}!", 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ══════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with statistics."""
    conn = get_db()
    today = datetime.today().strftime('%Y-%m-%d')

    stats = {
        'total_books':   conn.execute("SELECT COUNT(*) FROM books").fetchone()[0],
        'total_members': conn.execute("SELECT COUNT(*) FROM members WHERE active=1").fetchone()[0],
        'issued_books':  conn.execute("SELECT COUNT(*) FROM issued_books WHERE status='Issued'").fetchone()[0],
        'overdue_books': conn.execute(
            "SELECT COUNT(*) FROM issued_books WHERE status='Issued' AND due_date < ?", (today,)
        ).fetchone()[0],
        'total_fine':    conn.execute(
            "SELECT COALESCE(SUM(fine),0) FROM issued_books WHERE status='Returned'"
        ).fetchone()[0],
        'available_books': conn.execute("SELECT COALESCE(SUM(available),0) FROM books").fetchone()[0],
    }

    # Recent activity (last 5 issues)
    recent = conn.execute("""
        SELECT ib.id, b.title, m.name AS member_name,
               ib.issue_date, ib.due_date, ib.status,
               CASE WHEN ib.due_date < DATE('now') AND ib.status='Issued'
                    THEN 1 ELSE 0 END AS is_overdue
        FROM issued_books ib
        JOIN books b   ON ib.book_id   = b.id
        JOIN members m ON ib.member_id = m.id
        ORDER BY ib.id DESC LIMIT 8
    """).fetchall()

    # Category breakdown for chart
    categories = conn.execute("""
        SELECT category, COUNT(*) as cnt FROM books GROUP BY category
    """).fetchall()

    conn.close()
    return render_template('dashboard.html', stats=stats, recent=recent, categories=categories)

# ══════════════════════════════════════════════════════════
#  BOOK MANAGEMENT
# ══════════════════════════════════════════════════════════

@app.route('/books')
@login_required
def books():
    """List all books with optional search."""
    q        = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    conn     = get_db()

    query  = "SELECT * FROM books WHERE 1=1"
    params = []
    if q:
        query  += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)"
        params += [f'%{q}%', f'%{q}%', f'%{q}%']
    if category:
        query  += " AND category = ?"
        params.append(category)
    query += " ORDER BY title"

    all_books  = conn.execute(query, params).fetchall()
    categories = conn.execute("SELECT DISTINCT category FROM books ORDER BY category").fetchall()
    conn.close()
    return render_template('books.html', books=all_books, categories=categories,
                           search=q, selected_cat=category)

@app.route('/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        data = request.form
        conn = get_db()
        copies = int(data.get('total_copies', 1))
        conn.execute("""
            INSERT INTO books (title,author,category,isbn,publisher,year,total_copies,available)
            VALUES (?,?,?,?,?,?,?,?)
        """, (data['title'], data['author'], data['category'],
              data.get('isbn'), data.get('publisher'), data.get('year'), copies, copies))
        conn.commit(); conn.close()
        flash('Book added successfully!', 'success')
        return redirect(url_for('books'))
    return render_template('book_form.html', book=None, action='Add')

@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    if not book:
        conn.close(); flash('Book not found.', 'danger'); return redirect(url_for('books'))

    if request.method == 'POST':
        data = request.form
        diff = int(data['total_copies']) - book['total_copies']
        conn.execute("""
            UPDATE books SET title=?,author=?,category=?,isbn=?,publisher=?,year=?,
            total_copies=?, available=available+? WHERE id=?
        """, (data['title'], data['author'], data['category'], data.get('isbn'),
              data.get('publisher'), data.get('year'), data['total_copies'], diff, book_id))
        conn.commit(); conn.close()
        flash('Book updated!', 'success')
        return redirect(url_for('books'))

    conn.close()
    return render_template('book_form.html', book=book, action='Edit')

@app.route('/books/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    conn = get_db()
    issued = conn.execute(
        "SELECT COUNT(*) FROM issued_books WHERE book_id=? AND status='Issued'", (book_id,)
    ).fetchone()[0]
    if issued:
        flash('Cannot delete: book is currently issued.', 'danger')
    else:
        conn.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
        flash('Book deleted.', 'success')
    conn.close()
    return redirect(url_for('books'))

# ══════════════════════════════════════════════════════════
#  MEMBER MANAGEMENT
# ══════════════════════════════════════════════════════════

@app.route('/members')
@login_required
def members():
    q    = request.args.get('q', '').strip()
    conn = get_db()
    if q:
        all_members = conn.execute(
            "SELECT * FROM members WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? ORDER BY name",
            (f'%{q}%', f'%{q}%', f'%{q}%')
        ).fetchall()
    else:
        all_members = conn.execute("SELECT * FROM members ORDER BY name").fetchall()
    conn.close()
    return render_template('members.html', members=all_members, search=q)

@app.route('/members/add', methods=['GET', 'POST'])
@login_required
def add_member():
    if request.method == 'POST':
        data = request.form
        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO members (name,email,phone,address,member_type)
                VALUES (?,?,?,?,?)
            """, (data['name'], data.get('email'), data.get('phone'),
                  data.get('address'), data.get('member_type','Student')))
            conn.commit()
            flash('Member added!', 'success')
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'danger')
        finally:
            conn.close()
        return redirect(url_for('members'))
    return render_template('member_form.html', member=None, action='Add')

@app.route('/members/edit/<int:member_id>', methods=['GET', 'POST'])
@login_required
def edit_member(member_id):
    conn   = get_db()
    member = conn.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
    if not member:
        conn.close(); flash('Member not found.', 'danger'); return redirect(url_for('members'))

    if request.method == 'POST':
        data = request.form
        conn.execute("""
            UPDATE members SET name=?,email=?,phone=?,address=?,member_type=?,active=?
            WHERE id=?
        """, (data['name'], data.get('email'), data.get('phone'), data.get('address'),
              data.get('member_type','Student'), data.get('active',1), member_id))
        conn.commit(); conn.close()
        flash('Member updated!', 'success')
        return redirect(url_for('members'))

    conn.close()
    return render_template('member_form.html', member=member, action='Edit')

@app.route('/members/delete/<int:member_id>', methods=['POST'])
@login_required
def delete_member(member_id):
    conn = get_db()
    issued = conn.execute(
        "SELECT COUNT(*) FROM issued_books WHERE member_id=? AND status='Issued'", (member_id,)
    ).fetchone()[0]
    if issued:
        flash('Cannot delete: member has books pending return.', 'danger')
    else:
        conn.execute("DELETE FROM members WHERE id=?", (member_id,))
        conn.commit()
        flash('Member deleted.', 'success')
    conn.close()
    return redirect(url_for('members'))

# ══════════════════════════════════════════════════════════
#  ISSUE BOOK
# ══════════════════════════════════════════════════════════

@app.route('/issue', methods=['GET', 'POST'])
@login_required
def issue_book():
    conn    = get_db()
    books_  = conn.execute("SELECT * FROM books WHERE available > 0 ORDER BY title").fetchall()
    members_= conn.execute("SELECT * FROM members WHERE active=1 ORDER BY name").fetchall()

    if request.method == 'POST':
        book_id   = request.form['book_id']
        member_id = request.form['member_id']
        issue_date= request.form.get('issue_date', datetime.today().strftime('%Y-%m-%d'))
        due_date  = request.form.get('due_date',
                    (datetime.strptime(issue_date,'%Y-%m-%d') + timedelta(days=14)).strftime('%Y-%m-%d'))

        # Availability check
        avail = conn.execute("SELECT available FROM books WHERE id=?", (book_id,)).fetchone()
        if not avail or avail['available'] < 1:
            flash('Book not available.', 'danger')
        else:
            conn.execute("""
                INSERT INTO issued_books (book_id,member_id,issue_date,due_date,status)
                VALUES (?,?,?,?,'Issued')
            """, (book_id, member_id, issue_date, due_date))
            conn.execute("UPDATE books SET available = available - 1 WHERE id=?", (book_id,))
            conn.commit()
            flash('Book issued successfully!', 'success')
            conn.close()
            return redirect(url_for('issued_list'))

    conn.close()
    return render_template('issue.html', books=books_, members=members_,
                           today=datetime.today().strftime('%Y-%m-%d'),
                           default_due=(datetime.today()+timedelta(days=14)).strftime('%Y-%m-%d'))

# ══════════════════════════════════════════════════════════
#  ISSUED BOOKS LIST
# ══════════════════════════════════════════════════════════

@app.route('/issued')
@login_required
def issued_list():
    conn  = get_db()
    today = datetime.today().strftime('%Y-%m-%d')
    rows  = conn.execute("""
        SELECT ib.*, b.title, b.author, m.name AS member_name, m.phone,
               CASE WHEN ib.due_date < DATE('now') AND ib.status='Issued'
                    THEN CAST(JULIANDAY(DATE('now')) - JULIANDAY(ib.due_date) AS INTEGER)
                    ELSE 0 END AS days_overdue
        FROM issued_books ib
        JOIN books b   ON ib.book_id   = b.id
        JOIN members m ON ib.member_id = m.id
        ORDER BY ib.id DESC
    """).fetchall()
    conn.close()
    return render_template('issued.html', records=rows, today=today)

# ══════════════════════════════════════════════════════════
#  RETURN BOOK
# ══════════════════════════════════════════════════════════

FINE_PER_DAY = 5   # ₹5 per day after due date

@app.route('/return/<int:issue_id>', methods=['GET', 'POST'])
@login_required
def return_book(issue_id):
    conn   = get_db()
    record = conn.execute("""
        SELECT ib.*, b.title, b.author, m.name AS member_name
        FROM issued_books ib
        JOIN books b   ON ib.book_id   = b.id
        JOIN members m ON ib.member_id = m.id
        WHERE ib.id=? AND ib.status='Issued'
    """, (issue_id,)).fetchone()

    if not record:
        conn.close()
        flash('Record not found or already returned.', 'danger')
        return redirect(url_for('issued_list'))

    today      = datetime.today().strftime('%Y-%m-%d')
    due_date   = datetime.strptime(record['due_date'], '%Y-%m-%d')
    return_date= datetime.today()
    days_late  = (return_date - due_date).days
    fine       = max(0, days_late) * FINE_PER_DAY   # ₹5/day

    if request.method == 'POST':
        actual_return = request.form.get('return_date', today)
        actual_due    = datetime.strptime(record['due_date'], '%Y-%m-%d')
        actual_ret    = datetime.strptime(actual_return, '%Y-%m-%d')
        late_days     = (actual_ret - actual_due).days
        actual_fine   = max(0, late_days) * FINE_PER_DAY

        conn.execute("""
            UPDATE issued_books
            SET return_date=?, fine=?, status='Returned'
            WHERE id=?
        """, (actual_return, actual_fine, issue_id))
        conn.execute("UPDATE books SET available = available + 1 WHERE id=?", (record['book_id'],))
        conn.commit(); conn.close()
        flash(f'Book returned! Fine collected: ₹{actual_fine}', 'success')
        return redirect(url_for('issued_list'))

    conn.close()
    return render_template('return.html', record=record, fine=fine,
                           today=today, days_late=max(0, days_late))

# ══════════════════════════════════════════════════════════
#  API ENDPOINT – AJAX SEARCH
# ══════════════════════════════════════════════════════════

@app.route('/api/books/search')
@login_required
def api_search_books():
    q    = request.args.get('q', '')
    conn = get_db()
    rows = conn.execute("""
        SELECT id, title, author, category, available
        FROM books WHERE (title LIKE ? OR author LIKE ?) AND available > 0
        LIMIT 10
    """, (f'%{q}%', f'%{q}%')).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/members/search')
@login_required
def api_search_members():
    q    = request.args.get('q', '')
    conn = get_db()
    rows = conn.execute("""
        SELECT id, name, email, phone FROM members
        WHERE (name LIKE ? OR email LIKE ?) AND active=1
        LIMIT 10
    """, (f'%{q}%', f'%{q}%')).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ══════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════

if __name__ == '__main__':
    init_db()
    print("\n" + "="*55)
    print("  📚 Library Management System  –  Starting...")
    print("="*55)
    print("  URL     : http://127.0.0.1:5000")
    print("  Username: admin")
    print("  Password: admin123")
    print("="*55 + "\n")
    app.run(debug=True)
