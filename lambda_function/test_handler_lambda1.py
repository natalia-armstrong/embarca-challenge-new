import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from handler_lambda1 import validate_s3_bucket, download_file, process_files, main

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../lambda_function')))


class TestHandlerLambda1(unittest.TestCase):

    @patch('handler_lambda1.os.environ.get')
    def test_validate_s3_bucket(self, mock_get):
        # Teste de sucesso
        mock_get.return_value = 'my-test-bucket'
        self.assertEqual(validate_s3_bucket(), 'my-test-bucket')

        # Teste de erro (missing)
        mock_get.return_value = None
        with self.assertRaises(ValueError):
            validate_s3_bucket()

    @patch('handler_lambda1.requests.get')
    def test_download_file(self, mock_get):
        # Mock de sucesso
        mock_response = MagicMock(status_code=200, content=b"col1,col2\nval1,val2", apparent_encoding='utf-8')
        mock_get.return_value = mock_response
        file_name, content = download_file("http://example.com/file.csv", "test_file")
        
        self.assertTrue(file_name.endswith('.csv'))
        self.assertEqual(content, b"col1,col2\nval1,val2")
        
        # Mock de falha
        mock_response.status_code = 404
        with self.assertRaises(Exception):
            download_file("http://example.com/file.csv", "test_file")

    @patch('handler_lambda1.boto3.client')
    @patch('handler_lambda1.download_file')
    def test_process_files(self, mock_download, mock_boto3_client):
        mock_download.return_value = ("csv_files/test_file.csv", b"col1,col2\nval1,val2")
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client

        link = {"test_file": "http://example.com/file.csv"}
        s3_bucket = "my-test-bucket"
        result = process_files(link, s3_bucket)

        mock_s3_client.put_object.assert_called_with(Bucket=s3_bucket, Key='csv_files/test_file.csv', Body=b"col1,col2\nval1,val2")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['file_name'], 'csv_files/test_file.csv')

    @patch('handler_lambda1.process_files')
    @patch('handler_lambda1.validate_s3_bucket')
    def test_main(self, mock_validate_s3_bucket, mock_process_files):
        # Teste de sucesso
        mock_validate_s3_bucket.return_value = 'my-test-bucket'
        mock_process_files.return_value = [{'csv_url': 's3://my-test-bucket/csv_files/test_file.csv', 'file_name': 'csv_files/test_file.csv', 'original_link': 'http://example.com/file.csv'}]
        
        event = {'link': {"test_file": "http://example.com/file.csv"}}
        context = {}
        result = main(event, context)

        self.assertIn('files', result)
        self.assertEqual(len(result['files']), 1)
        self.assertEqual(result['files'][0]['file_name'], 'csv_files/test_file.csv')

        # Teste de erro
        mock_validate_s3_bucket.side_effect = ValueError("S3_BUCKET missing")
        result = main(event, context)
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'S3_BUCKET missing')


if __name__ == '__main__':
    unittest.main()