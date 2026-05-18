import boto3
import os
from botocore.exceptions import NoCredentialsError

class S3Connector:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        self.bucket = os.getenv("S3_BUCKET_NAME")

    def delete_user_objects(self, user_id: str):
        """Deletes all objects prefixed with user_id."""
        prefix = f"users/{user_id}/"
        
        try:
            # List objects
            objects_to_delete = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            
            if "Contents" in objects_to_delete:
                delete_keys = [{'Key': obj['Key']} for obj in objects_to_delete["Contents"]]
                self.client.delete_objects(Bucket=self.bucket, Delete={'Objects': delete_keys})
            else:
                print(f"No objects found for {user_id}")
                
        except NoCredentialsError:
            raise Exception("AWS Credentials not found")
        except Exception as e:
            raise Exception(f"S3 Deletion failed: {str(e)}")