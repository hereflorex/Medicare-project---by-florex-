from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'medicare_2026_super_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///medicare.db').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default='patient') # 'doctor' or 'patient'
    specialization = db.Column(db.String(100), nullable=True) # Only for doctors

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(50))
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Scheduled')

# Routes
@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    hashed_pw = generate_password_hash(data['password'])
    new_user = User(name=data['name'], email=data['email'], password=hashed_pw, 
                    role=data['role'], specialization=data.get('specialization'))
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True})
    except:
        return jsonify({"success": False, "error": "Email already exists"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['role'] = user.role
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('index'))
    stats = {
        "doctors": User.query.filter_by(role='doctor').count(),
        "patients": User.query.filter_by(role='patient').count(),
        "appointments": Appointment.query.count()
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/doctors')
def doctors_page():
    doctors = User.query.filter_by(role='doctor').all()
    return render_template('doctors.html', doctors=doctors)

@app.route('/api/book', methods=['POST'])
def book_apt():
    data = request.json
    new_apt = Appointment(patient_id=session['user_id'], doctor_id=data['doctor_id'], 
                          date=data['date'], reason=data['reason'])
    db.session.add(new_apt)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
