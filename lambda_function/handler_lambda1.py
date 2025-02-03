import boto3
import requests
import os
import yaml
from datetime import datetime

def main(event, context):
    try:
        links = event.get('links', {})
        s3_bucket = os.environ.get('S3_BUCKET', None)
        
        if not s3_bucket:
            raise ValueError("S3_BUCKET environment variable is missing or invalid.")

        results = []

        for name, url in links.items():
            file_name = f"csv_files/{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            
            response = requests.get(url)
            
            if response.status_code != 200:
                raise Exception(f"Failed to download file from {url}. Status Code: {response.status_code}")

            s3 = boto3.client('s3')
            s3.put_object(Bucket=s3_bucket, Key=file_name, Body=response.content)
            
            results.append({
                'csv_url': f"s3://{s3_bucket}/{file_name}",
                'file_name': file_name,
                'original_link': url
            })
        
        return {
            'files': results
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'error': str(e)
        }