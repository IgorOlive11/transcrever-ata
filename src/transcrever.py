import requests
import time
import os
from dotenv import load_dotenv
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import QApplication

load_dotenv()
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

class TranscriptionWorker(QThread):
    """Worker corrigido que não trava durante o typing effect"""
    progress = Signal(str)
    text_update = Signal(str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path
        self.api_token = API_KEY
        self.current_text = ""
        self.full_text = ""
        self.typing_timer = None

    def run(self):
        try:
            # Mostra status inicial
            self.progress.emit("🔄 Iniciando transcrição...")
            
            # Usa a API REST
            texto = self.transcrever_com_updates()
            
            # Inicia o efeito de typing de forma segura
            self.full_text = texto
            self.start_typing_effect_safe()
            
        except Exception as e:
            self.error.emit(str(e))

    def transcrever_com_updates(self):
        """Transcreve usando API REST"""
        # Upload do arquivo
        self.progress.emit("📤 Fazendo upload do arquivo...")
        upload_url = upload_file(self.audio_path, self.api_token)
        
        # Solicita transcrição
        self.progress.emit("🚀 Upload concluído. Iniciando transcrição...")
        transcript_id = request_transcription(upload_url, self.api_token)
        
        # Polling
        self.progress.emit("⏳ Processando áudio...")
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

    def start_typing_effect_safe(self):
        """Efeito de typing usando QTimer (não bloqueia a thread)"""
        if not self.full_text:
            self.finished.emit()
            return
            
        # Limpa status e prepara para typing
        self.progress.emit("")
        self.current_text = ""
        
        # OPÇÃO SIMPLES: Mostra texto por palavras usando QTimer
        words = self.full_text.split()
        self.word_index = 0
        self.words_list = words
        
        # Cria timer para efeito de typing
        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self.add_next_word)
        self.typing_timer.start(50)  # 50ms entre palavras
    
    def add_next_word(self):
        """Adiciona próxima palavra (chamado pelo QTimer)"""
        if self.word_index < len(self.words_list):
            self.current_text += self.words_list[self.word_index] + " "
            self.text_update.emit(self.current_text.strip())
            self.word_index += 1
        else:
            # Terminou o typing
            if self.typing_timer:
                self.typing_timer.stop()
                self.typing_timer = None
            self.finished.emit()


# Função original para compatibilidade
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


# Classe legada mantida para compatibilidade (mas corrigida)
class AssemblyAIStreamWorker(QThread):
    """Versão corrigida da classe original"""
    partial_transcript = Signal(str)
    finished = Signal()
    error = Signal(str)
    typing_effect = Signal(str)

    def __init__(self, api_token, audio_path):
        super().__init__()
        self.api_token = api_token
        self.audio_path = audio_path

    def run(self):
        try:
            self.partial_transcript.emit("🔄 Iniciando transcrição...")
            texto = self.transcrever_com_updates()
            
            # Emite texto completo diretamente (sem efeito problemático)
            self.typing_effect.emit(texto)
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))

    def transcrever_com_updates(self):
        """Transcreve usando API REST"""
        self.partial_transcript.emit("📤 Fazendo upload do arquivo...")
        upload_url = upload_file(self.audio_path, self.api_token)
        
        self.partial_transcript.emit("🚀 Upload concluído. Iniciando transcrição...")
        transcript_id = request_transcription(upload_url, self.api_token)
        
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
            
            if time.time() - start_time > 600:
                raise TimeoutError("Timeout: transcrição demorou mais de 10 minutos")

            time.sleep(3)