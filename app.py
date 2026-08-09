from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hospital_management_secret_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/hospital_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    medical_history = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    medication = db.Column(db.String(255), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    doctor = db.relationship('Doctor', backref='prescriptions')

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appointment = db.relationship('Appointment', backref='invoice')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/doctors')
def doctors_page():
    return render_template('doctors.html')

@app.route('/appointments')
def appointments_page():
    return render_template('appointments.html')

@app.route('/about')
def about():
    return render_template('about.html')

# API Routes
@app.route('/api/doctors/register', methods=['POST'])
def doctor_register():
    data = request.json
    if Doctor.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    doctor = Doctor(
        name=data['name'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        specialization=data['specialization'],
        phone=data['phone']
    )
    db.session.add(doctor)
    db.session.commit()
    return jsonify({'message': 'Doctor registered successfully', 'id': doctor.id}), 201

@app.route('/api/patients/register', methods=['POST'])
def patient_register():
    data = request.json
    if Patient.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    patient = Patient(
        name=data['name'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        phone=data['phone'],
        age=data['age'],
        address=data['address']
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify({'message': 'Patient registered successfully', 'id': patient.id}), 201

@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify([{
        'id': d.id,
        'name': d.name,
        'specialization': d.specialization,
        'phone': d.phone,
        'available': d.available
    } for d in doctors]), 200

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    data = request.json
    appointment = Appointment(
        doctor_id=data['doctor_id'],
        patient_id=data['patient_id'],
        appointment_date=datetime.fromisoformat(data['appointment_date']),
        reason=data['reason']
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment booked successfully', 'id': appointment.id}), 201

@app.route('/api/appointments/<int:patient_id>', methods=['GET'])
def get_appointments(patient_id):
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    return jsonify([{
        'id': a.id,
        'doctor': a.doctor.name,
        'date': a.appointment_date.isoformat(),
        'reason': a.reason,
        'status': a.status
    } for a in appointments]), 200

@app.route('/api/prescriptions/<int:patient_id>', methods=['GET'])
def get_prescriptions(patient_id):
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()
    return jsonify([{
        'id': p.id,
        'medication': p.medication,
        'dosage': p.dosage,
        'duration': p.duration,
        'instructions': p.instructions,
        'doctor': p.doctor.name
    } for p in prescriptions]), 200

@app.route('/api/dashboard/stats', methods=['GET'])
def get_stats():
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='scheduled').count()
    
    return jsonify({
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
