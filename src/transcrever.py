import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

def upload_file(filename, api_key):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Arquivo não encontrado: {filename}")

    headers = {
        "authorization": api_key,
    }

    with open(filename, "rb") as f:
        response = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers=headers,
            data=f
        )

    response.raise_for_status()
    return response.json()["upload_url"]

def request_transcription(audio_url, api_key):
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json_data = {
        "audio_url": audio_url,
        "language_code": "pt",
        "auto_chapters": False,
        "speaker_labels": True
    }
    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }

    response = requests.post(endpoint, json=json_data, headers=headers)
    response.raise_for_status()
    return response.json()["id"]

def transcrever_audio(caminho_arquivo, status_callback=None):
    if not API_KEY:
        raise Exception("Erro: variável ASSEMBLYAI_API_KEY não encontrada no .env")

    def report(msg):
        if status_callback:
            status_callback(msg)
        else:
            print(msg)

    report("Iniciando upload do áudio...")
    upload_url = upload_file(caminho_arquivo, API_KEY)
    report("Upload realizado com sucesso.")

    report("Solicitando transcrição...")
    transcript_id = request_transcription(upload_url, API_KEY)
    report(f"ID da transcrição: {transcript_id}")

    report("Aguardando finalização da transcrição...")
    
    final_text = poll_transcription(transcript_id, API_KEY, status_callback=report)

    return final_text

def poll_transcription(transcript_id, api_key, timeout=600, status_callback=None):
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {"authorization": api_key}
    start = time.time()
    while True:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()

        status = data["status"]
        msg = f"Status: {status}"
        if status_callback:
            status_callback(msg)
        else:
            print(msg)

        if status == "completed":
            return data["text"]
        elif status == "error":
            raise Exception(f"Transcrição falhou: {data['error']}")

        if time.time() - start > timeout:
            raise TimeoutError("Tempo limite excedido ao aguardar a transcrição.")

        time.sleep(5)
