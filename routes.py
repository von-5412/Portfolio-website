from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_mail import Message
from app import app, mail
import logging

@app.route('/')
def index():
    """Main portfolio page"""
    return render_template('index.html')

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
        
        # Create and send email
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
