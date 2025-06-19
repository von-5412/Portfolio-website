from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import init_models  # ← where your init_models is defined

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
User, Project, Contact, Visitor, LoginAttempt = init_models(db)

with app.app_context():
    db.create_all()
    print("✅ Tables created.")
