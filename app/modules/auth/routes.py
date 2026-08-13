from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db, bcrypt
from app.models import User, Tenant
from flask_login import login_user, logout_user, current_user, login_required
from app.services.email_service import EmailService
import random
import string
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # ── SMART DISCOVERY: Find user by email first ─────────────────────────
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            if not user.is_active:
                flash('Account-kaaga waa la xannibay (Suspended). Fadlan la xiriir Admin-ka.', 'danger')
                return render_template('auth/login.html')
                
            login_user(user, remember=remember)
            
            # Record login in audit log
            from app.models import AuditLog
            log = AuditLog(
                user_id=user.id,
                action="Login",
                description=f"User logged in from {request.remote_addr}",
                tenant_id=user.tenant_id
            )
            db.session.add(log)
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Email ama Password-ka waa khalad. Fadlan iska hubi.', 'danger')
            
    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new business (Tenant) and its admin user."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        business_name    = request.form.get('business_name', '').strip()
        business_phone   = request.form.get('business_phone', '').strip()
        currency         = request.form.get('currency', '$')
        username         = request.form.get('username', '').strip()
        email            = request.form.get('email', '').strip().lower()
        password         = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # ── Validation ───────────────────────────────────────────────────────
        if not business_name:
            flash('Business name is required.', 'danger')
            return render_template('auth/register.html')

        if not username or len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'danger')
            return render_template('auth/register.html')

        try:
            # ── Create Tenant ─────────────────────────────────────────────────
            new_tenant = Tenant(
                name=business_name,
                phone=business_phone,
                currency=currency,
            )
            db.session.add(new_tenant)
            db.session.flush()  # get the new tenant.id before commit

            # ── Create Admin User ─────────────────────────────────────────────
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(
                username=username,
                email=email,
                password=hashed_pw,
                role='admin',
                tenant_id=new_tenant.id,
                is_active=True
            )
            db.session.add(new_user)
            db.session.commit()

            flash(f'Business "{business_name}" registered successfully! Please sign in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')

    return render_template('auth/register.html')

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not bcrypt.check_password_hash(current_user.password, old_password):
            flash('Password-kii hore waa khalad!', 'danger')
        elif new_password != confirm_password:
            flash('Password-ka cusub iyo kan loo celiyay isma laha!', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash('Password-kaaga si guul leh ayaa loo beddelay!', 'success')
            return redirect(url_for('main.dashboard'))
            
    return render_template('auth/change_password.html')

@auth.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    phone = request.form.get('phone')
    
    if username:
        current_user.username = username
    if phone is not None:
        current_user.phone = phone
        
    try:
        db.session.commit()
        flash('Macluumaadka profile-kaaga waa la cusboonaysiiyay!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Magacan horay ayaa loo isticmaalay. Fadlan dooro magac kale.', 'danger')
    return redirect(request.referrer or url_for('main.dashboard'))
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate 6-digit OTP
            otp = ''.join(random.choices(string.digits, k=6))
            user.otp_code = otp
            user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
            db.session.commit()
            
            # Send Email
            EmailService.send_otp_email(user.email, otp)
            flash('Code-ka xaqiijinta (OTP) waxaa loo soo diray email-kaaga.', 'info')
            return redirect(url_for('auth.verify_otp', email=email))
        else:
            flash('Email-kan kuma jiro system-ka. Fadlan iska hubi.', 'danger')
            
    return render_template('auth/forgot_password.html')

@auth.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = request.args.get('email')
    if not email:
        return redirect(url_for('auth.forgot_password'))
        
    user = User.query.filter_by(email=email).first()
    
    if request.method == 'POST':
        otp_entered = request.form.get('otp', '').strip()
        
        if user and user.otp_code == otp_entered:
            if datetime.utcnow() < user.otp_expiry:
                flash('Code-kii waa la xaqiijiyay! Hadda qor password cusub.', 'success')
                return redirect(url_for('auth.reset_password', email=email, token=otp_entered))
            else:
                flash('Code-kii wuu dhacay (Expired). Fadlan mar kale isku day.', 'danger')
        else:
            flash('Code-ka aad qortay waa khalad. Fadlan iska hubi.', 'danger')
            
    return render_template('auth/verify_otp.html', email=email)

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email')
    token = request.args.get('token')
    
    if not email or not token:
        return redirect(url_for('auth.forgot_password'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        user = User.query.filter_by(email=email, otp_code=token).first()
        if not user:
            flash('Codsi aan jirin! Fadlan mar kale bilow.', 'danger')
            return redirect(url_for('auth.forgot_password'))
            
        if password != confirm_password:
            flash('Password-yada isma laha!', 'danger')
        elif len(password) < 8:
            flash('Password-ku waa inuu ugu yaraan ka koobnaadaa 8 xaraf.', 'danger')
        else:
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            user.password = hashed_pw
            user.otp_code = None # Clear OTP after use
            user.otp_expiry = None
            db.session.commit()
            
            flash('Password-kaaga si guul leh ayaa loo beddelay! Hadda soo gal.', 'success')
            return redirect(url_for('auth.login'))
            
    return render_template('auth/reset_password.html', email=email, token=token)
