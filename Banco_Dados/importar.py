import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import ast
import numpy as np

# Configurações de conexão com o MySQL
host = 'localhost'
database = 'locomotive_MBC'
user = 'root'
password = 'root'

# Caminho do arquivo CSV processado
file_path = 'dados_processados.csv'

# Leitura do CSV processado
print("🔄 Lendo o arquivo CSV...")
df = pd.read_csv(file_path, sep=';')

# ✅ Tratamento para listas (transformar string em lista)
def parse_list(value, expected_length):
    if pd.isna(value) or value == 'nan':
        return [None] * expected_length
    try:
        lista = ast.literal_eval(value)
        while len(lista) < expected_length:
            lista.append(None)
        return lista
    except (ValueError, SyntaxError):
        print(f"⚠️ Erro ao converter valor: {value}")
        return [None] * expected_length

# Aplicando o parse para as colunas do CSV
df['egu_data'] = df['egu_data'].apply(lambda x: parse_list(x, 8))
df['cab_data'] = df['cab_data'].apply(lambda x: parse_list(x, 10))
df['exc_data'] = df['exc_data'].apply(lambda x: parse_list(x, 20))

# Função para converter timestamp para formato correto
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
    except Exception as e:
        print(f"Erro ao converter timestamp: {timestamp} - {e}")
    return None

# Função para buscar o ID da locomotiva
def get_id_locomotiva(cursor, locomotive):
    cursor.execute("SELECT id FROM LOCOMOTIVAS WHERE locomotiva = %s", (str(locomotive),))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        print(f"⚠️ Locomotiva {locomotive} não encontrada no banco de dados.")
        return None

# Função para logar erros em arquivo
def log_error(message):
    with open("inserir_erros.log", "a") as log_file:
        log_file.write(message + "\n")

# Conexão com o banco de dados
try:
    connection = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )

    if connection.is_connected():
        cursor = connection.cursor()

        # Loop pelos dados do DataFrame
        for _, row in df.iterrows():
            locomotive = row['locomotive']
            timestamp = convert_to_datetime(row['timestamp'])
            gps_timestamp = convert_to_datetime(row['gps_gps_timestamp'])

            # Buscar o ID da locomotiva no banco de dados
            id_locomotiva = get_id_locomotiva(cursor, locomotive)

            if id_locomotiva:
                # ✅ Inserção em EGU
                sql_egu = """
                INSERT INTO EGU (
                    id_locomotiva, time_stamp, 
                    value_EGU_1, value_EGU_2, value_EGU_3, value_EGU_4,
                    value_EGU_5, value_EGU_6, value_EGU_7, value_EGU_8
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                data_egu = (id_locomotiva, timestamp) + tuple(row['egu_data'])
                try:
                    cursor.execute(sql_egu, data_egu)
                except Error as e:
                    log_error(f"Erro ao inserir EGU para {locomotive}: {e}")

                # ✅ Inserção em EXC
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
                data_exc = (id_locomotiva, timestamp) + tuple(row['exc_data'])
                try:
                    cursor.execute(sql_exc, data_exc)
                except Error as e:
                    log_error(f"Erro ao inserir EXC para {locomotive}: {e}")

                # ✅ Inserção em CAB
                sql_cab = """
                INSERT INTO CAB (
                    id_locomotiva, time_stamp, 
                    value_CAB_1, value_CAB_2, value_CAB_3, value_CAB_4,
                    value_CAB_5, value_CAB_6, value_CAB_7, value_CAB_8,
                    value_CAB_9, value_CAB_10
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                data_cab = (id_locomotiva, timestamp) + tuple(row['cab_data'])
                try:
                    cursor.execute(sql_cab, data_cab)
                except Error as e:
                    log_error(f"Erro ao inserir CAB para {locomotive}: {e}")

                # ✅ Inserção em GPS
                if gps_timestamp:
                    sql_gps = """
                    INSERT INTO GPS (
                        id_locomotiva, time_stamp, gps_timestamp, gps_status, 
                        gps_lat, gps_lon, gps_mag_variation, gps_mag_var_dir, 
                        gps_speed_on_ground, gps_true_course
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    data_gps = (
                        id_locomotiva, timestamp, gps_timestamp,
                        row.get('gps_gps_status', None),
                        row.get('gps_gps_lat', None),
                        row.get('gps_gps_lon', None),
                        row.get('gps_gps_mag_variation', None),
                        row.get('gps_gps_mag_var_dir', None),
                        row.get('gps_gps_speed_on_ground', None),
                        row.get('gps_gps_true_course', None)
                    )
                    try:
                        cursor.execute(sql_gps, data_gps)
                    except Error as e:
                        log_error(f"Erro ao inserir GPS para {locomotive}: {e}")

        connection.commit()
        print("✅ Dados inseridos com sucesso!")

except Error as e:
    print(f"❌ Erro ao conectar ao MySQL: {e}")
    log_error(f"Erro de conexão: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("🔌 Conexão MySQL encerrada.")
