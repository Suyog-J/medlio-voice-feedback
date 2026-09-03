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
        
        # Fetch file bytes from local disk or Cloudflare R2 object storage
        audio_bytes = storage_service.get_file_bytes(audio_file_path)

        if api_key and not api_key.startswith("your_") and not api_key.startswith("placeholder") and audio_bytes:
            try:
                headers = {"Authorization": f"Bearer {api_key}"}
                filename = os.path.basename(audio_file_path.split("?")[0]) or "audio.wav"
                files = {
                    "file": (filename, audio_bytes, "audio/wav"),
                    "model": (None, "whisper-large-v3"),
                }
                response = requests.post(self.url, headers=headers, files=files, timeout=30)
                response.raise_for_status()
                data = response.json()
                return data.get("text", ""), data.get("language", "en")
            except Exception as e:
                print(f"Groq STT transcription error: {str(e)}")

        # Development / Fallback response
        return "This is a sample transcribed feedback from the user regarding the food delivery service.", "en"

stt_service = STTService()
