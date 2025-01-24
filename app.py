import numpy as np
from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response
import pickle
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
import string
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create Flask app
flask_app = Flask(__name__)
flask_app.secret_key = os.getenv('FLASK_SECRET_KEY', "my_secret_key")  # Use environment variable

# Load model
model_path = "model. pkl"
if os.path.exists(model_path):
    model = pickle.load(open(model_path, "rb"))
else:
    raise FileNotFoundError(f"Model file not found at {model_path}")


DATABASE = {
    'database': os.getenv('DB_NAME', 'db_name'),
    'user': os.getenv('DB_USER', 'db_user'),
    'password': os.getenv('DB_PASSWORD', 'db_password'),
    'host': os.getenv('DB_HOST', 'db_host'),
    'port': os.getenv('DB_PORT', 'db_port')
}


def get_db_connection():
    try:
        connection = psycopg2.connect(**DATABASE)
        return connection
    except psycopg2.Error as e:
        flash(f"Database connection error: {e}", "error")
        return None


app = Flask(__name__)
# Secret key for session management
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'my_secret_key')

# SMTP email configuration
sender_email = os.getenv("Mail_Username")
receiver_email = os.getenv("MAIL_DEFAULT_SENDER")
sender_password = os.getenv("Mail_Secret_key")


@flask_app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username_or_email = request.form.get("usernameOrEmail")
        password = request.form.get("loginPassword")

        connection = get_db_connection()
        if connection:
            with connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, username, password FROM users 
                        WHERE username = %s OR email = %s
                    """, (username_or_email, username_or_email))
                    user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session["user_id"] = user['id']
                session["username"] = user['username']
                flash(f"Welcome, {user['username']}!", "success")
                return redirect(url_for("home"))
            else:
                flash("Invalid username/email or password", "error")
        else:
            flash("Could not connect to the database.", "error")
        return redirect(url_for("index"))

    return render_template("index.html")


def generate_reset_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))


# Route to display the forgot password page
@flask_app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Check if the email exists in the database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            reset_token = generate_reset_token()  # Generate the reset token

            # Store the reset token in the database
            cursor.execute("UPDATE users SET reset_token = %s WHERE email = %s", (reset_token, email))
            connection.commit()

            # Send the password reset email
            reset_link = url_for('reset_password', token=reset_token, _external=True)
            send_reset_email(email, reset_link)

            flash('A password reset link has been sent to your email address.', 'success')
            return redirect(url_for('forgot_password'))
        else:
            flash('Email address not found in our system.', 'danger')

    return render_template('forgot_password.html')


def send_reset_email(to_email, reset_link):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = "Password Reset Request"
    msg.attach(MIMEText(f'Click on the link below to reset your password:\n\n{reset_link}', 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")


@flask_app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE reset_token = %s", (token,))
    user = cursor.fetchone()

    if not user:
        flash('Invalid or expired reset token.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']  # Ensure this matches the HTML form field name
        hashed_password = generate_password_hash(new_password)

# Check if passwords match
        if new_password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("reset_password", token=token))

        # Password validation
        if new_password and not is_password_strong(new_password):
            flash(
                "Password must be at least 8 characters long, contain a lowercase letter, an uppercase letter, a number, and a special character.",
                "danger")
            return redirect(url_for("reset_password", token=token))

        # Hash the new password and update the database
        hashed_password = generate_password_hash(new_password)

        cursor.execute("UPDATE users SET password = %s WHERE reset_token = %s", (hashed_password, token))
        connection.commit()

        flash('Your password has been successfully reset!', 'success')
        return redirect(url_for('index'))

    return render_template('reset_password.html', token=token)


@flask_app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("fullName")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")  # For validation only
        phone_number = request.form.get("phoneNumber")
        gender = request.form.get("gender")

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))

        # Password strength validation
        if not is_password_strong(password):
            flash("Password must be at least 8 characters long, contain a lowercase letter, an uppercase letter, a number, and a special character.", "error")
            return redirect(url_for("register"))

            # Phone number validation
        if not is_phone_number_valid(phone_number):
            flash("Invalid phone number format. Please enter a valid 10-digit phone number.", "error")
            return redirect(url_for("register"))

        # Check if username or email already exists in the database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE username = %s OR email = %s
        """, (username, email))
        existing_user = cursor.fetchone()
        cursor.close()

        if existing_user:
            flash("Username or email already exists.", "error")
            return redirect(url_for("register"))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Save the new user data in the database
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO users (full_name, username, email, password, phone_number, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (full_name, username, email, hashed_password, phone_number, gender))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


def is_password_strong(password):
    # At least one lowercase letter, one uppercase letter, one number, one special character, and minimum 8 characters
    pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])(?=.{8,})')
    return bool(pattern.match(password))


def is_phone_number_valid(phone_number):
    # This regex checks for exactly 10 digits, with optional spaces or dashes.
    pattern = re.compile(r'^\+?[\d\s\-]{10,15}$')  # Allows up to 15 characters, including spaces or dashes
    return bool(pattern.match(phone_number))


