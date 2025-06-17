from flask import render_template, request, flash, redirect, url_for, jsonify, session
from flask_mail import Message
from flask_login import login_user, logout_user, login_required, current_user
from app import app, mail, db
import logging
import re
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
import json

# Security helpers
def get_client_ip():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def parse_user_agent(user_agent_string):
    """Parse user agent to extract browser, OS, and device info"""
    browser = "Unknown"
    os = "Unknown"
    device = "Desktop"
    
    if user_agent_string:
        # Browser detection
        if "Chrome" in user_agent_string:
            browser = "Chrome"
        elif "Firefox" in user_agent_string:
            browser = "Firefox"
        elif "Safari" in user_agent_string and "Chrome" not in user_agent_string:
            browser = "Safari"
        elif "Edge" in user_agent_string:
            browser = "Edge"
        elif "Opera" in user_agent_string:
            browser = "Opera"
        
        # OS detection
        if "Windows" in user_agent_string:
            os = "Windows"
        elif "Mac OS X" in user_agent_string or "Macintosh" in user_agent_string:
            os = "macOS"
        elif "Linux" in user_agent_string:
            os = "Linux"
        elif "Android" in user_agent_string:
            os = "Android"
            device = "Mobile"
        elif "iPhone" in user_agent_string or "iPad" in user_agent_string:
            os = "iOS"
            device = "Mobile" if "iPhone" in user_agent_string else "Tablet"
        
        # Device detection
        if "Mobile" in user_agent_string or "iPhone" in user_agent_string:
            device = "Mobile"
        elif "Tablet" in user_agent_string or "iPad" in user_agent_string:
            device = "Tablet"
    
    return browser, os, device

def track_visitor():
    """Track visitor information"""
    try:
        ip_address = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        browser, os, device = parse_user_agent(user_agent)
        referrer = request.headers.get('Referer', '')
        page_visited = request.path
        language = request.headers.get('Accept-Language', '').split(',')[0] if request.headers.get('Accept-Language') else 'en'
        
        # Check if visitor exists
        existing_visitor = app.Visitor.query.filter_by(ip_address=ip_address).first()
        
        if existing_visitor:
            # Update existing visitor
            existing_visitor.visit_count += 1
            existing_visitor.last_visit = datetime.utcnow()
            existing_visitor.page_visited = page_visited
            existing_visitor.user_agent = user_agent
        else:
            # Create new visitor record
            visitor = app.Visitor(
                ip_address=ip_address,
                user_agent=user_agent,
                browser=browser,
                os=os,
                device=device,
                referrer=referrer,
                page_visited=page_visited,
                language=language
            )
            db.session.add(visitor)
        
        db.session.commit()
    except Exception as e:
        logging.error(f"Error tracking visitor: {str(e)}")

def rate_limit_check(ip_address, action, limit=5, window=300):
    """Check rate limiting for actions"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(seconds=window)
        
        if action == 'login':
            recent_attempts = app.LoginAttempt.query.filter(
                app.LoginAttempt.ip_address == ip_address,
                app.LoginAttempt.created_at > cutoff_time
            ).count()
        else:
            # For other actions, you can implement similar logic
            return True
        
        return recent_attempts < limit
    except Exception as e:
        logging.error(f"Error checking rate limit: {str(e)}")
        return True

def log_login_attempt(ip_address, username, success):
    """Log login attempts for security monitoring"""
    try:
        login_attempt = app.LoginAttempt(
            ip_address=ip_address,
            username=username,
            success=success,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(login_attempt)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error logging login attempt: {str(e)}")

@app.before_request
def before_request():
    """Track visitors before each request"""
    if request.endpoint not in ['static', 'admin_login', 'admin_logout']:
        track_visitor()

@app.route('/')
def index():
    """Main portfolio page"""
    projects = app.Project.query.filter_by(is_featured=True).order_by(app.Project.created_at.desc()).all()
    return render_template('index.html', projects=projects)

@app.route('/contact', methods=['POST'])
def contact():
    """Handle contact form submission"""
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # Basic validation
        if not all([name, email, subject, message]):
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('index') + '#contact')
        
        # Email validation (basic)
        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('index') + '#contact')
        
        # Save to database
        contact = app.Contact(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.session.add(contact)
        db.session.commit()
        
        # Create and send email
        try:
            msg = Message(
                subject=f"Portfolio Contact: {subject}",
                recipients=[app.config.get('MAIL_USERNAME', 'your-email@example.com')],
                body=f"""
