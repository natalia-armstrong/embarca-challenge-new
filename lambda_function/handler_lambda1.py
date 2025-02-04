import boto3
import requests
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_s3_bucket() -> str:
    s3_bucket = os.environ.get('S3_BUCKET')
    if not s3_bucket:
        raise ValueError("S3_BUCKET environment variable is missing or invalid.")
    logger.info(f"Bucket S3 configurado: {s3_bucket}")
    return s3_bucket

def download_file(url: str, name: str) -> tuple[str, bytes]:
    logger.info(f"Baixando o arquivo: {url}")
    file_name = f"csv_files/{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download file from {url}. Status Code: {response.status_code}")
    logger.info(f"Arquivo {name} baixado com sucesso.")
    
    content = response.content.decode(response.apparent_encoding).encode('utf-8')
    return file_name, response.content

def upload_to_s3(s3_client, bucket: str, file_name: str, content: bytes):
    s3_client.put_object(Bucket=bucket, Key=file_name, Body=content)
    logger.info(f"Arquivo {file_name} enviado para o S3.")

def process_files(link: dict, s3_bucket: str) -> list:
    s3 = boto3.client('s3')
    results = []

    for name, url in link.items():
        file_name, content = download_file(url, name)
        upload_to_s3(s3, s3_bucket, file_name, content)
        results.append({
            'csv_url': f"s3://{s3_bucket}/{file_name}",
            'file_name': file_name,
            'original_link': url
        })
    
    return results

def main(event, context):
    try:
        logger.info("Iniciando função...")
        link = event.get('link', {})
        if not link:
            raise ValueError("Nenhum link fornecido no evento.")
        
        s3_bucket = validate_s3_bucket()
        results = process_files(link, s3_bucket)

        return {'files': results}

    except Exception as e:
        return {'error': str(e)}