@flask_app.route("/home")
def home():
    # Debug: Print session to check if user_id and username are present
    print(session)

    # Check if the user is logged in
    if "user_id" not in session:
        flash("Please log in first", "warning")
        return redirect(url_for("index"))  # Redirect to login page

    # If logged in, render home page with the username from session
    username = session.get("username")
    response = make_response(render_template("home.html", username=username))

    # Add cache control headers to prevent caching
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@flask_app.route("/terms_conditions")
def terms():
    return render_template("terms_conditions.html")


@flask_app.route("/about")
def about():
    # Debug: Print session to check if user_id and username are present
    print(session)

    # Check if the user is logged in
    if "user_id" not in session:
        flash("Please log in first", "warning")
        return redirect(url_for("index"))  # Redirect to login page

    # Render the About page with no-cache headers to prevent caching
    response = make_response(render_template("about.html"))
    # Cache control headers to prevent caching
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@flask_app.route("/profile", methods=["GET", "POST"])
def profile():
    # Check if the user is logged in
    if "user_id" not in session:
        flash("Please log in first", "warning")
        return redirect(url_for("index"))  # Redirect to login page

    user_id = session["user_id"]
    # Fetch the user's current data from the database
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT full_name, username, email, phone_number, gender FROM users WHERE id = %s
    """, (user_id,))
    user_data = cursor.fetchone()
    cursor.close()

    if not user_data:
        flash("User not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        # Get updated data from the form
        full_name = request.form.get("fullName")
        email = request.form.get("email")
        phone_number = request.form.get("phoneNumber")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("profile"))

        # Password validation
        if password and not is_password_strong(password):
            flash(
                "Password must be at least 8 characters long, contain a lowercase letter, an uppercase letter, a number, and a special character.",
                "error")
            return redirect(url_for("profile"))

        # Update the database with the new information
        hashed_password = generate_password_hash(password) if password else None

        # Update user info in the database
        cursor = connection.cursor()
        if hashed_password:
            cursor.execute("""
                UPDATE users
                SET full_name = %s, email = %s, phone_number = %s, password = %s
                WHERE id = %s
            """, (full_name, email, phone_number, hashed_password, user_id))
        else:
            cursor.execute("""
                UPDATE users
                SET full_name = %s, email = %s, phone_number = %s
                WHERE id = %s
            """, (full_name, email, phone_number, user_id))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Profile updated successfully", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user_data=user_data)


@flask_app.route("/how_to_use")
def how_to_use():
    # Debug: Print session to check if user_id and username are present
    print(session)

    # Check if the user is logged in
    if "user_id" not in session:
        flash("Please log in first", "warning")
        return redirect(url_for("index"))  # Redirect to login page

    # Render the About page with no-cache headers to prevent caching
    response = make_response(render_template("how_to_use.html"))
    # Cache control headers to prevent caching
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@flask_app.route("/contact", methods=["GET", "POST"])
def contact():

    # Check if the user is logged in
    if "user_id" not in session:
        flash("Please log in first", "warning")
        return redirect(url_for("index"))  # Redirect to login page

    if request.method == "POST":
        name = request.form["name"]
        user_email = request.form["email"]
        message_body = request.form["message"]

        # Prepare the email content
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = f"Message from {name}"

        # Body of the email
        body = f"Message from: {name}\nEmail: {user_email}\n\n{message_body}"
        message.attach(MIMEText(body, "plain"))

        try:
            # SMTP setup and sending the email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, message.as_string())

            flash("Sent successfully!", "success")  # Flash success message
        except Exception as e:
            flash(f"Error sending email: {str(e)}", "danger")  # Flash error message

        return redirect(url_for("contact"))  # Redirect after sending email

    # Render the Contact page with no-cache headers
    response = make_response(render_template("contact.html"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@flask_app.route("/result")
def result():
    if "user_id" not in session:
        flash("Please log in first", "warning")
        return redirect(url_for("index"))  # Redirect to login page

    return render_template("result.html")


@flask_app.route("/logout")
def logout():
    # Clear all session data
    session.clear()

    # Flash a success message
    flash("You have been logged out successfully.", "success")

    # Redirect with no-store cache headers
    response = make_response(redirect(url_for("index")))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@flask_app.route("/predict", methods=["POST"])
def predict():
    try:
        float_features = [float(x) for x in request.form.values()]
        input_data_as_numpy_array = np.asarray(float_features)
        input_data_reshaped = input_data_as_numpy_array.reshape(1, -1)

        prediction = model.predict(input_data_reshaped)
        predicted_sales = prediction[0]

        return render_template("result.html", prediction_text=f'Predicted sales for next month is {predicted_sales}')

    except ValueError as e:
        flash(f"Input error: {e}", "error")
        return redirect(url_for("home"))


if __name__ == "__main__":
    flask_app.run(debug=True)
