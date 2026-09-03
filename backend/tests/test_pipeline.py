import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.pool import StaticPool
from app import create_app
from app.models import db, User, Feedback
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'connect_args': {'check_same_thread': False},
            'poolclass': StaticPool
        },
        'TESTING': True
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_user(app):
    with app.app_context():
        u = User(name="Admin", email="admin@example.com", password_hash="hashed", role="ADMIN")
        db.session.add(u)
        db.session.commit()
        db.session.refresh(u)
        return u

def test_admin_list_feedback(client, admin_user, app):
    with app.app_context():
        token = create_access_token(identity=str(admin_user.id), additional_claims={'role': 'ADMIN'})
        f = Feedback(user_id=admin_user.id, audio_url="url", filename="file.wav", status="COMPLETED")
        db.session.add(f)
        db.session.commit()

    resp = client.get('/admin/feedback', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1

def test_pipeline_processing_success(app, admin_user):
    with app.app_context():
        with patch('app.routes.user_routes.stt_service.transcribe', return_value=("Hello world", "en")), \
             patch('app.routes.user_routes.ai_service.analyze_sentiment', return_value={
                 "sentiment": "POSITIVE", "confidence": 0.9, "summary": "Great", "key_topics": [], "urgency": "LOW"
             }):

            f = Feedback(user_id=admin_user.id, audio_url="url", filename="file.wav", status="UPLOADED")
            db.session.add(f)
            db.session.commit()

            from app.routes.user_routes import process_voice_feedback
            process_voice_feedback(app, str(f.id))

            db.session.refresh(f)
            assert f.status == 'COMPLETED'
            assert f.transcription.text == "Hello world"
            assert f.sentiment.sentiment == "POSITIVE"
