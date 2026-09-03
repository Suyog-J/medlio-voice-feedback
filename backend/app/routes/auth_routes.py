from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify(msg='Missing email or password'), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify(msg='User already exists'), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        name=data.get('name', 'Unknown'),
        email=data['email'],
        password_hash=hashed_password,
        role=data.get('role', 'USER')
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify(msg='User registered successfully'), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if user and check_password_hash(user.password_hash, data.get('password')):
        # Include role in the claims
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role}
        )
        return jsonify(access_token=access_token, role=user.role), 200

    return jsonify(msg='Invalid email or password'), 401
