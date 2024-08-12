from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

# Initialize the SQLite database
def init_db():
    with sqlite3.connect('contacts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        ''')
        conn.commit()

# Function to fetch all contacts from the database
def fetch_contacts():
    with sqlite3.connect('contacts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, email FROM contacts')
        return cursor.fetchall()

# Function to add a new contact to the database
def add_contact(name, email):
    try:
        with sqlite3.connect('contacts.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO contacts (name, email) VALUES (?, ?)', (name, email))
            conn.commit()
            return True
    except sqlite3.IntegrityError:  # This will catch unique constraint violations (duplicate emails)
        return False
@app.route('/')
def index():
    init_db()  # Ensure the DB and table are created
    contacts = fetch_contacts()
    return render_template_string(open('index.html').read(), contacts=render_contacts())

@app.route('/contacts', methods=['POST'])
def add_contact_route():
    name = request.form.get('name')  # Get name from form
    email = request.form.get('email')  # Get email from form

    if add_contact(name, email):
        return render_contacts()  # Return updated contacts
    else:
        return jsonify({"error": "The email is already taken."}), 400

@app.route('/contacts/table')
def render_contacts():
    contacts = fetch_contacts()
    contact_rows = ''.join([f"<tr><td>{c[0]}</td><td>{c[1]}</td></tr>" for c in contacts])
    return contact_rows

@app.route('/contacts/email', methods=['POST'])
def validate_email():
    email = request.form.get('email')
    error_msg = ''

    # Simple email validation
    if not email or '@' not in email:
        error_msg = "Please enter a valid email address."
    
    # Check for existing emails in the database
    elif email_in_db(email):
        error_msg = "That email is already taken. Please enter another email."

    return f"""
    <div hx-target="this" hx-swap="outerHTML" class="{('error' if error_msg else 'valid')}">
        <label>Email Address</label>
        <input name="email" required hx-post="/contacts/email" value="{email}">
        <div class="htmx-indicator"></div>
        {"<div class='error-message'>{error_msg}</div>" if error_msg else ""}
    </div>
    """

# Function to check if email exists in the database
def email_in_db(email):
    with sqlite3.connect('contacts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM contacts WHERE email = ?', (email,))
        return cursor.fetchone() is not None

# Start the server
if __name__ == '__main__':
    app.run(debug=True)
