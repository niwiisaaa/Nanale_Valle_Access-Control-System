#˜”*°•.˜”*°• CS 319 - INFORMATION ASSURANCE AND SECURITY  | FINAL PROJECT •°*”˜"
#                NANALE, KRIZIA BELLE L. | VALLE, NERISA S.  |  BSCS -3A

from flask import Flask, render_template, redirect, url_for, flash, session, request
import os
import hashlib
from werkzeug.utils import secure_filename
import mysql.connector
from functools import wraps
import secrets
from datetime import timedelta

# ----------------- Application Configuration -----------------

# Initialize the Flask application
app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your-secret-key'

# File upload configurations
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  

# Set the session lifetime to 7 days
app.permanent_session_lifetime = timedelta(days=7)

# ----------------- Utility Functions -----------------
def admin_required(f):
    """
    A decorator to restrict access to routes only for admin users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'Admin':
            flash("Access denied. Admins only.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """
    A decorator to ensure the user is logged in before accessing a route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def connectSQL():
    """
    Establish a connection to the MySQL database.
    """
    try:
        return mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="access_control"
        )
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        raise

def encrypt(password):
    """Hash a password using plain SHA-256."""
    hash_obj = hashlib.sha256(password.encode())
    return hash_obj.hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a password against a plain SHA-256 hash."""
    provided_password_hash = encrypt(provided_password)
    print(f"Stored password: {stored_password}")  # Debugging log
    print(f"Provided password hash: {provided_password_hash}")  # Debugging log
    return provided_password_hash == stored_password


def allowed_file(filename):
    """Check if the file is of an allowed type."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- Application Routes -----------------
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Display the user's dashboard with their profile information.
    """
    user_id = session.get('user')
    try:
        conn = connectSQL()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT first_name, last_name, email, contact, address, profile_picture, role FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            return render_template('dashboard.html', user=user)
        else:
            flash("User not found.", "danger")
            return redirect(url_for('logout'))

    except Exception as e:
        flash("An error occurred while retrieving user data.", "danger")
        print(f"Dashboard Error: {e}")
        return redirect(url_for('logout'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Please provide both email and password.", "danger")
            return render_template('login.html')

        try:
            conn = connectSQL()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, password, role FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                if verify_password(user['password'], password):
                    # Set session variables
                    session['user'] = user['id']
                    session['role'] = user['role']
                    flash("Login successful!", "success")
                    return redirect(url_for('dashboard'))
                else:
                    flash("Password is incorrect.", "danger")
            else:
                flash("Email not found.", "danger")

        except mysql.connector.Error as e:
            flash(f"Database error: {str(e)}", "danger")
        except Exception as e:
            flash("An unexpected error occurred.", "danger")

    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    hashed_password = encrypt(password)  # Hash the password

    try:
        conn = connectSQL()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        flash("Registration successful!", "success")
    except Exception as e:
        flash("Error registering user.", "danger")
        print(f"Registration Error: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('login'))


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        contact = request.form.get('contact')
        address = request.form.get('address')
        profile_picture = request.files.get('profile_picture')

        hashed_password = encrypt(password)

        # Save the data into the database
        try:
            conn = connectSQL()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (first_name, last_name, username, email, password, role, contact, address, profile_picture)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, username, email, hashed_password, role, contact, address, profile_picture.filename if profile_picture else None))
            conn.commit()
            flash("User added successfully!", "success")
            return redirect(url_for('users'))
        except Exception as e:
            flash(f"Error adding user: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('add_user.html')


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    try:
        # Fetch the user's current data
        conn = connectSQL()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('users'))

        if request.method == 'POST':
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            contact = request.form.get('contact')
            address = request.form.get('address')
            role = request.form.get('role')
            profile_picture = request.files.get('profile_picture')

            if not first_name or not last_name or not email or not contact or not address or not role:
                flash("All fields are required.", "danger")
                return render_template('edit_user.html', user=user)

            # Validate and upload the new profile picture if provided
            picture_filename = user['profile_picture']  # Use existing picture by default
            if profile_picture and allowed_file(profile_picture.filename):
                if profile_picture.content_length > MAX_FILE_SIZE:
                    flash("File size too large.", "danger")
                    return render_template('edit_user.html', user=user)

                picture_filename = secure_filename(f"{first_name}_{profile_picture.filename}")
                profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], picture_filename))

            # Update user data in the database
            try:
                conn = connectSQL()
                cursor = conn.cursor()
                query = """
                    UPDATE users 
                    SET first_name = %s, last_name = %s, email = %s, contact = %s, address = %s, role = %s, profile_picture = %s
                    WHERE id = %s
                """
                cursor.execute(query, (first_name, last_name, email, contact, address, role, picture_filename, user_id))
                conn.commit()
                cursor.close()
                conn.close()

                flash("User updated successfully.", "success")
                return redirect(url_for('users'))

            except Exception as e:
                flash("Error updating user.", "danger")
                print(f"Edit User Error: {e}")

        return render_template('edit_user.html', user=user)

    except Exception as e:
        flash("Error retrieving user data.", "danger")
        print(f"Error: {e}")
        return redirect(url_for('users'))

@app.route('/users')
@admin_required
def users():
    try:
        conn = connectSQL()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, first_name, last_name, email, contact, address,  role FROM users"
        cursor.execute(query)
        users_list = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('users.html', users=users_list)

    except Exception as e:
        flash("Error retrieving user list.", "danger")
        print(f"Users Error: {e}")
        return redirect(url_for('dashboard'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    try:
        # Connect to the database
        conn = connectSQL()
        cursor = conn.cursor()

        # Query to delete the user from the database
        query = "DELETE FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash("User deleted successfully!", "success")
        return redirect(url_for('users'))

    except mysql.connector.Error as e:
        flash(f"MySQL Error: {str(e)}", "danger")
        print(f"MySQL Error: {e}")
        return redirect(url_for('users'))

    except Exception as e:
        flash("Error deleting user.", "danger")
        print(f"Error: {e}")
        return redirect(url_for('users'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user')
    try:
        conn = connectSQL()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            contact = request.form.get('contact')
            address = request.form.get('address')
            new_password = request.form.get('password')
            profile_picture = request.files.get('profile_picture')

            # Validate and process profile picture
            profile_picture_filename = user['profile_picture']
            if profile_picture and allowed_file(profile_picture.filename):
                if profile_picture.content_length > MAX_FILE_SIZE:
                    flash("File size too large. Max allowed is 5MB.", "danger")
                else:
                    profile_picture_filename = secure_filename(f"profile_{user_id}_{profile_picture.filename}")
                    profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_picture_filename))

            # Update database
            try:
                conn = connectSQL()
                cursor = conn.cursor()
                update_query = """
                    UPDATE users SET first_name = %s, last_name = %s, email = %s, contact = %s, address = %s,
                    profile_picture = %s WHERE id = %s
                """
                values = (first_name, last_name, email, contact, address, profile_picture_filename, user_id)

                if new_password:
                    password_hash = encrypt(new_password)
                    update_query = """
                        UPDATE users SET first_name = %s, last_name = %s, email = %s, contact = %s, address = %s,
                        profile_picture = %s, password = %s WHERE id = %s
                    """
                    values = (first_name, last_name, email, contact, address, profile_picture_filename, password_hash, user_id)

                cursor.execute(update_query, values)
                conn.commit()
                flash("Profile updated successfully.", "success")
            except Exception as e:
                flash("Error updating profile.", "danger")
                print(f"Profile Update Error: {e}")
            finally:
                cursor.close()
                conn.close()

        return render_template('profile.html', user=user)

    except Exception as e:
        flash("Error retrieving profile.", "danger")
        print(f"Profile Retrieval Error: {e}")
        return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)