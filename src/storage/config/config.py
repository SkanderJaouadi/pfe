import boto3
from botocore.client import Config


ACCESS_KEY = 'OK2J2KRA0WIKGQNK8QEP'
SECRET_KEY = '6kJtmVwCJxnAlelP0RCqjSv16fg9ARdJlSyfDdCA'
ENDPOINT = 'http://172.20.70.79:8000/' 

def get_client():
    return boto3.client(
        's3',
        endpoint_url=ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )