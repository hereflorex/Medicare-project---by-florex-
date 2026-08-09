from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'medicare_2026')

# Railway Postgres Fix
uri = os.getenv("DATABASE_URL", "sqlite:///medicare.db")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models (Same as before)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(10))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(50))
    reason = db.Column(db.String(200))

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"success": False, "error": "Email already exists"}), 400
        new_user = User(name=data['name'], email=data['email'], 
                        password=generate_password_hash(data['password']), role=data['role'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        session['user_name'] = user.name
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Wrong email/password"}), 401

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect('/')
    # Dummy stats for now
    stats = {"doctors": 12, "patients": 45, "appointments": 3}
    return render_template('dashboard.html', stats=stats)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
