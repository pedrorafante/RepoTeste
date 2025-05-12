import pandas as pd
import json

# Caminho do arquivo CSV
file_path = '1740529762.csv'

# Leitura do arquivo CSV
df = pd.read_csv(file_path)

# Função para tratar campos JSON
def parse_json_column(column_value):
    try:
        # Corrigindo a formatação
        parsed = json.loads(column_value.replace('""', '"'))
        return parsed
    except (json.JSONDecodeError, TypeError):
        return None

# Aplicando a função para normalizar os campos JSON
df['data'] = df['data'].apply(parse_json_column)
df['gps'] = df['gps'].apply(parse_json_column)

# Separando os dados do JSON em colunas próprias
if df['data'].iloc[0] is not None:
    egu_df = pd.json_normalize(df['data'].apply(lambda x: x.get('egu', {})))
    cab_df = pd.json_normalize(df['data'].apply(lambda x: x.get('cab', {})))
    exc_df = pd.json_normalize(df['data'].apply(lambda x: x.get('exc', {})))
    
    # Adicionando prefixos para identificação
    egu_df.columns = [f"egu_{col}" for col in egu_df.columns]
    cab_df.columns = [f"cab_{col}" for col in cab_df.columns]
    exc_df.columns = [f"exc_{col}" for col in exc_df.columns]
    
    # Concatenando os DataFrames no principal
    df = pd.concat([df, egu_df, cab_df, exc_df], axis=1)

# Separando os dados de GPS
if df['gps'].iloc[0] is not None:
    gps_df = pd.json_normalize(df['gps'])
    gps_df.columns = [f"gps_{col}" for col in gps_df.columns]
    df = pd.concat([df, gps_df], axis=1)

# Removendo colunas antigas (data e gps em formato JSON)
df.drop(columns=['data', 'gps'], inplace=True)

# Salvando em um novo arquivo CSV formatado
output_file = 'dados_processados.csv'
df.to_csv(output_file, index=False, sep=';')

print(f"Dados processados e salvos em: {output_file}")
