import os
import requests

# URL do arquivo .m3u8
m3u8_url = "https://bardou.naosouumaplicativo.com/storage1/series//100757/100757-4-7/100757-4x7.m3u8"

# Função para baixar o arquivo .m3u8
def download_m3u8(m3u8_url):
    try:
        response = requests.get(m3u8_url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Erro ao baixar o arquivo m3u8. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o arquivo m3u8: {e}")
        return None

# Função para baixar os segmentos .ts
def download_ts_segment(segment_url, segment_name):
    try:
        response = requests.get(segment_url)
        if response.status_code == 200:
            with open(segment_name, 'wb') as f:
                f.write(response.content)
            print(f"Arquivo {segment_name} baixado com sucesso!")
        else:
            print(f"Erro ao baixar {segment_name}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar {segment_name}: {e}")

# Função para processar o arquivo m3u8
def download_video_from_m3u8(m3u8_url):
    m3u8_content = download_m3u8(m3u8_url)
    
    if m3u8_content:
        base_url = os.path.dirname(m3u8_url)  # Base URL para os arquivos .ts
        # Dividir o conteúdo do m3u8 em linhas
        lines = m3u8_content.splitlines()

        # Filtrar as linhas que contêm URLs dos segmentos .ts
        ts_files = [line for line in lines if line.endswith('.ts')]

        for ts_file in ts_files:
            # Completar o caminho do segmento .ts
            ts_url = os.path.join(base_url, ts_file)
            download_ts_segment(ts_url, ts_file)

# Chamada principal
download_video_from_m3u8(m3u8_url)