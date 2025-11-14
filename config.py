import os
from dotenv import load_dotenv
import boto3
import io

# Carica il file .env solo una volta all'avvio
load_dotenv()

def get_key(name: str) -> str:      #funzione usata in summarize.py
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Variabile d'ambiente '{name}' non trovata. Assicurati che sia definita nel file .env.")
    return value

def download_to_s3():             #funzione per dati_pandas.py e interface.py
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

    bucket_name = "amzn-s3-summerize"
    object_key = "dati_utente.csv"

    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    content = response['Body'].read().decode('utf-8')
    return content

def upload_to_s3(df):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

    buffer = io.StringIO()
    
    df.to_csv(buffer, index=False)

    bucket_name = "amzn-s3-summerize"
    object_key = "dati_utente.csv"
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=buffer.getvalue())








