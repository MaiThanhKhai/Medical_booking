# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical_booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

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


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        phone = request.form['phone']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng!', 'error')
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone=phone
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Đăng ký thành công!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất!', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    appointments = Appointment.query.filter_by(patient_id=user.id).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('dashboard.html', user=user, appointments=appointments)

@app.route('/doctors')
def doctors():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    search = request.args.get('search', '')
    specialty_filter = request.args.get('specialty', '')
    
    query = Doctor.query
    
    if search:
        query = query.filter(Doctor.name.contains(search))
    
    if specialty_filter:
        query = query.filter(Doctor.specialty == specialty_filter)
    
    doctors = query.all()
    specialties = db.session.query(Doctor.specialty).distinct().all()
    specialties = [s[0] for s in specialties]
    
    return render_template('doctors.html', doctors=doctors, specialties=specialties, 
                         search=search, specialty_filter=specialty_filter)

@app.route('/book_appointment/<int:doctor_id>', methods=['GET', 'POST'])
def book_appointment(doctor_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    doctor = Doctor.query.get_or_404(doctor_id)
    today = date.today().isoformat()
    
    if request.method == 'POST':
        appointment_date = datetime.strptime(request.form['appointment_date'], '%Y-%m-%d').date()
        appointment_time = request.form['appointment_time']
        symptoms = request.form['symptoms']
        
        # Check if appointment slot is available
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).first()
        
        if existing:
            flash('Thời gian này đã được đặt! Vui lòng chọn thời gian khác.', 'error')
            return render_template('book_appointment.html', doctor=doctor, today= today)
        
        # Create new appointment
        new_appointment = Appointment(
            patient_id=session['user_id'],
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            symptoms=symptoms
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        flash('Đặt lịch khám thành công!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('book_appointment.html', doctor=doctor, today= today)

@app.route('/edit_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check if user owns this appointment
    if appointment.patient_id != session['user_id']:
        flash('Bạn không có quyền sửa lịch hẹn này!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        appointment_date = datetime.strptime(request.form['appointment_date'], '%Y-%m-%d').date()
        appointment_time = request.form['appointment_time']
        symptoms = request.form['symptoms']
        
        # Check if new slot is available (excluding current appointment)
        existing = Appointment.query.filter(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.id != appointment_id
        ).first()
        
        if existing:
            flash('Thời gian này đã được đặt! Vui lòng chọn thời gian khác.', 'error')
            return render_template('edit_appointment.html', appointment=appointment)
        
        # Update appointment
        appointment.appointment_date = appointment_date
        appointment.appointment_time = appointment_time
        appointment.symptoms = symptoms
        
        db.session.commit()
        
        flash('Cập nhật lịch hẹn thành công!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_appointment.html', appointment=appointment)

@app.route('/cancel_appointment/<int:appointment_id>')
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check if user owns this appointment
    if appointment.patient_id != session['user_id']:
        flash('Bạn không có quyền hủy lịch hẹn này!', 'error')
        return redirect(url_for('dashboard'))
    
    appointment.status = 'Cancelled'
    db.session.commit()
    
    flash('Đã hủy lịch hẹn!', 'info')
    return redirect(url_for('dashboard'))

@app.route('/delete_appointment/<int:appointment_id>')
def delete_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check if user owns this appointment
    if appointment.patient_id != session['user_id']:
        flash('Bạn không có quyền xóa lịch hẹn này!', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(appointment)
    db.session.commit()
    
    flash('Đã xóa lịch hẹn!', 'info')
    return redirect(url_for('dashboard'))

# def init_db():
#     """Initialize database with sample data"""
#     db.create_all()
    
#     # Add sample doctors if they don't exist
#     if Doctor.query.count() == 0:
#         doctors = [
#             Doctor(name='BS. Nguyễn Văn An', specialty='Nội khoa', phone='0901234567', 
#                   email='bs.an@hospital.com', experience=10),
#             Doctor(name='BS. Trần Thị Bình', specialty='Ngoại khoa', phone='0901234568', 
#                   email='bs.binh@hospital.com', experience=8),
#             Doctor(name='BS. Lê Văn Cường', specialty='Tim mạch', phone='0901234569', 
#                   email='bs.cuong@hospital.com', experience=15),
#             Doctor(name='BS. Phạm Thị Dung', specialty='Da liễu', phone='0901234570', 
#                   email='bs.dung@hospital.com', experience=12),
#             Doctor(name='BS. Hoàng Văn Em', specialty='Tai mũi họng', phone='0901234571', 
#                   email='bs.em@hospital.com', experience=7),
#         ]
        
#         for doctor in doctors:
#             db.session.add(doctor)
        
#         db.session.commit()

# if __name__ == '__main__':
#     with app.app_context():
#         init_db()
#     app.run(debug=True)

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.is_admin and check_password_hash(user.password_hash, password):
            session['admin_id'] = user.id
            session['is_admin'] = True
            flash('Đăng nhập admin thành công!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Thông tin đăng nhập admin không đúng!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Thống kê
    total_appointments = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='Pending').count()
    confirmed_appointments = Appointment.query.filter_by(status='Confirmed').count()
    cancelled_appointments = Appointment.query.filter_by(status='Cancelled').count()
    
    # Lấy lịch hẹn gần đây
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html', 
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         confirmed_appointments=confirmed_appointments,
                         cancelled_appointments=cancelled_appointments,
                         recent_appointments=recent_appointments)

@app.route('/admin/appointments')
def admin_appointments():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = Appointment.query
    
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    if search:
        query = query.join(User).filter(User.full_name.contains(search))
    
    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
    
    return render_template('admin_appointments.html', appointments=appointments, 
                         status_filter=status_filter, search=search)

@app.route('/admin/update_status/<int:appointment_id>/<status>')
def update_appointment_status(appointment_id, status):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if status in ['Pending', 'Confirmed', 'Cancelled']:
        appointment.status = status
        db.session.commit()
        flash(f'Đã cập nhật trạng thái thành "{status}"!', 'success')
    else:
        flash('Trạng thái không hợp lệ!', 'error')
    
    return redirect(url_for('admin_appointments'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('is_admin', None)
    flash('Đã đăng xuất admin!', 'info')
    return redirect(url_for('index'))

def init_db():
    """Initialize database with sample data"""
    db.create_all()
    
    # Add admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_user = User(
            username='admin',
            email='admin@hospital.com',
            password_hash=generate_password_hash('admin123'),
            full_name='Administrator',
            phone='0900000000',
            is_admin=True
        )
        db.session.add(admin_user)
    
    # Add sample doctors if they don't exist
    if Doctor.query.count() == 0:
        doctors = [
            Doctor(name='BS. Nguyễn Văn An', specialty='Nội khoa', phone='0901234567', 
                  email='bs.an@hospital.com', experience=10),
            Doctor(name='BS. Trần Thị Bình', specialty='Ngoại khoa', phone='0901234568', 
                  email='bs.binh@hospital.com', experience=8),
            Doctor(name='BS. Lê Văn Cường', specialty='Tim mạch', phone='0901234569', 
                  email='bs.cuong@hospital.com', experience=15),
            Doctor(name='BS. Phạm Thị Dung', specialty='Da liễu', phone='0901234570', 
                  email='bs.dung@hospital.com', experience=12),
            Doctor(name='BS. Hoàng Văn Em', specialty='Tai mũi họng', phone='0901234571', 
                  email='bs.em@hospital.com', experience=7),
        ]
        
        for doctor in doctors:
            db.session.add(doctor)
        
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)