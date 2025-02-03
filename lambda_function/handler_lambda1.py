import boto3
import requests
import os
import yaml
from datetime import datetime

def main(event, context):
    try:
        # Carregar os links do arquivo link.yml
        links = event.get('links', {})

        # Nome do bucket S3 (usando .get() para evitar KeyError)
        s3_bucket = os.environ.get('S3_BUCKET', None)
        
        if not s3_bucket:
            raise ValueError("S3_BUCKET environment variable is missing or invalid.")

        # Lista para armazenar os resultados
        results = []

        # Iterar sobre os links e processá-los
        for name, url in links.items():
            # Nome do arquivo a ser salvo no S3, usando timestamp para nome exclusivo
            file_name = f"csv_files/{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            
            # Baixar o arquivo CSV
            response = requests.get(url)
            
            if response.status_code != 200:
                raise Exception(f"Failed to download file from {url}. Status Code: {response.status_code}")

            # Salvar o CSV no S3
            s3 = boto3.client('s3')
            s3.put_object(Bucket=s3_bucket, Key=file_name, Body=response.content)
            
            # Adicionar a URL S3 ao resultado
            results.append({
                'csv_url': f"s3://{s3_bucket}/{file_name}",
                'file_name': file_name,
                'original_link': url
            })
        
        # Retornar os resultados para a próxima função
        return {
            'files': results
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'error': str(e)
        }