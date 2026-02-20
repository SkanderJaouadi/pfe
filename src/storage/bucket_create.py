from config.config import get_client

s3 = get_client()
bucket_name = input("Enter bucket name to create: ")

try:
    s3.create_bucket(Bucket=bucket_name)
    print(f" Bucket '{bucket_name}' created successfully!")
except Exception as e:
    print(f" Error: {e}")