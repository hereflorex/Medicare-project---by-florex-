from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import or_, func
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-secret-in-production')

database_url = os.getenv('DATABASE_URL', '').strip()
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
if not database_url:
    database_url = 'sqlite:///medicare.db'
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

db = SQLAlchemy(app)


class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    available = db.Column(db.Boolean, default=True, nullable=False)
    bio = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True, cascade='all, delete-orphan')


class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    medical_history = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True, cascade='all, delete-orphan')
    invoices = db.relationship('Invoice', backref='patient', lazy=True, cascade='all, delete-orphan')


class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    appointment_date = db.Column(db.DateTime, nullable=False, index=True)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='scheduled', nullable=False, index=True)
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    invoice = db.relationship('Invoice', back_populates='appointment', uselist=False, cascade='all, delete-orphan')


class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, index=True)
    medication = db.Column(db.String(255), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    doctor = db.relationship('Doctor', backref=db.backref('prescriptions', lazy=True))


class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def current_user():
    role = session.get('role')
    user_id = session.get('user_id')
    if not role or not user_id:
        return None
    return Doctor.query.get(user_id) if role == 'doctor' else Patient.query.get(user_id)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('index'))
        return view(*args, **kwargs)
    return wrapped


def role_required(role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if session.get('role') != role or not current_user():
                if request.path.startswith('/api/'):
                    return jsonify({'error': f'{role.title()} access required'}), 403
                return redirect(url_for('dashboard'))
            return view(*args, **kwargs)
        return wrapped
    return decorator


def user_payload(user, role):
    data = {'id': user.id, 'name': user.name, 'email': user.email, 'phone': user.phone, 'role': role}
    if role == 'patient':
        data.update({'age': user.age, 'address': user.address, 'medical_history': user.medical_history or ''})
    else:
        data.update({'specialization': user.specialization, 'available': user.available, 'bio': user.bio or ''})
    return data


@app.context_processor
def inject_user():
    user = current_user()
    return {'current_user': user, 'current_role': session.get('role')}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login_page():
    if current_user():
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/register')
def register_page():
    if current_user():
        return redirect(url_for('dashboard'))
    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/doctors')
@login_required
def doctors_page():
    return render_template('doctors.html')


@app.route('/appointments')
@login_required
def appointments_page():
    return render_template('appointments.html')


@app.route('/prescriptions')
@login_required
def prescriptions_page():
    return render_template('prescriptions.html')


@app.route('/billing')
@login_required
def billing_page():
    return render_template('billing.html')


@app.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.post('/api/auth/register')
def register():
    data = request.get_json(silent=True) or {}
    role = data.get('role', 'patient')
    required = ['name', 'email', 'password']
    missing = [key for key in required if not str(data.get(key, '')).strip()]
    if missing:
        return jsonify({'error': f"Missing: {', '.join(missing)}"}), 400
    email = data['email'].strip().lower()
    if Patient.query.filter(func.lower(Patient.email) == email).first() or Doctor.query.filter(func.lower(Doctor.email) == email).first():
        return jsonify({'error': 'An account with this email already exists'}), 409
    if len(data['password']) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    try:
        if role == 'doctor':
            user = Doctor(name=data['name'].strip(), email=email, password=generate_password_hash(data['password']),
                          specialization=str(data.get('specialization') or 'General Medicine').strip(), phone=str(data.get('phone') or '').strip(),
                          bio=str(data.get('bio', '')).strip())
        else:
            age_raw = str(data.get('age') or '').strip()
            if age_raw:
                try:
                    age = int(age_raw)
                except ValueError:
                    return jsonify({'error': 'Enter a valid age'}), 400
                if age < 1 or age > 120:
                    return jsonify({'error': 'Enter a valid age'}), 400
            else:
                age = 0
            user = Patient(name=data['name'].strip(), email=email, password=generate_password_hash(data['password']),
                           phone=str(data.get('phone') or '').strip(), age=age, address=str(data.get('address') or '').strip(),
                           medical_history=str(data.get('medical_history', '')).strip())
        db.session.add(user)
        db.session.commit()
        session.clear()
        session['user_id'] = user.id
        session['role'] = role
        return jsonify({'message': 'Account created successfully', 'user': user_payload(user, role)}), 201
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Could not create account', 'detail': str(exc)}), 500


@app.post('/api/auth/login')
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    role = data.get('role', 'patient')
    model = Doctor if role == 'doctor' else Patient
    user = model.query.filter(func.lower(model.email) == email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email, password, or account type'}), 401
    session.clear()
    session['user_id'] = user.id
    session['role'] = role
    session.permanent = True
    return jsonify({'message': 'Login successful', 'user': user_payload(user, role), 'redirect': url_for('dashboard')}), 200


@app.post('/api/auth/logout')
def logout_api():
    session.clear()
    return jsonify({'message': 'Logged out'}), 200


@app.get('/api/auth/me')
def me():
    user = current_user()
    if not user:
        return jsonify({'authenticated': False}), 200
    return jsonify({'authenticated': True, 'user': user_payload(user, session['role'])}), 200


@app.get('/api/doctors')
def get_doctors():
    search = request.args.get('search', '').strip()
    specialization = request.args.get('specialization', '').strip()
    query = Doctor.query
    if search:
        term = f'%{search}%'
        query = query.filter(or_(Doctor.name.ilike(term), Doctor.specialization.ilike(term)))
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
    doctors = query.order_by(Doctor.name.asc()).all()
    return jsonify([{'id': d.id, 'name': d.name, 'specialization': d.specialization, 'phone': d.phone,
                     'available': d.available, 'bio': d.bio or ''} for d in doctors])


@app.post('/api/doctors/availability')
@role_required('doctor')
def update_availability():
    data = request.get_json(silent=True) or {}
    doctor = current_user()
    doctor.available = bool(data.get('available'))
    db.session.commit()
    return jsonify({'message': 'Availability updated', 'available': doctor.available})


@app.get('/api/dashboard')
@login_required
def dashboard_data():
    role = session['role']
    user = current_user()
    if role == 'patient':
        appointments = Appointment.query.filter_by(patient_id=user.id).order_by(Appointment.appointment_date.desc()).all()
        return jsonify({
            'user': user_payload(user, role),
            'stats': {
                'appointments': Appointment.query.filter_by(patient_id=user.id).count(),
                'upcoming': Appointment.query.filter_by(patient_id=user.id, status='scheduled').filter(Appointment.appointment_date >= datetime.utcnow()).count(),
                'prescriptions': Prescription.query.filter_by(patient_id=user.id).count(),
                'pending_bills': Invoice.query.filter_by(patient_id=user.id, status='pending').count(),
            },
            'recent': [appointment_payload(a) for a in appointments[:5]]
        })
    appointments = Appointment.query.filter_by(doctor_id=user.id).order_by(Appointment.appointment_date.desc()).all()
    return jsonify({
        'user': user_payload(user, role),
        'stats': {
            'appointments': Appointment.query.filter_by(doctor_id=user.id).count(),
            'upcoming': Appointment.query.filter_by(doctor_id=user.id, status='scheduled').filter(Appointment.appointment_date >= datetime.utcnow()).count(),
            'completed': Appointment.query.filter_by(doctor_id=user.id, status='completed').count(),
            'pending': Appointment.query.filter_by(doctor_id=user.id, status='scheduled').count(),
        },
        'recent': [appointment_payload(a) for a in appointments[:8]]
    })


def appointment_payload(a):
    return {'id': a.id, 'doctor': a.doctor.name, 'doctor_id': a.doctor_id, 'patient': a.patient.name,
            'patient_id': a.patient_id, 'date': a.appointment_date.isoformat(), 'reason': a.reason,
            'status': a.status, 'notes': a.notes or ''}


@app.post('/api/appointments')
@role_required('patient')
def create_appointment():
    data = request.get_json(silent=True) or {}
    try:
        doctor_id = int(data['doctor_id'])
        appointment_date = datetime.fromisoformat(data['appointment_date'].replace('Z', '+00:00')).replace(tzinfo=None)
        reason = str(data['reason']).strip()
    except (KeyError, ValueError, TypeError):
        return jsonify({'error': 'Invalid appointment data'}), 400
    doctor = db.session.get(Doctor, doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    if not doctor.available:
        return jsonify({'error': 'Doctor is currently unavailable'}), 400
    if appointment_date <= datetime.utcnow():
        return jsonify({'error': 'Appointment must be in the future'}), 400
    conflict = Appointment.query.filter_by(doctor_id=doctor_id, appointment_date=appointment_date).filter(Appointment.status != 'cancelled').first()
    if conflict:
        return jsonify({'error': 'That time slot is already booked'}), 409
    appointment = Appointment(doctor_id=doctor_id, patient_id=current_user().id, appointment_date=appointment_date, reason=reason)
    db.session.add(appointment)
    db.session.flush()
    invoice = Invoice(patient_id=current_user().id, appointment_id=appointment.id, amount=500.0, status='pending')
    db.session.add(invoice)
    db.session.commit()
    return jsonify({'message': 'Appointment booked successfully', 'appointment': appointment_payload(appointment)}), 201


@app.get('/api/appointments')
@login_required
def get_my_appointments():
    role = session['role']
    user = current_user()
    query = Appointment.query.filter_by(patient_id=user.id) if role == 'patient' else Appointment.query.filter_by(doctor_id=user.id)
    status = request.args.get('status', '').strip()
    if status and status != 'all':
        query = query.filter_by(status=status)
    appointments = query.order_by(Appointment.appointment_date.desc()).all()
    return jsonify([appointment_payload(a) for a in appointments])


@app.patch('/api/appointments/<int:appointment_id>')
@login_required
def update_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    role = session['role']
    user = current_user()
    owns = appointment.patient_id == user.id if role == 'patient' else appointment.doctor_id == user.id
    if not owns:
        return jsonify({'error': 'You cannot modify this appointment'}), 403
    data = request.get_json(silent=True) or {}
    action = data.get('action')
    if action == 'cancel':
        if appointment.status == 'completed':
            return jsonify({'error': 'Completed appointments cannot be cancelled'}), 400
        appointment.status = 'cancelled'
    elif action == 'complete' and role == 'doctor':
        appointment.status = 'completed'
        appointment.notes = str(data.get('notes', appointment.notes or '')).strip()
    elif action == 'confirm' and role == 'doctor':
        appointment.status = 'scheduled'
    elif action == 'reschedule' and role == 'patient':
        try:
            new_date = datetime.fromisoformat(data['appointment_date'].replace('Z', '+00:00')).replace(tzinfo=None)
        except (KeyError, ValueError, TypeError):
            return jsonify({'error': 'Invalid new date/time'}), 400
        if new_date <= datetime.utcnow():
            return jsonify({'error': 'New appointment must be in the future'}), 400
        conflict = Appointment.query.filter(Appointment.id != appointment.id, Appointment.doctor_id == appointment.doctor_id,
                                             Appointment.appointment_date == new_date, Appointment.status != 'cancelled').first()
        if conflict:
            return jsonify({'error': 'That time slot is already booked'}), 409
        appointment.appointment_date = new_date
    else:
        return jsonify({'error': 'Unsupported appointment action'}), 400
    db.session.commit()
    return jsonify({'message': 'Appointment updated', 'appointment': appointment_payload(appointment)})


@app.get('/api/prescriptions')
@login_required
def get_prescriptions():
    user = current_user()
    if session['role'] == 'patient':
        prescriptions = Prescription.query.filter_by(patient_id=user.id).order_by(Prescription.created_at.desc()).all()
    else:
        prescriptions = Prescription.query.filter_by(doctor_id=user.id).order_by(Prescription.created_at.desc()).all()
    return jsonify([{'id': p.id, 'medication': p.medication, 'dosage': p.dosage, 'duration': p.duration,
                     'instructions': p.instructions or '', 'doctor': p.doctor.name, 'patient': p.patient.name,
                     'created_at': p.created_at.isoformat()} for p in prescriptions])


@app.post('/api/prescriptions')
@role_required('doctor')
def create_prescription():
    data = request.get_json(silent=True) or {}
    try:
        patient_id = int(data['patient_id'])
    except (KeyError, ValueError, TypeError):
        return jsonify({'error': 'Invalid patient'}), 400
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    for key in ('medication', 'dosage', 'duration'):
        if not str(data.get(key, '')).strip():
            return jsonify({'error': f'{key.title()} is required'}), 400
    prescription = Prescription(patient_id=patient_id, doctor_id=current_user().id,
                                medication=data['medication'].strip(), dosage=data['dosage'].strip(),
                                duration=data['duration'].strip(), instructions=str(data.get('instructions', '')).strip())
    db.session.add(prescription)
    db.session.commit()
    return jsonify({'message': 'Prescription created', 'id': prescription.id}), 201


@app.get('/api/billing')
@role_required('patient')
def billing():
    invoices = Invoice.query.filter_by(patient_id=current_user().id).order_by(Invoice.created_at.desc()).all()
    return jsonify([{'id': i.id, 'appointment_id': i.appointment_id, 'amount': i.amount, 'status': i.status,
                     'date': i.created_at.isoformat(), 'doctor': i.appointment.doctor.name,
                     'appointment_date': i.appointment.appointment_date.isoformat()} for i in invoices])


@app.post('/api/billing/<int:invoice_id>/pay')
@role_required('patient')
def pay_invoice(invoice_id):
    invoice = db.session.get(Invoice, invoice_id)
    if not invoice or invoice.patient_id != current_user().id:
        return jsonify({'error': 'Invoice not found'}), 404
    if invoice.status == 'paid':
        return jsonify({'message': 'Invoice already paid'})
    invoice.status = 'paid'
    db.session.commit()
    return jsonify({'message': 'Payment marked as paid'})


@app.patch('/api/profile')
@login_required
def update_profile():
    data = request.get_json(silent=True) or {}
    user = current_user()
    role = session['role']
    name = str(data.get('name', user.name)).strip()
    phone = str(data.get('phone', user.phone)).strip()
    email = str(data.get('email', user.email)).strip().lower()
    if not name or not phone or not email:
        return jsonify({'error': 'Name, email and phone are required'}), 400
    patient_match = Patient.query.filter(func.lower(Patient.email) == email, Patient.id != user.id).first()
    doctor_match = Doctor.query.filter(func.lower(Doctor.email) == email, Doctor.id != user.id).first()
    if patient_match or doctor_match:
        return jsonify({'error': 'Email is already in use'}), 409
    user.name, user.phone, user.email = name, phone, email
    if role == 'patient':
        try:
            user.age = int(data.get('age', user.age))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid age'}), 400
        user.address = str(data.get('address', user.address)).strip()
        user.medical_history = str(data.get('medical_history', user.medical_history or '')).strip()
    else:
        user.specialization = str(data.get('specialization', user.specialization)).strip()
        user.bio = str(data.get('bio', user.bio or '')).strip()
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'user': user_payload(user, role)})


@app.post('/api/auth/change-password')
@login_required
def change_password():
    data = request.get_json(silent=True) or {}
    user = current_user()
    if not check_password_hash(user.password, str(data.get('current_password', ''))):
        return jsonify({'error': 'Current password is incorrect'}), 400
    new_password = str(data.get('new_password', ''))
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400
    user.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'message': 'Password changed successfully'})


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return render_template('index.html'), 404


@app.errorhandler(500)
def server_error(error):
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return 'Internal server error', 500


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=True)
