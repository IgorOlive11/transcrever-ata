import requests
import time
import os
from dotenv import load_dotenv
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import QApplication

load_dotenv()
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

class AssemblyAIStreamWorker(QThread):
    """Worker que simula streaming com efeito de typing em tempo real"""
    partial_transcript = Signal(str)
    finished = Signal()
    error = Signal(str)
    typing_effect = Signal(str)  # Sinal para efeito de typing

    def __init__(self, api_token, audio_path):
        super().__init__()
        self.api_token = api_token
        self.audio_path = audio_path

    def run(self):
        try:
            # Mostra status inicial
            self.partial_transcript.emit("🔄 Iniciando transcrição...")
            
            # Usa a API REST
            texto = self.transcrever_com_updates()
            
            # Inicia o efeito de typing usando sleep ao invés de QTimer
            self.start_typing_effect(texto)
            
        except Exception as e:
            self.error.emit(str(e))

    def transcrever_com_updates(self):
        """Transcreve usando API REST"""
        # Upload do arquivo
        self.partial_transcript.emit("📤 Fazendo upload do arquivo...")
        upload_url = upload_file(self.audio_path, self.api_token)
        
        # Solicita transcrição
        self.partial_transcript.emit("🚀 Upload concluído. Iniciando transcrição...")
        transcript_id = request_transcription(upload_url, self.api_token)
        
        # Polling
        self.partial_transcript.emit("⏳ Processando áudio...")
        return self.poll_transcription(transcript_id)

    def poll_transcription(self, transcript_id):
        """Polling da transcrição"""
        endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        headers = {"authorization": self.api_token}
        
        start_time = time.time()
        
        while True:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            data = response.json()

            status = data["status"]
            
            if status == "completed":
                return data["text"]
            elif status == "error":
                raise Exception(f"Erro na transcrição: {data.get('error', 'Erro desconhecido')}")
            
            # Timeout de 10 minutos
            if time.time() - start_time > 600:
                raise TimeoutError("Timeout: transcrição demorou mais de 10 minutos")

            time.sleep(3)

    def start_typing_effect(self, text):
        """Simula typing usando sleep ao invés de QTimer"""
        # Limpa mensagens de status
        self.partial_transcript.emit("clear_status")
        
        # Efeito de typing MUITO mais rápido - várias opções:
        
        # OPÇÃO 1: Super rápido (5ms por caractere)
        for char in text:
            self.typing_effect.emit(char)
            time.sleep(0.005)  # 5ms entre cada caractere
            
        # OPÇÃO 2: Descomente para usar chunks de palavras (mais rápido ainda)
        # words = text.split()
        # current_text = ""
        # for word in words:
        #     current_text += word + " "
        #     self.typing_effect.emit(current_text)
        #     time.sleep(0.05)  # 50ms por palavra
            
        # OPÇÃO 3: Descomente para exibir instantaneamente
        # self.typing_effect.emit(text)
            
        self.finished.emit()


# Classe alternativa com chunks de palavras (mais realista)
class AssemblyAIRealisticStreamWorker(QThread):
    """Worker que simula streaming palavra por palavra (mais realista)"""
    partial_transcript = Signal(str)
    finished = Signal()
    error = Signal(str)
    word_chunk = Signal(str)

    def __init__(self, api_token, audio_path):
        super().__init__()
        self.api_token = api_token
        self.audio_path = audio_path

    def run(self):
        try:
            # Status inicial
            self.partial_transcript.emit("🔄 Iniciando transcrição...\n\n")
            
            # Transcrição
            texto = self.transcrever_com_updates()
            
            # Simula streaming palavra por palavra
            self.simulate_word_streaming(texto)
            
        except Exception as e:
            self.error.emit(str(e))

    def transcrever_com_updates(self):
        """Mesma lógica de transcrição"""
        upload_url = upload_file(self.audio_path, self.api_token)
        transcript_id = request_transcription(upload_url, self.api_token)
        return self.poll_transcription(transcript_id)

    def poll_transcription(self, transcript_id):
        """Polling da transcrição"""
        endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        headers = {"authorization": self.api_token}
        
        start_time = time.time()
        
        while True:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            data = response.json()

            status = data["status"]
            
            if status == "completed":
                return data["text"]
            elif status == "error":
                raise Exception(f"Erro na transcrição: {data.get('error')}")
            
            if time.time() - start_time > 600:
                raise TimeoutError("Timeout na transcrição")

            time.sleep(3)

    def simulate_word_streaming(self, text):
        """Simula streaming enviando palavras gradualmente"""
        # Limpa status
        self.partial_transcript.emit("")
        
        words = text.split()
        current_text = ""
        
        for i, word in enumerate(words):
            current_text += word + " "
            
            # Emite o texto completo até agora
            self.word_chunk.emit(current_text)
            
            # Pausa variável baseada no comprimento da palavra
            pause = min(0.1 + len(word) * 0.02, 0.3)  # Entre 100ms e 300ms
            time.sleep(pause)
            
            # Pausa extra após pontuação
            if word.endswith(('.', '!', '?', ':')):
                time.sleep(0.5)
        
        self.finished.emit()


# Função original que o main.py ainda precisa
def transcrever_audio(caminho_arquivo, status_callback=None):
    """Função principal de transcrição (fallback)"""
    if not API_KEY:
        raise Exception("ASSEMBLYAI_API_KEY não encontrada no .env")

    def report(msg):
        if status_callback:
            status_callback(msg)
        print(msg)

    try:
        report("📤 Fazendo upload do áudio...")
        upload_url = upload_file(caminho_arquivo, API_KEY)
        
        report("🚀 Solicitando transcrição...")
        transcript_id = request_transcription(upload_url, API_KEY)
        
        report("⏳ Aguardando processamento...")
        texto = poll_transcription(transcript_id, API_KEY, status_callback=report)
        
        report("✅ Transcrição concluída!")
        return texto
        
    except Exception as e:
        report(f"❌ Erro: {e}")
        raise

def poll_transcription(transcript_id, api_key, timeout=600, status_callback=None):
    """Polling padrão da transcrição"""
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {"authorization": api_key}
    
    start = time.time()
    while True:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()

        status = data["status"]
        
        if status_callback:
            status_callback(f"Status: {status}")

        if status == "completed":
            return data["text"]
        elif status == "error":
            raise Exception(f"Transcrição falhou: {data.get('error')}")

        if time.time() - start > timeout:
            raise TimeoutError("Timeout na transcrição")

        time.sleep(5)

def upload_file(filename, api_key):
    """Upload do arquivo para AssemblyAI"""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Arquivo não encontrado: {filename}")

    headers = {"authorization": api_key}

    with open(filename, "rb") as f:
        response = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers=headers,
            data=f
        )

    if not response.ok:
        raise Exception(f"Erro no upload: {response.status_code} - {response.text}")
    
    return response.json()["upload_url"]

def request_transcription(audio_url, api_key):
    """Solicita transcrição na API REST"""
    endpoint = "https://api.assemblyai.com/v2/transcript"
    
    json_data = {
        "audio_url": audio_url,
        "language_code": "pt",
        "punctuate": True,
        "format_text": True,
        "speaker_labels": True,
    }
    
    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }

    response = requests.post(endpoint, json=json_data, headers=headers)
    
    if not response.ok:
        raise Exception(f"Erro na requisição: {response.status_code} - {response.text}")
    
    return response.json()["id"]