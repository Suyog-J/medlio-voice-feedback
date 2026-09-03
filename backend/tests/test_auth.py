import io
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
def user(app):
    with app.app_context():
        u = User(name="Test User", email="test@example.com", password_hash="hashed", role="USER")
        db.session.add(u)
        db.session.commit()
        db.session.refresh(u)
        return u

def test_register(client):
    resp = client.post('/auth/register', json={"name": "Test", "email": "reg@example.com", "password": "password"})
    assert resp.status_code == 201

def test_login(client, user):
    with patch('app.routes.auth_routes.check_password_hash', return_value=True):
        resp = client.post('/auth/login', json={"email": user.email, "password": "password"})
        assert resp.status_code == 200
        assert 'access_token' in resp.get_json()

def test_upload_feedback_unauthorized(client):
    resp = client.post('/user/feedback', data={"file": (io.BytesIO(b"audio data"), 'test.wav')})
    assert resp.status_code == 401

def test_upload_feedback_user(client, user, app):
    with app.app_context():
        token = create_access_token(identity=str(user.id), additional_claims={'role': 'USER'})

    with patch('app.routes.user_routes.storage_service.upload_file', return_value="http://mock/audio.wav"):
        resp = client.post('/user/feedback',
                           headers={"Authorization": f"Bearer {token}"},
                           data={"file": (io.BytesIO(b"audio data"), 'test.wav')})
        assert resp.status_code == 201
        assert resp.get_json()['status'] == 'UPLOADED'

def test_admin_access_denied_for_user(client, user, app):
    with app.app_context():
        token = create_access_token(identity=str(user.id), additional_claims={'role': 'USER'})

    resp = client.get('/admin/feedback', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
