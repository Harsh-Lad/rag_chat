import boto3
from botocore.exceptions import ClientError
from io import BytesIO
from urllib.parse import urlparse

class S3Client:
    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name):
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def download_file(self, file_url):
        try:
            parsed_url = urlparse(file_url)
            file_key = parsed_url.path.lstrip('/')
            print(f"Extracted file key: {file_key}")
            file_obj = BytesIO()
            self.s3.download_fileobj(self.bucket_name, file_key, file_obj)
            file_obj.seek(0)  
            print(f"File downloaded successfully to memory")
            return file_obj
        except ClientError as e:
            print(f"Error downloading file: {e}")
            return None

    def upload_file(self, file_obj, file_key):
        try:
            
            file_obj.seek(0)  
            self.s3.upload_fileobj(file_obj, self.bucket_name, file_key)
            print(f"File uploaded successfully to S3")          
            s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"
            return s3_url
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return None
