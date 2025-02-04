import boto3
import csv
from datetime import datetime
from io import StringIO
import chardet
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, inspect
from sqlalchemy.orm import sessionmaker

load_dotenv()

def process_csv(bucket_name, file_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content_bytes = response['Body'].read()
    detected_encoding = chardet.detect(file_content_bytes)['encoding']
    file_content = file_content_bytes.decode(detected_encoding)

    csv_data = StringIO(file_content)
    reader = csv.DictReader(csv_data, delimiter=";")
    
    return list(reader)

def calculate_deaths(rows):
    vehicle_columns = ["automovel", "bicicleta", "caminhao", "moto", "onibus"]
    vehicle_deaths = {vehicle: 0 for vehicle in vehicle_columns}
    total_deaths = 0

    for row in rows:
        total_deaths += int(row["mortos"])
        for vehicle in vehicle_columns:
            vehicle_deaths[vehicle] += int(row.get(vehicle, 0))

    print(f"Total de mortes: {total_deaths}")
    print(f"Mortos por veículo: {vehicle_deaths}")

    insert_data = []
    for vehicle, deaths in vehicle_deaths.items():
        insert_data.append({
            "created_at": datetime.now(),
            "road_name": rows[0]["trecho"], 
            "vehicle": vehicle,
            "number_deaths": deaths
        })
    
    return insert_data

def save_to_db(insert_data, db_url):

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

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tabelas no banco de dados: {tables}")

    # Inserção dos dados
    for data in insert_data:
        session.execute(accident_deaths.insert().values(data))

    session.commit()
    session.close()

def process_and_save(file_info, db_url):
    bucket_name = file_info["csv_url"].split("/")[2]
    file_key = "/".join(file_info["csv_url"].split("/")[3:])
    
    rows = process_csv(bucket_name, file_key)
    insert_data = calculate_deaths(rows)
    save_to_db(insert_data, db_url)

def main(event, context):
    db_url = os.getenv('DB_URL')

    for file_info in event.get('files', []):
        process_and_save(file_info, db_url)