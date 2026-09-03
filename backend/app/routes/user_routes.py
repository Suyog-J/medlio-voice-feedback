import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from threading import Thread
from ..models import db, Feedback, Transcription, Sentiment
from ..services.storage_service import storage_service
from ..services.stt_service import stt_service
from ..services.ai_service import ai_service
from ..auth import user_required

user_bp = Blueprint('user', __name__, url_prefix='/user')

def process_voice_feedback(app, feedback_id):
    """Background task to process audio -> STT -> Sentiment."""
    with app.app_context():
        try:
            feedback_uuid = uuid.UUID(feedback_id) if isinstance(feedback_id, str) else feedback_id
            feedback = db.session.get(Feedback, feedback_uuid)
            if not feedback: return

            f_id = feedback.id

            # Set status to PROCESSING immediately before calling STT service
            feedback.status = 'PROCESSING'
            db.session.commit()

            # 1. Speech-to-Text
            text, lang = stt_service.transcribe(feedback.audio_url)

            transcription = Transcription(feedback_id=f_id, text=text, language=lang)
            db.session.add(transcription)
            db.session.commit()

            # 2. Sentiment Analysis
            analysis = ai_service.analyze_sentiment(text)

            sentiment = Sentiment(
                feedback_id=f_id,
                sentiment=analysis['sentiment'],
                confidence=analysis['confidence'],
                summary=analysis['summary'],
                key_topics=analysis['key_topics'],
                urgency=analysis['urgency']
            )
            db.session.add(sentiment)

            feedback = db.session.get(Feedback, f_id)
            if feedback:
                feedback.status = 'COMPLETED'
            db.session.commit()

        except Exception as e:
            err_msg = str(e)
            print(f"Error processing feedback {feedback_id}: {err_msg}")
            feedback_uuid = uuid.UUID(feedback_id) if isinstance(feedback_id, str) else feedback_id
            feedback = db.session.get(Feedback, feedback_uuid)
            if feedback:
                feedback.status = 'FAILED'
                feedback.error_message = err_msg
                db.session.commit()

@user_bp.route('/feedback', methods=['POST'])
@jwt_required()
@user_required()
def upload_feedback():
    user_id = get_jwt_identity()
    if 'file' not in request.files:
        return jsonify(msg='No file uploaded'), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify(msg='No selected file'), 400

    # Validate audio MIME type & extension
    allowed_mimetypes = {'audio/wav', 'audio/webm', 'audio/mp3', 'audio/mpeg', 'audio/ogg', 'audio/mp4', 'audio/x-wav', 'audio/m4a', 'application/octet-stream'}
    allowed_extensions = {'.wav', '.webm', '.mp3', '.ogg', '.mp4', '.m4a', '.aac'}
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ''
    is_audio = (file.mimetype and (file.mimetype.startswith('audio/') or file.mimetype in allowed_mimetypes)) or (ext in allowed_extensions)

    if not is_audio:
        return jsonify(msg='Invalid file type. Only audio files are allowed.'), 400

    # Validate file size (15MB limit)
    MAX_FILE_SIZE = 15 * 1024 * 1024
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_FILE_SIZE:
        return jsonify(msg='File size exceeds maximum allowed limit of 15MB.'), 400

    audio_url = storage_service.upload_file(file, file.filename)

    new_feedback = Feedback(
        user_id=uuid.UUID(user_id),
        audio_url=audio_url,
        filename=file.filename,
        status='UPLOADED'
    )
    db.session.add(new_feedback)
    db.session.commit()

    # Start background processing
    app_obj = current_app._get_current_object()
    if current_app.config.get('TESTING'):
        process_voice_feedback(app_obj, str(new_feedback.id))
    else:
        thread = Thread(target=process_voice_feedback, args=(app_obj, str(new_feedback.id)))
        thread.start()

    return jsonify(id=str(new_feedback.id), status=new_feedback.status), 201

@user_bp.route('/feedback', methods=['GET'])
@jwt_required()
@user_required()
def list_my_feedback():
    user_id = get_jwt_identity()
    user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
    feedbacks = Feedback.query.filter_by(user_id=user_uuid).all()

    return jsonify([{
        "id": str(f.id),
        "status": f.status,
        "date": f.created_at.isoformat()
    } for f in feedbacks]), 200

@user_bp.route('/feedback/<id>', methods=['GET'])
@jwt_required()
@user_required()
def get_feedback_detail(id):
    feedback_uuid = uuid.UUID(id) if isinstance(id, str) else id
    feedback = db.session.get(Feedback, feedback_uuid)
    if not feedback or str(feedback.user_id) != get_jwt_identity():
        return jsonify(msg='Feedback not found or unauthorized'), 404

    return jsonify({
        "feedback": {
            "id": str(feedback.id),
            "status": feedback.status,
            "error_message": feedback.error_message if feedback.status == 'FAILED' else None,
            "date": feedback.created_at.isoformat()
        },
        "transcription": feedback.transcription.text if feedback.transcription else None,
        "sentiment": {
            "sentiment": feedback.sentiment.sentiment if feedback.sentiment else None,
            "confidence": feedback.sentiment.confidence if feedback.sentiment else None,
            "summary": feedback.sentiment.summary if feedback.sentiment else None,
        }
    }), 200
