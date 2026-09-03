import os
import uuid
import requests
from typing import Optional

class StorageService:
    """
    Service for handling audio file uploads and retrievals.
    Supports Cloud Object Storage (Supabase Storage, AWS S3) with local storage fallback.
    """
    def __init__(self, upload_dir: str = None):
        if upload_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            upload_dir = os.path.join(base_dir, "uploads")
        
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload_file(self, file_obj, filename: str) -> str:
        """
        Uploads file to Cloud Object Storage (Supabase/S3) or Local Storage.
        Returns the public URL of the uploaded audio file.
        """
        ext = os.path.splitext(filename)[1] if filename else ".wav"
        if not ext:
            ext = ".wav"
        unique_filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(self.upload_dir, unique_filename)

        # Read content bytes
        if hasattr(file_obj, 'read'):
            content = file_obj.read()
            file_obj.seek(0) if hasattr(file_obj, 'seek') else None
        elif hasattr(file_obj, 'save'):
            file_obj.save(filepath)
            with open(filepath, 'rb') as f:
                content = f.read()
        else:
            content = b""

        # Always save local copy for STT service processing
        with open(filepath, 'wb') as f:
            f.write(content)

        # Option 1: Supabase Cloud Object Storage
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
        bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "medlio-feedback")

        if supabase_url and supabase_key and not supabase_url.startswith("your_"):
            try:
                upload_endpoint = f"{supabase_url.rstrip('/')}/storage/v1/object/{bucket}/{unique_filename}"
                headers = {
                    "Authorization": f"Bearer {supabase_key}",
                    "apiKey": supabase_key,
                    "Content-Type": "audio/wav",
                    "x-upsert": "true"
                }
                res = requests.post(upload_endpoint, headers=headers, data=content, timeout=15)
                if res.status_code in (200, 201):
                    public_url = f"{supabase_url.rstrip('/')}/storage/v1/object/public/{bucket}/{unique_filename}"
                    print(f"Uploaded to Supabase Cloud Storage: {public_url}")
                    return public_url
                else:
                    print(f"Supabase upload warning ({res.status_code}): {res.text}")
            except Exception as e:
                print(f"Supabase storage upload error: {str(e)}")

        # Option 2: AWS S3 Cloud Object Storage
        s3_bucket = os.environ.get("AWS_S3_BUCKET")
        aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        if s3_bucket and aws_access_key and aws_secret_key and not s3_bucket.startswith("your_"):
            try:
                import boto3
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=os.environ.get("AWS_REGION", "us-east-1")
                )
                s3_client.put_object(Bucket=s3_bucket, Key=unique_filename, Body=content, ContentType='audio/wav')
                s3_url = f"https://{s3_bucket}.s3.amazonaws.com/{unique_filename}"
                print(f"Uploaded to AWS S3 Object Storage: {s3_url}")
                return s3_url
            except Exception as e:
                print(f"AWS S3 upload error: {str(e)}")

        # Fallback: Local Server Storage URL
        base_url = os.environ.get("BASE_URL", "http://localhost:5000")
        return f"{base_url}/uploads/{unique_filename}"

    def get_file_path(self, url_or_filename: str) -> str:
        """
        Returns absolute local file path from URL or filename.
        """
        filename = os.path.basename(url_or_filename)
        return os.path.join(self.upload_dir, filename)

    def delete_file(self, url: str) -> bool:
        """
        Deletes a file from storage given its URL.
        """
        try:
            filepath = self.get_file_path(url)
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        except Exception:
            return False

storage_service = StorageService()
