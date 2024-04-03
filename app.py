from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wallet.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_success = False
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully. Please log in.', 'success')
        signup_success = True
    return render_template('signup.html', signup_success=signup_success)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    if request.method == 'POST' or request.method == 'GET':
        logout_user()
        return redirect(url_for('index'))

@app.route('/add_money', methods=['POST'])
@login_required
def add_money():
    amount = float(request.form['amount'])
    current_user.balance += amount
    db.session.commit()
    flash('Amount added successfully', 'success')
    return redirect(url_for('index'))

@app.route('/send_money', methods=['POST'])
@login_required
def send_money():
    recipient_email = request.form['recipient_email']
    amount = float(request.form['amount'])
    recipient = User.query.filter_by(email=recipient_email).first()
    if recipient:
        if current_user.balance >= amount:
            current_user.balance -= amount
            recipient.balance += amount
            db.session.commit()
            flash('Money sent successfully', 'success')
        else:
            flash('Insufficient funds', 'error')
    else:
        flash('Recipient not found', 'error')
    return redirect(url_for('index'))

@app.route('/check_balance')
@login_required
def check_balance():
    return render_template('balance.html', balance=current_user.balance)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

