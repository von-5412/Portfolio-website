# Portfolio Website

## Overview

This is a professional portfolio website built with Flask, featuring a modern, responsive design with a contact form, email functionality, and smooth user interactions. The application showcases work and provides a way for visitors to get in touch through an integrated contact system.

## System Architecture

The application follows a traditional Flask MVC pattern with the following structure:

- **Backend**: Flask web framework with Python 3.11
- **Frontend**: HTML templates with Bootstrap 5, custom CSS, and JavaScript
- **Email Service**: Flask-Mail integration for contact form submissions
- **Deployment**: Gunicorn WSGI server with autoscale deployment target
- **Development Environment**: Replit with Nix package management

## Key Components

### Backend Components

1. **Flask Application (`app.py`, `main.py`)**
   - Main application factory with Flask-Mail configuration
   - Environment-based configuration for email settings
   - Debug logging enabled for development

2. **Routes (`routes.py`)**
   - Home page route serving the portfolio
   - Contact form handler with validation and email sending
   - Basic form validation and error handling

3. **Templates (`templates/`)**
   - Jinja2 templates with Bootstrap 5 styling
   - Responsive design with mobile-first approach
   - Base template with common layout and navigation

### Frontend Components

1. **Static Assets (`static/`)**
   - Custom CSS with CSS variables for theming
   - JavaScript for smooth scrolling and navigation
   - SVG graphics for visual elements

2. **Design System**
   - Color palette: Primary (#2C3E50), Accent (#3498DB), Highlight (#E74C3C)
   - Typography: Playfair Display for headings, Lato for body text
   - Bootstrap 5 grid system with custom components

## Data Flow

1. **Portfolio Display**: Static content rendered through Flask templates
2. **Contact Form Submission**:
   - Form data collected via POST request
   - Server-side validation performed
   - Email sent via Flask-Mail using SMTP
   - Flash messages for user feedback
   - Redirect back to contact section

## External Dependencies

### Python Packages
- `flask>=3.1.1` - Web framework
- `flask-mail>=0.10.0` - Email functionality
- `flask-sqlalchemy>=3.1.1` - Database ORM (prepared for future use)
- `email-validator>=2.2.0` - Email validation
- `gunicorn>=23.0.0` - WSGI server
- `psycopg2-binary>=2.9.10` - PostgreSQL adapter (prepared for future use)

### Frontend Libraries
- Bootstrap 5.3.0 - CSS framework
- Font Awesome 6.4.0 - Icons
- Google Fonts - Typography (Playfair Display, Lato, Source Sans Pro)

### Infrastructure
- SMTP service (Gmail by default) for email delivery
- Replit hosting platform
- Nix package manager for system dependencies

## Deployment Strategy

**Development Environment**:
- Replit-based development with hot reload
- Flask development server on port 5000
- Debug mode enabled with detailed logging

**Production Deployment**:
- Gunicorn WSGI server with autoscale deployment
- Environment variables for sensitive configuration
- Production-ready error handling and logging

**Configuration Management**:
- Environment variables for email settings
- Separate development and production secrets
- Configurable SMTP settings for different email providers

## Changelog

- June 17, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.