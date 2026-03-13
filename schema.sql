-- ================================================================
--  LIBRARY MANAGEMENT SYSTEM – Database Schema (SQLite / MySQL)
--  For B.Tech Final Year Project
-- ================================================================

-- ── Table 1: admin ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS admin (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    NOT NULL UNIQUE,
    password TEXT    NOT NULL,         -- SHA-256 hashed password
    name     TEXT    NOT NULL
);

-- ── Table 2: books ─────────────────────────────────────────────
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
);

-- ── Table 3: members ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS members (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    UNIQUE,
    phone       TEXT,
    address     TEXT,
    member_type TEXT    DEFAULT 'Student',   -- Student | Faculty | Staff | External
    joined_on   TEXT    DEFAULT (DATE('now')),
    active      INTEGER DEFAULT 1            -- 1 = active, 0 = inactive
);

-- ── Table 4: issued_books ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS issued_books (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id     INTEGER NOT NULL REFERENCES books(id),
    member_id   INTEGER NOT NULL REFERENCES members(id),
    issue_date  TEXT    NOT NULL DEFAULT (DATE('now')),
    due_date    TEXT    NOT NULL,            -- typically issue_date + 14 days
    return_date TEXT,                        -- NULL if not returned
    fine        REAL    DEFAULT 0,           -- ₹5 per day after due_date
    status      TEXT    DEFAULT 'Issued'     -- 'Issued' | 'Returned'
);

-- ── Sample Data ────────────────────────────────────────────────

-- Admin (password: admin123)
INSERT INTO admin (username, password, name) VALUES
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831d9a0bfce9ea7748a3e31f5', 'Library Administrator');

-- Sample Books
INSERT INTO books (title, author, category, isbn, publisher, year, total_copies, available) VALUES
('Data Structures & Algorithms', 'Thomas H. Cormen',   'Computer Science', '978-0262046305', 'MIT Press',      2022, 5, 5),
('Clean Code',                  'Robert C. Martin',    'Computer Science', '978-0132350884', 'Prentice Hall',  2008, 3, 3),
('Introduction to Python',      'Mark Lutz',           'Programming',      '978-1449355739', 'O Reilly',       2013, 6, 6),
('Database Management Systems', 'Raghu Ramakrishnan',  'Database',         '978-0072465631', 'McGraw-Hill',    2002, 3, 3),
('Artificial Intelligence',     'Stuart Russell',      'AI/ML',            '978-0134610993', 'Pearson',        2020, 5, 5);

-- Sample Members
INSERT INTO members (name, email, phone, address, member_type) VALUES
('Aarav Sharma',  'aarav@example.com',  '9876543210', 'Lucknow, UP',   'Student'),
('Priya Verma',   'priya@example.com',  '9123456780', 'Varanasi, UP',  'Student'),
('Vikram Singh',  'vikram@example.com', '9876012345', 'Kanpur, UP',    'Faculty');

-- ── Useful Queries ─────────────────────────────────────────────

-- All currently issued books with member & book details
SELECT ib.id, b.title, b.author, m.name AS member, m.phone,
       ib.issue_date, ib.due_date, ib.status,
       CASE WHEN ib.due_date < DATE('now') AND ib.status='Issued'
            THEN CAST(JULIANDAY(DATE('now')) - JULIANDAY(ib.due_date) AS INTEGER)
            ELSE 0 END AS days_overdue
FROM issued_books ib
JOIN books b   ON ib.book_id   = b.id
JOIN members m ON ib.member_id = m.id
WHERE ib.status = 'Issued';

-- Dashboard statistics
SELECT
  (SELECT COUNT(*) FROM books)                                        AS total_books,
  (SELECT COUNT(*) FROM members WHERE active=1)                       AS total_members,
  (SELECT COUNT(*) FROM issued_books WHERE status='Issued')           AS books_issued,
  (SELECT COUNT(*) FROM issued_books WHERE status='Issued' AND due_date < DATE('now')) AS overdue,
  (SELECT COALESCE(SUM(fine),0) FROM issued_books WHERE status='Returned') AS fine_collected;
