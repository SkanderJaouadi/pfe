from config.config import get_client

s3 = get_client()
response = s3.list_buckets()

print("\n--- Current Buckets ---")
for b in response['Buckets']:
    print(f"Bucket: {b['Name']}")
    # List files inside each bucket
    objs = s3.list_objects_v2(Bucket=b['Name'])
    if 'Contents' in objs:
        for obj in objs['Contents']:
            print(f"  └─ File: {obj['Key']} ({obj['Size']} bytes)")