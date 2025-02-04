import boto3
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from io import StringIO
import os

def process_csv(bucket_name, file_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = response['Body'].read().decode('utf-8')

    csv_data = StringIO(file_content)
    df = pd.read_csv(csv_data, delimiter=";") 

    return df

def calculate_deaths(df):
    """
    Calcula o número total de mortes e por tipo de veículo.
    """
    vehicle_columns = ["automovel", "bicicleta", "caminhao", "moto", "onibus"]
    
    vehicle_deaths = df[vehicle_columns].sum()

    total_deaths = df["mortos"].sum()

    print(f"Total de mortes: {total_deaths}")
    print(f"Mortos por veículo: {vehicle_deaths}")

    insert_data = []
    for vehicle, deaths in vehicle_deaths.items():
        insert_data.append({
            "created_at": datetime.now(),
            "road_name": df["trecho"].iloc[0], 
            "vehicle": vehicle,
            "number_deaths": deaths
        })
    
    return insert_data

def save_to_db(insert_data, db_url):

    engine = create_engine(db_url) 

    insert_df = pd.DataFrame(insert_data)
    insert_df.to_sql('accident_deaths', con=engine, if_exists='append', index=False)

def process_and_save(bucket_name, file_key, db_url):

    df = process_csv(bucket_name, file_key)
    
    insert_data = calculate_deaths(df)
    
    save_to_db(insert_data, db_url)

bucket_name = os.getenv('BUCKET_NAME')
file_key = os.getenv('FILE_KEY')
db_url = os.getenv('DB_URL')

process_and_save(bucket_name, file_key, db_url)