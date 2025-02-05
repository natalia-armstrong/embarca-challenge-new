# Informações de desenvolvimento

**Desenvolvedora:** Natalia Armstrong
**Repositório GitHub:** [link-do-repositorio](https://github.com/natalia-armstrong/embarca-challenge-new)

# Desafio AWS Step Functions com Serverless Framework e S3

Bem-vindo(a) ao desafio de orquestração de microserviços usando **AWS Step Functions**, **Lambdas** e **S3**. O objetivo é criar e gerenciar os recursos AWS utilizando o **Serverless Framework** e **Python** para automatizar o fluxo de dados e cálculo de métricas.

## Objetivo

O desafio envolve a criação de um fluxo orquestrado por uma **State Machine** no **AWS Step Functions**, no qual:

- **Lambda 1**: Baixa um arquivo CSV e salva em um **S3 Bucket**.
- **Lambda 2**: Recupera o CSV salvo e calcula uma métrica (número de mortes em acidentes) para diferentes tipos de veículos, salvando os dados em um banco de dados relacional.

## Requisitos

### Lambda 1

- Deve ser capaz de receber um link de arquivo como entrada.
- Baixar o CSV encontrado e salvá-lo em um **S3 Bucket**.
- Transformar ou tratar os dados conforme necessário.
- Retornar as informações pertinentes para a segunda Lambda.

### Lambda 2

- Recebe as informações da primeira Lambda.
- Calcula o número de mortos em acidentes envolvendo os seguintes veículos:
  - 'automovel'
  - 'bicicleta'
  - 'caminhao'
  - 'moto'
  - 'onibus'
- Salva os dados em uma tabela em um banco relacional.
- Retorna informações significativas para o usuário.

### Formato de Saída

A tabela gerada pela segunda Lambda deverá conter as seguintes colunas:

| Coluna        | Descrição                            |
|---------------|--------------------------------------|
| `created_at`  | Data de criação                      |
| `road_name`   | Nome da rua                          |
| `vehicle`     | Tipo de veículo                      |
| `number_deaths` | Número de mortes                     |

## Desenvolvimento

- **Lambda 1**: Responsável pelo download do arquivo CSV e armazenamento no S3.
- **Lambda 2**: Processa o CSV, calcula as métricas e salva no banco relacional.

## Estrutura de Arquivos

- **serverless.yml**: Arquivo de configuração do Serverless Framework para orquestrar as Lambdas e o AWS Step Functions.
- **handler_lambda1.py**: Código da Lambda 1.
- **handler_lambda2.py**: Código da Lambda 2.
- **requirements.txt**: Dependências necessárias para o funcionamento das Lambdas.
- **Dockerfile**: Para construção e execução local do ambiente.

## Principais Documentações e procedimentos:
- **Usar o Serverless Framework Local**: 


## Principais Comandos
- **serverless deploy**: Implantar de um serviço na nuvem
- **serverless invoke -f lambda1 -p event.json**: Invocar uma função Lambda específica, no caso a função lambda1, dentro de um ambiente Serverless Framework.
- **serverless invoke -f lambda2 -p lambda1_output_clean.json**: Invocar uma função Lambda específica, no caso a função lambda2, dentro de um ambiente Serverless Framework.
- **(dentro do diretório lambda_function) python -m unittest test_handler_lambda1.py**: Testar o arquivo python handler_lambda1.py.
- **(dentro do diretório lambda_function) python -m unittest test_handler_lambda2.py**: Testar o arquivo python handler_lambda2.py.

## Mais informações de configuração e acesso:
- **Link da documentação**: https://radial-quark-6a1.notion.site/Embarca-Docs-1914c6677e9780f89320dc9640960705
    P.S: Escolhi documentar através do notion pois acredito ser uma ótima plataforma de documentação e gostaria de compartilhar esse conhecimento.
