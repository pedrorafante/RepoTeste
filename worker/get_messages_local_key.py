
import boto3
import json
import zlib, base64
import pandas as pd
from datetime import datetime
import time
import os
import mysql.connector

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
SQS_QUEUE = os.getenv("SQS_QUEUE", "vli-mezuri-out")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
REGION = os.getenv("AWS_REGION", "us-east-1")

def baixar_dados_sqs():
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=REGION
    )
    sqs = session.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE)

    max_queue_messages = 10
    wait_time_seconds = 5
    visibility_timeout = 120

    df = pd.DataFrame()
    counter = 0
    messages_to_delete = []

    while True:
        messages = queue.receive_messages(MaxNumberOfMessages=max_queue_messages,
                                          WaitTimeSeconds=wait_time_seconds,
                                          VisibilityTimeout=visibility_timeout)
        if not messages:
            break

        for message in messages:
            try:
                body = json.loads(message.body)
                payload = json.loads(zlib.decompress(base64.b64decode(body['Message'])))
                df = pd.concat([df, pd.DataFrame([payload])])
                messages_to_delete.append({'Id': message.message_id, 'ReceiptHandle': message.receipt_handle})
                counter += 1
            except Exception as e:
                print(f"[⚠️] Erro ao processar mensagem: {e}")

        if counter >= 100:
            break

    if messages_to_delete:
        queue.delete_messages(Entries=messages_to_delete)

    return df

def salvar_no_mysql(df):
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = conn.cursor()
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO locomotives (locomotive, model, built_in, mezuri_install_date, mezure_SN, mezure_version)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE model=VALUES(model)
            """, (
                row.get("locomotive", 0),
                row.get("model", ""),
                row.get("built_in", datetime.now().date()),
                row.get("mezuri_install_date", datetime.now().date()),
                row.get("mezure_SN", ""),
                row.get("mezure_version", "")
            ))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[✅] {len(df)} registros inseridos no banco.")
    except Exception as e:
        print(f"[❌] Erro ao salvar no banco: {e}")

if __name__ == "__main__":
    while True:
        print(f"[{datetime.now()}] 🔄 Iniciando ciclo de ingestão...")
        try:
            dados = baixar_dados_sqs()
            if not dados.empty:
                salvar_no_mysql(dados)
            else:
                print(f"[ℹ️] Nenhum dado novo encontrado.")
        except Exception as e:
            print(f"[❌] Erro geral: {e}")
        print("[⏱️] Aguardando 5 minutos...")
        time.sleep(300)
