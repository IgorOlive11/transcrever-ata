import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
AUDIO_PATH = "audio.mp3"  # ajuste se precisar

def upload_file(filename, api_key):
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
        "language_code": "pt",  # ou "pt-BR"
        "auto_chapters": False,
        "speaker_labels": True
    }
    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }
    response = requests.post(endpoint, json=json_data, headers=headers)
    print("Resposta ao solicitar transcrição:", response.text)  # debug
    response.raise_for_status()
    return response.json()["id"]

def poll_transcription(transcript_id, api_key):
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {
        "authorization": api_key
    }

    while True:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()

        print("Status:", data["status"])

        if data["status"] == "completed":
            return data["text"]
        elif data["status"] == "error":
            raise Exception(f"Transcrição falhou: {data['error']}")

        time.sleep(5)

def main():
    if not API_KEY:
        print("Erro: variável ASSEMBLYAI_API_KEY não encontrada no .env")
        return

    print("Iniciando upload do áudio...")
    upload_url = upload_file(AUDIO_PATH, API_KEY)
    print("Upload URL recebido:", upload_url)

    print("Solicitando transcrição...")
    transcript_id = request_transcription(upload_url, API_KEY)
    print("ID da transcrição:", transcript_id)

    print("Aguardando finalização da transcrição...")
    final_text = poll_transcription(transcript_id, API_KEY)

    with open("transcricao.txt", "w", encoding="utf-8") as f:
        f.write(final_text)
    print("Transcrição salva em transcricao.txt")

    print("\n=== TRANSCRIÇÃO FINALIZADA ===\n")
    print(final_text)

if __name__ == "__main__":
    main()
