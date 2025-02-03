import boto3
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from io import StringIO

# Função para processar o CSV
def process_csv(bucket_name, file_key):
    """
    Baixa o arquivo CSV do S3 e o carrega em um DataFrame pandas.
    """
    # Baixar o arquivo CSV do S3
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = response['Body'].read().decode('utf-8')

    # Usar pandas para ler o CSV diretamente do conteúdo
    csv_data = StringIO(file_content)
    df = pd.read_csv(csv_data, delimiter=";")  # O separador é ";"

    return df

# Função para calcular o número de mortes por veículo
def calculate_deaths(df):
    """
    Calcula o número total de mortes e por tipo de veículo.
    """
    vehicle_columns = ["automovel", "bicicleta", "caminhao", "moto", "onibus"]
    
    # Somar os mortos por veículo
    vehicle_deaths = df[vehicle_columns].sum()

    # Somar o total de mortos
    total_deaths = df["mortos"].sum()

    print(f"Total de mortes: {total_deaths}")
    print(f"Mortos por veículo: {vehicle_deaths}")

    # Criar uma lista de dicionários com os dados para salvar no banco
    insert_data = []
    for vehicle, deaths in vehicle_deaths.items():
        insert_data.append({
            "created_at": datetime.now(),
            "road_name": df["trecho"].iloc[0],  # Usando o nome do primeiro trecho como exemplo
            "vehicle": vehicle,
            "number_deaths": deaths
        })
    
    return insert_data

# Função para salvar os dados no banco de dados
def save_to_db(insert_data, db_url):
    """
    Salva os dados calculados no banco de dados.
    """
    # Criar conexão com o banco de dados usando SQLAlchemy
    engine = create_engine(db_url)  # db_url deve ter o formato: 'postgresql://usuario:senha@host:porta/banco'

    # Convertendo a lista de dicionários para um DataFrame do pandas
    insert_df = pd.DataFrame(insert_data)

    # Inserir os dados no banco (supondo que já exista uma tabela chamada "accident_deaths")
    insert_df.to_sql('accident_deaths', con=engine, if_exists='append', index=False)

# Função principal para orquestrar o processo
def process_and_save(bucket_name, file_key, db_url):
    """
    Função principal que orquestra as operações de processamento e salvamento dos dados.
    """
    # Processar o CSV
    df = process_csv(bucket_name, file_key)
    
    # Calcular as mortes
    insert_data = calculate_deaths(df)
    
    # Salvar no banco de dados
    save_to_db(insert_data, db_url)

# Exemplo de uso
bucket_name = 'step-functions-challenge-dev-bucket'  # Substitua pelo seu bucket
file_key = 'csv_files/Via Araucaria_20250203102246.csv'  # Caminho do arquivo no S3
db_url = 'postgresql://username:password@localhost:5432/mydatabase'  # Substitua pela URL do seu banco de dados

# Executar o processo
process_and_save(bucket_name, file_key, db_url)