import unittest
from unittest.mock import patch, MagicMock
from handler_lambda2 import process_csv, calculate_deaths, save_to_db, process_and_save, main
import os

class TestHandlerLambda2(unittest.TestCase):

    @patch('handler_lambda2.boto3.client')
    @patch('handler_lambda2.chardet.detect')
    def test_process_csv(self, mock_detect, mock_boto3_client):
        # Simulando o retorno do S3
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.get_object.return_value = {
            'Body': MagicMock(read=MagicMock(return_value=b"trecho;automovel;bicicleta;moto;mortos\nRua A;2;1;3;6"))
        }
        
        # Simulando a detecção do encoding
        mock_detect.return_value = {'encoding': 'utf-8'}
        
        bucket_name = "my-bucket"
        file_key = "path/to/file.csv"
        
        result = process_csv(bucket_name, file_key)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['trecho'], 'Rua A')
        self.assertEqual(result[0]['mortos'], '6')  # A chave 'mortos' foi adicionada corretamente

    @patch('handler_lambda2.calculate_deaths')
    def test_calculate_deaths(self, mock_calculate_deaths):
        rows = [
            {"trecho": "Rua A", "automovel": "2", "bicicleta": "1", "moto": "3", "mortos": "6"}
        ]
        
        result = calculate_deaths(rows)
        
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["vehicle"], "automovel")
        self.assertEqual(result[0]["number_deaths"], 2)

    @patch('handler_lambda2.save_to_db')
    @patch('handler_lambda2.boto3.client')  # Mockando o boto3 para não fazer chamadas reais
    def test_process_and_save(self, mock_boto3_client, mock_save_to_db):
        # Mock do S3 para não fazer a requisição real
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.get_object.return_value = {
            'Body': MagicMock(read=MagicMock(return_value=b"trecho;automovel;bicicleta;moto;mortos\nRua A;2;1;3;6"))
        }
        
        file_info = {"csv_url": "s3://my-bucket/path/to/file.csv"}
        db_url = "sqlite:///:memory:"
        
        # Simulando sucesso no processo
        mock_save_to_db.return_value = None
        
        process_and_save(file_info, db_url)
        
        # Verificando se o método de salvar foi chamado
        mock_save_to_db.assert_called_once()

    @patch('handler_lambda2.process_and_save')
    @patch('handler_lambda2.os.getenv')
    def test_main_success(self, mock_getenv, mock_process_and_save):
        mock_getenv.return_value = "sqlite:///:memory:"
        
        # Simulando o comportamento do processo
        mock_process_and_save.return_value = None
        
        event = {'files': [{"csv_url": "s3://my-bucket/path/to/file.csv"}]}
        context = {}
        
        result = main(event, context)
        
        self.assertIsNone(result)

    @patch('handler_lambda2.process_and_save')
    @patch('handler_lambda2.os.getenv')
    def test_main_missing_db_url(self, mock_getenv, mock_process_and_save):
        mock_getenv.return_value = None  # Simulando a falta da variável DB_URL
        
        event = {'files': [{"csv_url": "s3://my-bucket/path/to/file.csv"}]}
        context = {}
        
        with self.assertRaises(ValueError):
            main(event, context)

if __name__ == '__main__':
    unittest.main()
