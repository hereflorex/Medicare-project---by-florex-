from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'medicare_pro_2026')

# Database Setup
uri = os.getenv("DATABASE_URL", "sqlite:///medicare.db")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(10)) # 'doctor' or 'patient'

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    doctor_name = db.Column(db.String(100))
    date = db.Column(db.String(50))
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default="Scheduled")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect('/')
    stats = {
        "doctors": 8,
        "patients": 150,
        "appointments": Appointment.query.filter_by(patient_id=session['user_id']).count()
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/doctors')
def doctors():
    if 'user_id' not in session: return redirect('/')
    # Dummy Doctors List
    doc_list = [
        {"id": 1, "name": "Dr. Tirth", "spec": "Cardiologist"},
        {"id": 2, "name": "Dr. Dhvanit", "spec": "Neurologist"},
        {"id": 3, "name": "Dr. Sharma", "spec": "Pediatrician"},
        {"id": 4, "name": "Dr. Patel", "spec": "Orthopedic"}
    ]
    return render_template('doctors.html', doctors=doc_list)

@app.route('/appointments')
def appointments():
    if 'user_id' not in session: return redirect('/')
    user_apts = Appointment.query.filter_by(patient_id=session['user_id']).all()
    return render_template('appointments.html', appointments=user_apts)

@app.route('/about')
def about():
    return render_template('about.html')

# API Endpoints
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"success": False, "error": "User already exists"}), 400
    new_user = User(name=data['name'], email=data['email'], 
                    password=generate_password_hash(data['password']), role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        session['user_name'] = user.name
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid login"})

@app.route('/api/book', methods=['POST'])
def book():
    data = request.json
    new_apt = Appointment(patient_id=session['user_id'], doctor_name=data['doctor_name'],
                          date=data['date'], reason=data['reason'])
    db.session.add(new_apt)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
