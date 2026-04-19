import os
import pandas as pd
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, flash
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------- MYSQL CONNECTION ----------------
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor(dictionary=True)

# ---------------- EMAIL FUNCTION ----------------
def send_reset_email(to_email):
    msg = MIMEText("Click here to reset password: http://127.0.0.1:5000/reset-password")
    msg['Subject'] = "Password Reset"
    msg['From'] = os.getenv("MAIL_FROM")
    msg['To'] = to_email

    server = smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT")))
    server.starttls()
    server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
    server.send_message(msg)
    server.quit()

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']

        # Validation
        if not (email.endswith("@gmail.com") or email.endswith("@yahoo.com")):
            flash("Use Gmail or Yahoo email")
            return redirect('/signup')

        if len(mobile) != 10 or not mobile.isdigit():
            flash("Mobile must be 10 digits")
            return redirect('/signup')

        # Check duplicate
        cursor.execute("SELECT * FROM users WHERE mobile=%s OR email=%s", (mobile, email))
        if cursor.fetchone():
            flash("User already exists")
            return redirect('/signup')

        # Hash password
        hashed_password = generate_password_hash(password)

        query = "INSERT INTO users (name, email, mobile, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, mobile, hashed_password))
        db.commit()

        flash("Signup successful")
        return redirect('/login')

    return render_template('signup.html')


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE mobile=%s", (mobile,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            return redirect('/dashboard')
        else:
            flash("Invalid credentials")

    return render_template('login.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    output = None

    if request.method == 'POST':
        file = request.files['file']

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            try:
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)

                output = df.head().to_html(classes='table')
            except:
                flash("Invalid file format")

    return render_template('dashboard.html', output=output)


# ---------------- FORGOT PASSWORD ----------------
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        mobile = request.form['mobile']

        cursor.execute("SELECT email FROM users WHERE mobile=%s", (mobile,))
        user = cursor.fetchone()

        if user:
            send_reset_email(user['email'])
            return redirect('/forget-password-sent')
        else:
            flash("Mobile not registered")

    return render_template('forget_password.html')


@app.route('/forget-password-sent')
def forget_password_sent():
    return render_template('forget_password_sent.html')


# ---------------- RESET PASSWORD ----------------
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Passwords do not match")
            return redirect('/reset-password')

        cursor.execute("SELECT * FROM users WHERE mobile=%s", (mobile,))
        user = cursor.fetchone()

        if not user:
            flash("Mobile not registered")
            return redirect('/reset-password')

        hashed_password = generate_password_hash(new_password)

        cursor.execute("UPDATE users SET password=%s WHERE mobile=%s",
                       (hashed_password, mobile))
        db.commit()

        flash("Password updated successfully")
        return redirect('/login')

    return render_template('reset_password.html')


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)