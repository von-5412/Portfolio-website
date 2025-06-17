from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Models will be defined with db imported from app context
def init_models(db):
    """Initialize models with database instance"""
    
    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(64), unique=True, nullable=False)
        password_hash = db.Column(db.String(256))
        is_admin = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

    class Project(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text, nullable=False)
        thumbnail_url = db.Column(db.String(500))
        project_url = db.Column(db.String(500))
        github_url = db.Column(db.String(500))
        technologies = db.Column(db.String(500))  # Comma-separated tech stack
        status = db.Column(db.String(50), default='🚀 Live Project')  # Live Project, Client Project, Side Project, etc.
        rating = db.Column(db.Float, default=0.0)
        users_count = db.Column(db.String(20))  # e.g., "2.3k users"
        metrics = db.Column(db.String(200))  # e.g., "300% ROI, 6 weeks"
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        is_featured = db.Column(db.Boolean, default=True)

        def get_tech_list(self):
            """Return technologies as a list"""
            if self.technologies:
                return [tech.strip() for tech in self.technologies.split(',')]
            return []

        def get_metrics_list(self):
            """Return metrics as a list"""
            if self.metrics:
                return [metric.strip() for metric in self.metrics.split(',')]
            return []

        def to_dict(self):
            return {
                'id': self.id,
                'title': self.title,
                'description': self.description,
                'thumbnail_url': self.thumbnail_url,
                'project_url': self.project_url,
                'github_url': self.github_url,
                'technologies': self.get_tech_list(),
                'status': self.status,
                'rating': self.rating,
                'users_count': self.users_count,
                'metrics': self.get_metrics_list(),
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'is_featured': self.is_featured
            }

    class Contact(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), nullable=False)
        subject = db.Column(db.String(200), nullable=False)
        message = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        is_read = db.Column(db.Boolean, default=False)

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'email': self.email,
                'subject': self.subject,
                'message': self.message,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'is_read': self.is_read
            }

    class Visitor(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        ip_address = db.Column(db.String(45), nullable=False)
        user_agent = db.Column(db.Text)
        browser = db.Column(db.String(100))
        os = db.Column(db.String(100))
        device = db.Column(db.String(100))
        country = db.Column(db.String(100))
        city = db.Column(db.String(100))
        referrer = db.Column(db.String(500))
        page_visited = db.Column(db.String(200))
        visit_duration = db.Column(db.Integer)  # in seconds
        screen_resolution = db.Column(db.String(20))
        language = db.Column(db.String(10))
        visit_count = db.Column(db.Integer, default=1)
        first_visit = db.Column(db.DateTime, default=datetime.utcnow)
        last_visit = db.Column(db.DateTime, default=datetime.utcnow)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        # Enhanced tracking fields
        accept_encoding = db.Column(db.String(200))  # Compression preferences
        connection_type = db.Column(db.String(50))   # keep-alive, close, etc.
        dnt_enabled = db.Column(db.Boolean, default=False)  # Do Not Track preference
        x_forwarded_for = db.Column(db.String(200))  # Proxy chain
        x_real_ip = db.Column(db.String(45))         # Real IP behind proxy
        host = db.Column(db.String(100))             # Host header
        session_start = db.Column(db.DateTime)       # Session start time
        session_duration = db.Column(db.Integer)     # Session length in seconds
        timezone_offset = db.Column(db.String(10))   # UTC offset
        page_load_time = db.Column(db.Integer)       # Page load time in ms
        viewport_size = db.Column(db.String(20))     # Browser viewport size
        color_depth = db.Column(db.Integer)          # Screen color depth
        pixel_ratio = db.Column(db.Float)            # Device pixel ratio
        online_status = db.Column(db.Boolean)        # Navigator.onLine
        cookies_enabled = db.Column(db.Boolean)      # Cookie support
        local_storage = db.Column(db.Boolean)        # LocalStorage support
        session_storage = db.Column(db.Boolean)      # SessionStorage support
        webgl_vendor = db.Column(db.String(100))     # WebGL renderer info
        webgl_renderer = db.Column(db.String(200))
        cpu_cores = db.Column(db.Integer)            # Hardware concurrency
        memory_size = db.Column(db.Integer)          # Device memory (GB)
        battery_level = db.Column(db.Float)          # Battery level (0-1)
        charging_status = db.Column(db.Boolean)      # Is charging
        network_type = db.Column(db.String(50))      # Connection type (4g, wifi, etc.)
        network_speed = db.Column(db.String(20))     # Effective connection type

        def to_dict(self):
            return {
                'id': self.id,
                'ip_address': self.ip_address,
                'user_agent': self.user_agent,
                'browser': self.browser,
                'os': self.os,
                'device': self.device,
                'country': self.country,
                'city': self.city,
                'referrer': self.referrer,
                'page_visited': self.page_visited,
                'visit_duration': self.visit_duration,
                'screen_resolution': self.screen_resolution,
                'language': self.language,
                'visit_count': self.visit_count,
                'first_visit': self.first_visit.isoformat() if self.first_visit else None,
                'last_visit': self.last_visit.isoformat() if self.last_visit else None,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    class LoginAttempt(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        ip_address = db.Column(db.String(45), nullable=False)
        username = db.Column(db.String(64))
        success = db.Column(db.Boolean, default=False)
        user_agent = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        def to_dict(self):
            return {
                'id': self.id,
                'ip_address': self.ip_address,
                'username': self.username,
                'success': self.success,
                'user_agent': self.user_agent,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
    
    return User, Project, Contact, Visitor, LoginAttempt