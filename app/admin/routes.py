from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.models import User, Appointment, db
from werkzeug.security import check_password_hash
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.is_admin and check_password_hash(user.password_hash, password):
            session['admin_id'] = user.id
            session['is_admin'] = True
            flash('Đăng nhập admin thành công!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Thông tin đăng nhập admin không đúng!', 'error')
    
    return render_template('admin/admin_login.html')
    
@admin_bp.route('/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin.admin_login'))
    
    # Thống kê
    total_appointments = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='Pending').count()
    confirmed_appointments = Appointment.query.filter_by(status='Confirmed').count()
    cancelled_appointments = Appointment.query.filter_by(status='Cancelled').count()
    
    # Lấy lịch hẹn gần đây
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()
    
    return render_template('admin/admin_dashboard.html', 
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         confirmed_appointments=confirmed_appointments,
                         cancelled_appointments=cancelled_appointments,
                         recent_appointments=recent_appointments)

    
@admin_bp.route('/appointments')
def admin_appointments():
    if 'admin_id' not in session:
        return redirect(url_for('admin.admin_login'))
    
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = Appointment.query
    
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    if search:
        query = query.join(User).filter(User.full_name.contains(search))
    
    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
    
    return render_template('admin/admin_appointments.html', appointments=appointments, 
                         status_filter=status_filter, search=search)

    
@admin_bp.route('/update_status/<int:appointment_id>/<status>')
def update_appointment_status(appointment_id, status):
    if 'admin_id' not in session:
        return redirect(url_for('admin.admin_login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if status in ['Pending', 'Confirmed', 'Cancelled']:
        appointment.status = status
        db.session.commit()
        flash(f'Đã cập nhật trạng thái thành "{status}"!', 'success')
    else:
        flash('Trạng thái không hợp lệ!', 'error')
    
    return redirect(url_for('admin.admin_appointments'))

@admin_bp.route('/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('is_admin', None)
    flash('Đã đăng xuất admin!', 'info')
    return redirect(url_for('main.index'))