New contact form submission:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
                """,
                reply_to=email
            )
            mail.send(msg)
        except Exception as email_error:
            logging.error(f"Email sending failed: {str(email_error)}")
            # Continue even if email fails since we saved to database
        
        flash('Thank you for your message! I\'ll get back to you soon.', 'success')
        
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        flash('Sorry, there was an error sending your message. Please try again later.', 'error')
    
    return redirect(url_for('index') + '#contact')

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('index.html'), 500

@app.route('/api/projects')
def api_projects():
    """API endpoint to get projects data"""
    projects = app.Project.query.filter_by(is_featured=True).order_by(app.Project.created_at.desc()).all()
    return jsonify([project.to_dict() for project in projects])

@app.route('/api/track-visitor', methods=['POST'])
def track_visitor_api():
    """API endpoint to track additional visitor data from frontend"""
    try:
        data = request.get_json()
        ip_address = get_client_ip()
        
        visitor = app.Visitor.query.filter_by(ip_address=ip_address).first()
        if visitor:
            if data.get('screen_resolution'):
                visitor.screen_resolution = data['screen_resolution']
            if data.get('visit_duration'):
                visitor.visit_duration = data['visit_duration']
            db.session.commit()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Error tracking visitor via API: {str(e)}")
        return jsonify({'status': 'error'}), 500

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page with security measures"""
    ip_address = get_client_ip()
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Rate limiting check
        if not rate_limit_check(ip_address, 'login'):
            flash('Too many login attempts. Please try again later.', 'error')
            log_login_attempt(ip_address, username, False)
            return render_template('admin_login.html')
        
        # Input validation
        if not username or not password:
            flash('Username and password are required.', 'error')
            log_login_attempt(ip_address, username, False)
            return render_template('admin_login.html')
        
        user = app.User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_admin:
            login_user(user, remember=False)
            session.permanent = True
            flash('Logged in successfully!', 'success')
            log_login_attempt(ip_address, username, True)
            
            # Log successful admin login
            logging.info(f"Admin login successful for {username} from {ip_address}")
            
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials or not an admin user.', 'error')
            log_login_attempt(ip_address, username, False)
            
            # Log failed login attempt
            logging.warning(f"Failed login attempt for {username} from {ip_address}")
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard with project management and visitor analytics"""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    projects = app.Project.query.order_by(app.Project.created_at.desc()).all()
    contacts = app.Contact.query.order_by(app.Contact.created_at.desc()).all()
    
    # Visitor analytics
    total_visitors = app.Visitor.query.count()
    recent_visitors = app.Visitor.query.filter(
        app.Visitor.last_visit > datetime.utcnow() - timedelta(days=7)
    ).order_by(app.Visitor.last_visit.desc()).limit(50).all()
    
    # Browser stats
    browser_stats = db.session.query(
        app.Visitor.browser, 
        db.func.count(app.Visitor.browser).label('count')
    ).group_by(app.Visitor.browser).all()
    
    # OS stats
    os_stats = db.session.query(
        app.Visitor.os, 
        db.func.count(app.Visitor.os).label('count')
    ).group_by(app.Visitor.os).all()
    
    # Device stats
    device_stats = db.session.query(
        app.Visitor.device, 
        db.func.count(app.Visitor.device).label('count')
    ).group_by(app.Visitor.device).all()
    
    # Login attempts (security monitoring)
    recent_login_attempts = app.LoginAttempt.query.filter(
        app.LoginAttempt.created_at > datetime.utcnow() - timedelta(days=7)
    ).order_by(app.LoginAttempt.created_at.desc()).limit(20).all()
    
    # Daily visitor counts for the last 30 days
    daily_visitors = []
    for i in range(30):
        date = datetime.utcnow().date() - timedelta(days=i)
        count = app.Visitor.query.filter(
            db.func.date(app.Visitor.last_visit) == date
        ).count()
        daily_visitors.append({'date': date.strftime('%Y-%m-%d'), 'count': count})
    
    analytics = {
        'total_visitors': total_visitors,
        'recent_visitors': recent_visitors,
        'browser_stats': browser_stats,
        'os_stats': os_stats,
        'device_stats': device_stats,
        'daily_visitors': list(reversed(daily_visitors)),
        'recent_login_attempts': recent_login_attempts
    }
    
    return render_template('admin_dashboard.html', 
                         projects=projects, 
                         contacts=contacts, 
                         analytics=analytics)

@app.route('/admin/project/add', methods=['GET', 'POST'])
@login_required
def add_project():
    """Add new project"""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        project = app.Project(
            title=request.form.get('title'),
            description=request.form.get('description'),
            thumbnail_url=request.form.get('thumbnail_url'),
            project_url=request.form.get('project_url'),
            github_url=request.form.get('github_url'),
            technologies=request.form.get('technologies'),
            status=request.form.get('status'),
            rating=float(request.form.get('rating', 0)),
            users_count=request.form.get('users_count'),
            metrics=request.form.get('metrics'),
            is_featured=bool(request.form.get('is_featured'))
        )
        
        db.session.add(project)
        db.session.commit()
        flash('Project added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_project_form.html', project=None)

@app.route('/admin/project/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Edit existing project"""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    project = app.Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.thumbnail_url = request.form.get('thumbnail_url')
        project.project_url = request.form.get('project_url')
        project.github_url = request.form.get('github_url')
        project.technologies = request.form.get('technologies')
        project.status = request.form.get('status')
        project.rating = float(request.form.get('rating', 0))
        project.users_count = request.form.get('users_count')
        project.metrics = request.form.get('metrics')
        project.is_featured = bool(request.form.get('is_featured'))
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_project_form.html', project=project)

@app.route('/admin/project/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    """Delete project"""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    project = app.Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/contact/mark-read/<int:contact_id>', methods=['POST'])
@login_required
def mark_contact_read(contact_id):
    """Mark contact message as read"""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    contact = app.Contact.query.get_or_404(contact_id)
    contact.is_read = True
    db.session.commit()
    flash('Message marked as read!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/contact/delete/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id):
    """Delete contact message"""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    contact = app.Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash('Message deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))
