init:
    pip install -r requirements.txt

test: 
    python -m unittest test_handler_lambda2.py
    python -m unittest outro_arquivo_de_teste.py