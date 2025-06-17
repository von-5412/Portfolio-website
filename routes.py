from flask import render_template, request, flash, redirect, url_for, jsonify, session
from flask_mail import Message
from flask_login import login_user, logout_user, login_required, current_user
from app import app, mail, db
import logging

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

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = app.User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_admin:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials or not an admin user.', 'error')
    
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
    """Admin dashboard with project management"""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    projects = app.Project.query.order_by(app.Project.created_at.desc()).all()
    contacts = app.Contact.query.order_by(app.Contact.created_at.desc()).all()
    return render_template('admin_dashboard.html', projects=projects, contacts=contacts)

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
