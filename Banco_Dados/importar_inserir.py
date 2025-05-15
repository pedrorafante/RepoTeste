import pandas as pd
import json
import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import ast
import numpy as np

# Caminhos das pastas
input_folder = 'Banco_Dados/entrada'
processed_folder = 'Banco_Dados/processados'
output_folder = 'Banco_Dados/saida'
os.makedirs(processed_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Configurações do MySQL
host = 'localhost'
database = 'locomotive_MBC'
user = 'root'
password = 'root'

# Funções auxiliares
def parse_json_column(column_value):
    try:
        return json.loads(column_value.replace('""', '"'))
    except (json.JSONDecodeError, TypeError):
        return None

def parse_list(value, expected_length):
    if isinstance(value, list):
        # Já é lista, apenas ajustar o tamanho
        while len(value) < expected_length:
            value.append(None)
        return value
    if pd.isna(value) or str(value).lower() == 'nan':
        return [None] * expected_length
    try:
        lista = ast.literal_eval(value)
        if not isinstance(lista, list):
            return [None] * expected_length
        while len(lista) < expected_length:
            lista.append(None)
        return lista
    except (ValueError, SyntaxError):
        return [None] * expected_length
    
    
def convert_to_datetime(timestamp):
    if pd.isna(timestamp) or timestamp is None:
        return None
    if isinstance(timestamp, float):
        return None
    try:
        if isinstance(timestamp, str):
            formats = ['%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S']
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp, fmt)
                except ValueError:
                    continue
    except Exception:
        pass
    return None

def get_id_locomotiva(cursor, locomotive):
    cursor.execute("SELECT id FROM LOCOMOTIVAS WHERE locomotiva = %s", (str(locomotive),))
    result = cursor.fetchone()
    return result[0] if result else None

def log_error(message):
    with open("inserir_erros.log", "a") as log_file:
        log_file.write(message + "\n")

# Conectando ao banco de dados
try:
    connection = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )

    if connection.is_connected():
        cursor = connection.cursor()

        for file_name in os.listdir(input_folder):
            if not file_name.endswith('.csv'):
                continue

            print(f"🔄 Processando: {file_name}")
            file_path = os.path.join(input_folder, file_name)
            df = pd.read_csv(file_path)

            df['data'] = df['data'].apply(parse_json_column)
            df['gps'] = df['gps'].apply(parse_json_column)

            if df['data'].notna().any():
                egu_df = pd.json_normalize(df['data'].apply(lambda x: x.get('egu', {}) if isinstance(x, dict) else {}))
                cab_df = pd.json_normalize(df['data'].apply(lambda x: x.get('cab', {}) if isinstance(x, dict) else {}))
                exc_df = pd.json_normalize(df['data'].apply(lambda x: x.get('exc', {}) if isinstance(x, dict) else {}))
                egu_df.columns = [f"egu_{col}" for col in egu_df.columns]
                cab_df.columns = [f"cab_{col}" for col in cab_df.columns]
                exc_df.columns = [f"exc_{col}" for col in exc_df.columns]
                df = pd.concat([df, egu_df, cab_df, exc_df], axis=1)

            if df['gps'].iloc[0] is not None:
                gps_df = pd.json_normalize(df['gps'])
                gps_df.columns = [f"gps_{col}" for col in gps_df.columns]
                df = pd.concat([df, gps_df], axis=1)

            df.drop(columns=['data', 'gps'], inplace=True)

            # Tratamento de listas
            df['egu_data'] = df['egu_data'].apply(lambda x: parse_list(x, 8))
            df['cab_data'] = df['cab_data'].apply(lambda x: parse_list(x, 10))
            df['exc_data'] = df['exc_data'].apply(lambda x: parse_list(x, 20))

            # Inserção no banco
            for _, row in df.iterrows():
                locomotive = row['locomotive']
                timestamp = convert_to_datetime(row['timestamp'])
                gps_timestamp = convert_to_datetime(row.get('gps_gps_timestamp'))

                id_locomotiva = get_id_locomotiva(cursor, locomotive)
                if not id_locomotiva:
                    log_error(f"Locomotiva {locomotive} não encontrada.")
                    continue

                # Inserir EGU
                sql_egu = """
                INSERT INTO EGU (
                    id_locomotiva, time_stamp, 
                    value_EGU_1, value_EGU_2, value_EGU_3, value_EGU_4,
                    value_EGU_5, value_EGU_6, value_EGU_7, value_EGU_8
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                try:
                    cursor.execute(sql_egu, (id_locomotiva, timestamp) + tuple(row['egu_data']))
                except Error as e:
                    log_error(f"Erro EGU ({locomotive}): {e}")

                # Inserir EXC
                sql_exc = """
                INSERT INTO EXC (
                    id_locomotiva, time_stamp, 
                    value_EXC_1, value_EXC_2, value_EXC_3, value_EXC_4, value_EXC_5,
                    value_EXC_6, value_EXC_7, value_EXC_8, value_EXC_9, value_EXC_10,
                    value_EXC_11, value_EXC_12, value_EXC_13, value_EXC_14,
                    value_EXC_15, value_EXC_16, value_EXC_17, value_EXC_18,
                    value_EXC_19, value_EXC_20
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                try:
                    cursor.execute(sql_exc, (id_locomotiva, timestamp) + tuple(row['exc_data']))
                except Error as e:
                    log_error(f"Erro EXC ({locomotive}): {e}")

                # Inserir CAB
                sql_cab = """
                INSERT INTO CAB (
                    id_locomotiva, time_stamp, 
                    value_CAB_1, value_CAB_2, value_CAB_3, value_CAB_4,
                    value_CAB_5, value_CAB_6, value_CAB_7, value_CAB_8,
                    value_CAB_9, value_CAB_10
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                try:
                    cursor.execute(sql_cab, (id_locomotiva, timestamp) + tuple(row['cab_data']))
                except Error as e:
                    log_error(f"Erro CAB ({locomotive}): {e}")

                # Inserir GPS
                if gps_timestamp:
                    sql_gps = """
                    INSERT INTO GPS (
                        id_locomotiva, time_stamp, gps_timestamp, gps_status, 
                        gps_lat, gps_lon, gps_mag_variation, gps_mag_var_dir, 
                        gps_speed_on_ground, gps_true_course
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    try:
                        cursor.execute(sql_gps, (
                            id_locomotiva, timestamp, gps_timestamp,
                            row.get('gps_gps_status'),
                            row.get('gps_gps_lat'),
                            row.get('gps_gps_lon'),
                            row.get('gps_gps_mag_variation'),
                            row.get('gps_gps_mag_var_dir'),
                            row.get('gps_gps_speed_on_ground'),
                            row.get('gps_gps_true_course')
                        ))
                    except Error as e:
                        log_error(f"Erro GPS ({locomotive}): {e}")

            connection.commit()
            print(f"✅ Dados de {file_name} inseridos com sucesso!")

            # Salvar CSV tratado
            output_file = os.path.join(output_folder, f'processado_{file_name}')
            df.to_csv(output_file, index=False, sep=';')

            # Renomear o arquivo original
            new_name = os.path.join(processed_folder, f'importado_{file_name}')
            os.rename(file_path, new_name)
            print(f"📁 Arquivo movido para: {new_name}\n")

except Error as e:
    print(f"❌ Erro de conexão com MySQL: {e}")
    log_error(f"Erro de conexão: {e}")

finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("🔌 Conexão MySQL encerrada.")
