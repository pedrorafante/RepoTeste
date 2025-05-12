import pandas as pd
import mysql.connector
from mysql.connector import Error
import numpy as np

# Configurações de conexão com o MySQL
host = 'localhost'
database = 'locomotive_MBC'
user = 'mqtt_user'
password = 'mqttpass'

# Ler o arquivo Excel
file_path = 'Roteadores_Locomotivas_VLI.xlsx'
colunas_desejadas = [
    'Locomotiva',
    'SERIAL',
    'IMEI',
    'LAN MAC',
    'WIFI SSID',
    'WIFI PASSWORD',
    'Username',
    'PASSWORD',
    'OPERADORA',
    'CHIP',
    'DATA ATIVAÇÃO',
    'DATA INSTALAÇÃO'
]
df = pd.read_excel(file_path, sheet_name='Roteadores VLI Locomotivas')
df = df[colunas_desejadas]

# Tratamento de valores nulos para None
df = df.replace({np.nan: None})

# Conversão das datas para string no formato aceito pelo MySQL
df['DATA ATIVAÇÃO'] = pd.to_datetime(df['DATA ATIVAÇÃO'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
df['DATA INSTALAÇÃO'] = pd.to_datetime(df['DATA INSTALAÇÃO'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

# Substituir NaT por None para evitar erro de inserção
df['DATA ATIVAÇÃO'] = df['DATA ATIVAÇÃO'].replace({pd.NaT: None})
df['DATA INSTALAÇÃO'] = df['DATA INSTALAÇÃO'].replace({pd.NaT: None})

# Função para inserir ou atualizar dados no MySQL
def inserir_ou_atualizar_dados():
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Query SQL para inserção ou atualização
            sql_query = """
            INSERT INTO LOCOMOTIVAS (
                locomotiva, serial, imei, lan_mac, wifi_ssid, 
                wifi_password, username, password, operadora, 
                chip, data_ativacao, data_instalacao
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                serial = VALUES(serial),
                imei = VALUES(imei),
                lan_mac = VALUES(lan_mac),
                wifi_ssid = VALUES(wifi_ssid),
                wifi_password = VALUES(wifi_password),
                username = VALUES(username),
                password = VALUES(password),
                operadora = VALUES(operadora),
                chip = VALUES(chip),
                data_ativacao = VALUES(data_ativacao),
                data_instalacao = VALUES(data_instalacao)
            """

            # Loop para inserir os dados
            for _, row in df.iterrows():
                data = (
                    row['Locomotiva'],
                    row['SERIAL'],
                    row['IMEI'],
                    row['LAN MAC'],
                    row['WIFI SSID'],
                    row['WIFI PASSWORD'],
                    row['Username'],
                    row['PASSWORD'],
                    row['OPERADORA'],
                    row['CHIP'],
                    row['DATA ATIVAÇÃO'],
                    row['DATA INSTALAÇÃO']
                )
                
                try:
                    cursor.execute(sql_query, data)
                    print(f"Linha inserida/atualizada para Locomotiva: {row['Locomotiva']}")
                except Error as e:
                    print(f"Erro ao inserir Locomotiva {row['Locomotiva']}: {e}")

            # Confirmação no banco
            connection.commit()
            print("Todos os dados foram inseridos/atualizados com sucesso!")

    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexão MySQL encerrada.")

# Executar a função
inserir_ou_atualizar_dados()
