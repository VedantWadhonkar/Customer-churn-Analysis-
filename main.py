import os
import time
import re
import pandas as pd
import mysql.connector
from flask import Flask, render_template, request, redirect, flash, session
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

from training import analyze_churn

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# ---------------- UPLOAD CONFIG ----------------
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- VALIDATION ----------------
def is_valid_mobile(mobile):
    return re.fullmatch(r'[0-9]{10}', mobile)

# ---------------- MYSQL CONNECTION ----------------
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor(dictionary=True)

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
        company = request.form['company']

        if not (email.endswith("@gmail.com") or email.endswith("@yahoo.com")):
            flash("Use Gmail or Yahoo email")
            return redirect('/signup')

        if not is_valid_mobile(mobile):
            flash("Mobile must be exactly 10 digits")
            return redirect('/signup')

        cursor.execute("SELECT * FROM users WHERE mobile=%s OR email=%s", (mobile, email))
        if cursor.fetchone():
            flash("User already exists")
            return redirect('/signup')

        hashed_password = generate_password_hash(password)

        query = """
        INSERT INTO users (owner_name, email, mobile, company, password_hash)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, mobile, company, hashed_password))
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

        if not is_valid_mobile(mobile):
            flash("Enter valid 10-digit mobile number")
            return redirect('/login')

        cursor.execute("SELECT * FROM users WHERE mobile=%s", (mobile,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user'] = mobile
            return redirect('/dashboard')
        else:
            flash("Invalid credentials")

    return render_template('login.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully")
    return redirect('/')


# ---------------- DASHBOARD (FINAL) ----------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    output = None

    # ✅ GET COMPANY NAME
    cursor.execute("SELECT company FROM users WHERE mobile=%s", (session['user'],))
    user = cursor.fetchone()
    company = user['company'] if user else "User"

    if request.method == 'POST':
        file = request.files['file']

        if file and file.filename != "" and allowed_file(file.filename):

            filename = str(int(time.time())) + "_" + file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # ✅ READ FILE
                df = pd.read_csv(filepath) if filename.endswith('.csv') else pd.read_excel(filepath)

                # ✅ REQUIRED COLUMN CHECK
                required_columns = ['Churn']
                missing = [col for col in required_columns if col not in df.columns]

                # ❌ INVALID DATASET
                if missing:
                    output = {
                        "status": "error",
                        "missing": missing,
                        "required": required_columns
                    }
                    flash("Upload proper dataset with required columns")

                # ✅ VALID DATASET
                else:
                    result = analyze_churn(filepath)

                    output = {
                        "status": "success",
                        "data": result
                    }

                    flash("Dataset uploaded successfully")

            except Exception as e:
                output = {
                    "status": "error",
                    "missing": [],
                    "required": [],
                    "data": f"Error: {str(e)}"
                }

        else:
            flash("Only CSV and Excel files are allowed")

    return render_template('dashboard.html', output=output, company=company)


# ---------------- FORGOT PASSWORD ----------------
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        cursor.execute("SELECT email FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            return redirect(f'/reset-password?email={email}')
        else:
            flash("Email not registered")

    return render_template('forget_password.html')


# ---------------- RESET PASSWORD ----------------
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():

    email = request.args.get('email')

    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Passwords do not match")
            return redirect(f'/reset-password?email={email}')

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            flash("Email not registered")
            return redirect('/forgot-password')

        hashed_password = generate_password_hash(new_password)

        cursor.execute(
            "UPDATE users SET password_hash=%s WHERE email=%s",
            (hashed_password, email)
        )
        db.commit()

        flash("Password updated successfully")
        return redirect('/login')

    return render_template('reset_password.html', email=email)


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)