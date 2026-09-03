from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'USER' or 'ADMIN'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    feedback = db.relationship('Feedback', backref='user', lazy=True)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    audio_url = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='UPLOADED') # 'UPLOADED', 'PROCESSING', 'COMPLETED', 'FAILED'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transcription = db.relationship('Transcription', backref='feedback', uselist=False, cascade='all, delete-orphan')
    sentiment = db.relationship('Sentiment', backref='feedback', uselist=False, cascade='all, delete-orphan')

class Transcription(db.Model):
    __tablename__ = 'transcriptions'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feedback_id = db.Column(UUID(as_uuid=True), db.ForeignKey('feedback.id'), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sentiment(db.Model):
    __tablename__ = 'sentiment'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feedback_id = db.Column(UUID(as_uuid=True), db.ForeignKey('feedback.id'), unique=True, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False) # 'POSITIVE', 'NEUTRAL', 'NEGATIVE'
    confidence = db.Column(db.Float, nullable=False)
    summary = db.Column(db.Text)
    key_topics = db.Column(db.JSON) # Store as list of strings
    urgency = db.Column(db.String(20)) # 'LOW', 'MEDIUM', 'HIGH'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
