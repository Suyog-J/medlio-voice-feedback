import os
import requests
from typing import Tuple, Optional
from .storage_service import storage_service

class STTService:
    """
    Service for Speech-to-Text transcription using Groq Whisper Large V3.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.url = "https://api.groq.com/openai/v1/audio/transcriptions"

    def transcribe(self, audio_file_path: str) -> Tuple[str, str]:
        """
        Transcribes an audio file using Groq Whisper Large V3.
        Returns a tuple of (transcript_text, detected_language).
        """
        api_key = self.api_key or os.environ.get("GROQ_API_KEY")
        
        # Resolve path if URL is passed
        local_path = storage_service.get_file_path(audio_file_path) if (audio_file_path.startswith("http://") or audio_file_path.startswith("https://")) else audio_file_path

        if api_key and not api_key.startswith("your_") and not api_key.startswith("placeholder") and os.path.exists(local_path):
            try:
                headers = {"Authorization": f"Bearer {api_key}"}
                with open(local_path, "rb") as f:
                    files = {
                        "file": f,
                        "model": (None, "whisper-large-v3"),
                    }
                    response = requests.post(self.url, headers=headers, files=files)
                    response.raise_for_status()
                    data = response.json()
                    return data.get("text", ""), data.get("language", "en")
            except Exception as e:
                print(f"Groq STT transcription error: {str(e)}")

        # Development / Fallback response
        return "This is a sample transcribed feedback from the user regarding the food delivery service.", "en"

stt_service = STTService()
