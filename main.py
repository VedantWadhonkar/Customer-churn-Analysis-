from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        company = request.form['company']
        mobile = request.form['mobile']
        password = request.form['password']

        print("Signup Data:", email, company, mobile)

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']

        print("Login Data:", mobile)

        return redirect(url_for('home'))

    return render_template('login.html')


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)