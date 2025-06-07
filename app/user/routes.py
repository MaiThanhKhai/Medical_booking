from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.models import User, Doctor, Appointment, db
from datetime import datetime, date

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    appointments = Appointment.query.filter_by(patient_id=user.id).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('user/dashboard.html', user=user, appointments=appointments)

@user_bp.route('/doctors')
def doctors():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
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
    
    return render_template('user/doctors.html', doctors=doctors, specialties=specialties, 
                         search=search, specialty_filter=specialty_filter)

@user_bp.route('/book_appointment/<int:doctor_id>', methods=['GET', 'POST'])
def book_appointment(doctor_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

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
            return render_template('user/book_appointment.html', doctor=doctor, today= today)
        
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
        return redirect(url_for('user.dashboard'))

    return render_template('user/book_appointment.html', doctor=doctor, today= today)

@user_bp.route('/edit_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check if user owns this appointment
    if appointment.patient_id != session['user_id']:
        flash('Bạn không có quyền sửa lịch hẹn này!', 'error')
        return redirect(url_for('user.dashboard'))

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
            return render_template('user/edit_appointment.html', appointment=appointment)
        
        # Update appointment
        appointment.appointment_date = appointment_date
        appointment.appointment_time = appointment_time
        appointment.symptoms = symptoms
        
        db.session.commit()
        
        flash('Cập nhật lịch hẹn thành công!', 'success')
        return redirect(url_for('user.dashboard'))
    
    return render_template('user/edit_appointment.html', appointment=appointment)

@user_bp.route('/cancel_appointment/<int:appointment_id>')
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check if user owns this appointment
    if appointment.patient_id != session['user_id']:
        flash('Bạn không có quyền hủy lịch hẹn này!', 'error')
        return redirect(url_for('user.dashboard'))
    
    appointment.status = 'Cancelled'
    db.session.commit()
    
    flash('Đã hủy lịch hẹn!', 'info')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/delete_appointment/<int:appointment_id>')
def delete_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check if user owns this appointment
    if appointment.patient_id != session['user_id']:
        flash('Bạn không có quyền xóa lịch hẹn này!', 'error')
        return redirect(url_for('user.dashboard'))
    
    db.session.delete(appointment)
    db.session.commit()
    
    flash('Đã xóa lịch hẹn!', 'info')
    return redirect(url_for('user.dashboard'))