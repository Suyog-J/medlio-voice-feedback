import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from ..models import db, Feedback, User
from ..auth import admin_required
from ..services.storage_service import storage_service

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/feedback', methods=['GET'])
@jwt_required()
@admin_required()
def list_all_feedback():
    # Eager load user to eliminate N+1 queries
    feedbacks = Feedback.query.options(joinedload(Feedback.user)).all()
    results = []
    for f in feedbacks:
        results.append({
            "id": str(f.id),
            "user_name": f.user.name if f.user else "Unknown",
            "status": f.status,
            "date": f.created_at.isoformat()
        })
    return jsonify(results), 200

@admin_bp.route('/feedback/<id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_feedback_detail(id):
    feedback_uuid = uuid.UUID(id) if isinstance(id, str) else id
    feedback = db.session.get(Feedback, feedback_uuid)
    if not feedback:
        return jsonify(msg='Feedback not found'), 404

    # Generate fresh presigned URL dynamically for audio playback
    playback_url = storage_service.get_presigned_url(feedback.audio_url)

    return jsonify({
        "feedback": {
            "id": str(feedback.id),
            "user_id": str(feedback.user_id),
            "audio_url": playback_url,
            "status": feedback.status,
            "date": feedback.created_at.isoformat()
        },
        "transcription": {
            "text": feedback.transcription.text if feedback.transcription else None,
            "language": feedback.transcription.language if feedback.transcription else None
        },
        "sentiment": {
            "sentiment": feedback.sentiment.sentiment if feedback.sentiment else None,
            "confidence": feedback.sentiment.confidence if feedback.sentiment else None,
            "summary": feedback.sentiment.summary if feedback.sentiment else None,
            "key_topics": feedback.sentiment.key_topics if feedback.sentiment else None,
            "urgency": feedback.sentiment.urgency if feedback.sentiment else None
        }
    }), 200

@admin_bp.route('/feedback/<id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_feedback(id):
    feedback_uuid = uuid.UUID(id) if isinstance(id, str) else id
    feedback = db.session.get(Feedback, feedback_uuid)
    if not feedback:
        return jsonify(msg='Feedback not found'), 404

    # Delete audio file from storage
    storage_service.delete_file(feedback.audio_url)

    db.session.delete(feedback)
    db.session.commit()

    return '', 204
