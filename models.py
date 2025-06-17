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
    
    return User, Project