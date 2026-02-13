from config.config import get_client

s3 = get_client()
bucket = "my-first-bucket"
object_name = "file.txt" # The name inside Ceph
dest_path = "downloaded_file.txt" # Where it goes on Windows

try:
    s3.download_file(bucket, object_name, dest_path)
    print(f" {object_name} downloaded to {dest_path}!")
except Exception as e:
    print(f" Download failed: {e}")