import os
import json
import requests
from typing import Dict, Any, Optional

class AIService:
    """
    Service for Transcript Analysis and Sentiment Classification using Gemini Flash.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the sentiment of a transcript and returns structured JSON data.
        """
        api_key = self.api_key or os.environ.get("GEMINI_API_KEY")

        if api_key and not api_key.startswith("your_") and not api_key.startswith("placeholder"):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                prompt = (
                    "Analyze the sentiment of the following customer feedback transcript. "
                    "Return ONLY a raw valid JSON object without markdown code blocks, containing keys: "
                    '"sentiment" ("POSITIVE", "NEUTRAL", "NEGATIVE"), '
                    '"confidence" (float between 0.0 and 1.0), '
                    '"summary" (string brief summary), '
                    '"key_topics" (array of strings), '
                    '"urgency" ("LOW", "MEDIUM", "HIGH").\n\n'
                    f"Transcript: {text}"
                )
                headers = {"Content-Type": "application/json"}
                body = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                response = requests.post(url, headers=headers, json=body, timeout=15)
                response.raise_for_status()
                result_json = response.json()
                raw_text = result_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Clean codeblock wrappers if present
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("\n", 1)[1]
                    if raw_text.endswith("```"):
                        raw_text = raw_text.rsplit("```", 1)[0]
                
                parsed = json.loads(raw_text)
                key_topics = parsed.get("key_topics", [])
                if isinstance(key_topics, str):
                    key_topics = [key_topics]

                return {
                    "sentiment": parsed.get("sentiment", "NEUTRAL"),
                    "confidence": float(parsed.get("confidence", 0.9)),
                    "summary": parsed.get("summary", "Transcript analyzed."),
                    "key_topics": key_topics,
                    "urgency": parsed.get("urgency", "LOW")
                }
            except Exception as e:
                print(f"Gemini API sentiment analysis error: {str(e)}")

        # Development / Fallback mock response
        return {
            "sentiment": "POSITIVE",
            "confidence": 0.95,
            "summary": "User is very happy with the quality of food and the promptness of delivery.",
            "key_topics": ["Food Quality", "Delivery Speed"],
            "urgency": "LOW"
        }

ai_service = AIService()
