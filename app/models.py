from app import db
from datetime import datetime
from sqlalchemy.orm import validates
import re

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(32), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    
    @validates('full_name')
    def validate_full_name(self, key, value):
        if not re.match(r'^[A-Za-zÀ-ỹ\s]+$', value):
            raise ValueError("Full name chỉ được chứa ký tự chữ và khoảng trắng.")
        return value
    
    @validates('phone')
    def validate_phone(self, key, value):
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Số điện thoại phải là 10 chữ số.")
        if not value.startswith('0'):
            raise ValueError("Số điện thoại phải bắt đầu bằng số 0.")
        if not re.match(r'^[0-9]+$', value):
            raise ValueError("Số điện thoại chỉ được chứa các chữ số.")
        return value
    
    

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    experience = db.Column(db.Integer, nullable=False)  # years of experience
    
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(10), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Confirmed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
