import os
import uuid
import requests
from typing import Optional

class StorageService:
    """
    Service for handling audio file uploads and retrievals.
    Supports Cloud Object Storage (Cloudflare R2, Supabase, AWS S3) with local storage fallback.
    """
    def __init__(self, upload_dir: str = None):
        if upload_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            upload_dir = os.path.join(base_dir, "uploads")
        
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload_file(self, file_obj, filename: str) -> str:
        """
        Uploads file to Cloud Object Storage (Cloudflare R2 / Supabase / AWS S3) or Local Storage.
        Returns the accessible URL of the uploaded audio file.
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

        # Option 1: Cloudflare R2 Object Storage
        r2_endpoint = os.environ.get("R2_ENDPOINT")
        r2_access_key = os.environ.get("R2_ACCESS_KEY_ID")
        r2_secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
        r2_bucket = os.environ.get("R2_BUCKET_NAME", "medlio-voice-feedback")

        if r2_endpoint and r2_access_key and r2_secret_key:
            try:
                import boto3
                s3_client = boto3.client(
                    's3',
                    endpoint_url=r2_endpoint,
                    aws_access_key_id=r2_access_key,
                    aws_secret_access_key=r2_secret_key,
                    region_name='auto'
                )
                s3_client.put_object(
                    Bucket=r2_bucket,
                    Key=unique_filename,
                    Body=content,
                    ContentType='audio/wav'
                )
                
                r2_public_base = os.environ.get("R2_PUBLIC_URL")
                if r2_public_base:
                    r2_url = f"{r2_public_base.rstrip('/')}/{unique_filename}"
                else:
                    # Generate a presigned GET URL for audio playback
                    r2_url = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': r2_bucket, 'Key': unique_filename},
                        ExpiresIn=604800  # 7 days
                    )
                print(f"Uploaded to Cloudflare R2 Object Storage: {r2_url}")
                return r2_url
            except Exception as e:
                print(f"Cloudflare R2 upload error: {str(e)}")

        # Option 2: Supabase Storage
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
        supabase_bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "medlio-feedback")

        if supabase_url and supabase_key and not supabase_url.startswith("your_"):
            try:
                upload_endpoint = f"{supabase_url.rstrip('/')}/storage/v1/object/{supabase_bucket}/{unique_filename}"
                headers = {
                    "Authorization": f"Bearer {supabase_key}",
                    "apiKey": supabase_key,
                    "Content-Type": "audio/wav",
                    "x-upsert": "true"
                }
                res = requests.post(upload_endpoint, headers=headers, data=content, timeout=15)
                if res.status_code in (200, 201):
                    public_url = f"{supabase_url.rstrip('/')}/storage/v1/object/public/{supabase_bucket}/{unique_filename}"
                    print(f"Uploaded to Supabase Cloud Storage: {public_url}")
                    return public_url
            except Exception as e:
                print(f"Supabase storage upload error: {str(e)}")

        # Fallback: Local Server Storage URL
        base_url = os.environ.get("BASE_URL", "http://localhost:5000")
        return f"{base_url}/uploads/{unique_filename}"

    def get_file_path(self, url_or_filename: str) -> str:
        """
        Returns absolute local file path from URL or filename.
        """
        clean_url = url_or_filename.split("?")[0]
        filename = os.path.basename(clean_url)
        return os.path.join(self.upload_dir, filename)

    def delete_file(self, url: str) -> bool:
        """
        Deletes a file from storage given its URL.
        """
        try:
            clean_url = url.split("?")[0]
            filename = os.path.basename(clean_url)
            filepath = os.path.join(self.upload_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

            # Delete from Cloudflare R2 if configured
            r2_endpoint = os.environ.get("R2_ENDPOINT")
            r2_access_key = os.environ.get("R2_ACCESS_KEY_ID")
            r2_secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
            r2_bucket = os.environ.get("R2_BUCKET_NAME", "medlio-voice-feedback")

            if r2_endpoint and r2_access_key and r2_secret_key:
                import boto3
                s3_client = boto3.client(
                    's3',
                    endpoint_url=r2_endpoint,
                    aws_access_key_id=r2_access_key,
                    aws_secret_access_key=r2_secret_key,
                    region_name='auto'
                )
                s3_client.delete_object(Bucket=r2_bucket, Key=filename)

            return True
        except Exception as e:
            print(f"Delete file error: {str(e)}")
            return False

storage_service = StorageService()
