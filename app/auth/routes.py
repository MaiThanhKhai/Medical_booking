from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
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
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng!', 'error')
            return render_template('auth/register.html')

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
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất!', 'info')
    return redirect(url_for('main.index'))