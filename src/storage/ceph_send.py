from config.config import get_client
import os

s3 = get_client()
bucket = "docs"
file_path = "../../data/doc/recu.pdf" 
file_name = os.path.basename(file_path)

try:
    s3.upload_file(file_path, bucket, file_name)
    print(f" {file_name} uploaded to {bucket}!")
except Exception as e:
    print(f" Upload failed: {e}")