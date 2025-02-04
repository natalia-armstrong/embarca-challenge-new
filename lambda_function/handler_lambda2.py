import boto3
import csv
from datetime import datetime
from io import StringIO
import chardet
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker
import logging

# Configuração básica do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def process_csv(bucket_name, file_key):
    try:
        logger.info(f"Buscando arquivo {file_key} no bucket {bucket_name}.")
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        file_content_bytes = response['Body'].read()
        
        detected_encoding = chardet.detect(file_content_bytes)['encoding']
        logger.info(f"Encoding detectado: {detected_encoding}")
        file_content = file_content_bytes.decode(detected_encoding)

        csv_data = StringIO(file_content)
        reader = csv.DictReader(csv_data, delimiter=";")
        
        logger.info(f"Arquivo {file_key} processado com sucesso.")
        return list(reader)

    except Exception as e:
        raise ValueError(f"Erro ao processar CSV: {str(e)}")

def calculate_deaths(rows):
    vehicle_columns = ["automovel", "bicicleta", "caminhao", "moto", "onibus"]
    vehicle_deaths = {vehicle: 0 for vehicle in vehicle_columns}
    total_deaths = 0

    for row in rows:
        total_deaths += int(row["mortos"])
        for vehicle in vehicle_columns:
            vehicle_deaths[vehicle] += int(row.get(vehicle, 0))

    insert_data = []
    for vehicle, deaths in vehicle_deaths.items():
        insert_data.append({
            "created_at": datetime.now(),
            "road_name": rows[0]["trecho"],
            "vehicle": vehicle,
            "number_deaths": deaths
        })
    
    logger.info(f"Dados de mortes calculados: {insert_data}")
    return insert_data

def save_to_db(insert_data, db_url):
    try:
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        metadata = MetaData()
        accident_deaths = Table('accident_deaths', metadata,
            Column('created_at', String),
            Column('road_name', String),
            Column('vehicle', String),
            Column('number_deaths', Integer)
        )
        
        metadata.create_all(engine)

        logger.info("Inserindo dados no banco de dados.")
        for data in insert_data:
            session.execute(accident_deaths.insert().values(data))

        session.commit()
        logger.info("Dados salvos com sucesso no banco de dados.")
        session.close()

    except Exception as e:
        raise ValueError(f"Erro ao salvar dados no banco de dados: {str(e)}")

def process_and_save(file_info, db_url):
    try:
        bucket_name = file_info["csv_url"].split("/")[2]
        file_key = "/".join(file_info["csv_url"].split("/")[3:])
        
        logger.info(f"Processando arquivo {file_key} do bucket {bucket_name}.")
        rows = process_csv(bucket_name, file_key)
        insert_data = calculate_deaths(rows)
        save_to_db(insert_data, db_url)

    except Exception as e:
        raise ValueError(f"Erro ao processar e salvar dados: {str(e)}")
                         

def main(event, context):
    db_url = os.getenv('DB_URL')

    if not db_url:
        raise ValueError("DB_URL não configurado.")

    for file_info in event.get('files', []):
        logger.info(f"Processando entrada do arquivo: {file_info}")
        process_and_save(file_info, db_url)