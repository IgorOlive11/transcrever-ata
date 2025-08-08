import sys
import os
import ctypes

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

if getattr(sys, 'frozen', False):
    cache_path = resource_path("tiktoken_cache")
    os.environ["TIKTOKEN_CACHE_DIR"] = cache_path

# .env fora da pasta src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(project_root, ".env")

if os.path.exists(env_path):
    from dotenv import load_dotenv
    load_dotenv(env_path)
else:
    print(f"Aviso: arquivo .env não encontrado em {env_path}")

import traceback
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QProgressDialog
from PySide6.QtCore import QThread, QObject, Signal, QRunnable, QThreadPool
from PySide6.QtGui import QIcon, QTextCursor
from transcrever import transcrever_audio
from gerar_ata import gerar_ata_formal
from interface import Ui_MainWindow
from transcrever import AssemblyAIStreamWorker, API_KEY
from dialog_info_assembleia import DialogInfoAssembleia  # Nova importação

class AtaWorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    progress = Signal(str)


class AtaWorker(QRunnable):
    def __init__(self, texto_transcricao, caminho_saida, info_assembleia=None):
        super().__init__()
        self.texto_transcricao = texto_transcricao
        self.caminho_saida = caminho_saida
        self.info_assembleia = info_assembleia
        self.signals = AtaWorkerSignals()

    def run(self):
        try:
            self.signals.progress.emit("Dividindo texto em blocos...")
            gerar_ata_formal(
                self.texto_transcricao,
                caminho_saida=self.caminho_saida,
                status_callback=self.signals.progress.emit,
                info_assembleia=self.info_assembleia  # Passa as informações
            )
            self.signals.progress.emit("ATA gerada com sucesso.")
            self.signals.finished.emit()
        except Exception as e:
            tb = traceback.format_exc()
            self.signals.error.emit(f"{str(e)}\n{tb}")


class WorkerThread(QThread):
    finished = Signal(str)
    error = Signal(str)
    status = Signal(str)

    def __init__(self, caminho_arquivo):
        super().__init__()
        self.caminho_arquivo = caminho_arquivo

    def run(self):
        try:
            texto = transcrever_audio(self.caminho_arquivo, status_callback=self.emit_status)
            self.finished.emit(texto)
        except Exception as e:
            tb = traceback.format_exc()
            self.error.emit(f"{str(e)}\n{tb}")

    def emit_status(self, msg):
        self.status.emit(msg)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        icon_path = resource_path(os.path.join("ui", "windowicon.ico"))
        self.setWindowIcon(QIcon(icon_path))

        self.threadpool = QThreadPool()

        self.ui.btnEscolher.clicked.connect(self.selecionar_arquivo)
        self.ui.btnTranscrever.clicked.connect(self.transcrever)
        self.ui.btnGerar.clicked.connect(self.gerar_ata)

        self.worker = None
        self.progress_dialog = None

    def selecionar_arquivo(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Selecione o arquivo de áudio",
            "",
            "Arquivos de Áudio (*.mp3 *.wav *.m4a)"
        )
        if caminho:
            self.ui.lineEditArquivo.setText(caminho)

    def transcrever(self):
        caminho = self.ui.lineEditArquivo.text().strip()
        if not caminho:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo primeiro.")
            return
        if not os.path.exists(caminho):
            QMessageBox.critical(self, "Erro", "Arquivo não encontrado.")
            return

        self.ui.textEdit.clear()
        self.ui.statusbar.showMessage("Iniciando transcrição...")

        self.ui.btnTranscrever.setEnabled(False)

        # OPÇÃO 1: Efeito character-by-character (mais dramático)
        self.worker = AssemblyAIStreamWorker(API_KEY, caminho)
        self.worker.partial_transcript.connect(self.update_status_text)
        self.worker.typing_effect.connect(self.append_character)
        self.worker.error.connect(self.transcricao_erro)
        self.worker.finished.connect(self.transcricao_finalizada)

        # OPÇÃO 2: Efeito word-by-word (mais realista)
        # Descomente as linhas abaixo e comente as de cima para usar
        # from transcrever import AssemblyAIRealisticStreamWorker
        # self.worker = AssemblyAIRealisticStreamWorker(API_KEY, caminho)
        # self.worker.partial_transcript.connect(self.update_status_text)
        # self.worker.word_chunk.connect(self.replace_text)
        # self.worker.error.connect(self.transcricao_erro)
        # self.worker.finished.connect(self.transcricao_finalizada)

        self.worker.start()

    def update_status_text(self, texto):
        """Atualiza apenas mensagens de status, não o texto principal"""
        if texto == "clear_status":
            # Limpa o campo de texto para começar o typing
            self.ui.textEdit.clear()
            return
            
        if any(emoji in texto for emoji in ['🔄', '📤', '🚀', '⏳']):
            self.ui.statusbar.showMessage(texto.replace('\n', ' ').strip())

    def append_character(self, text):
        """Adiciona texto (pode ser um caractere ou palavra/frase)"""
        cursor = self.ui.textEdit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Se receber o texto completo (OPÇÃO 3), substitui tudo
        if len(text) > 100:  # Provavelmente texto completo
            self.ui.textEdit.setPlainText(text)
        else:
            # Adiciona caractere por caractere ou palavra por palavra
            cursor.insertText(text)
            
        self.ui.textEdit.setTextCursor(cursor)
        
        # Auto-scroll para o final
        scrollbar = self.ui.textEdit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        QApplication.processEvents()

    def replace_text(self, texto_completo):
        """Substitui todo o texto (para efeito word-by-word)"""
        self.ui.textEdit.setPlainText(texto_completo)
        
        # Auto-scroll para o final
        scrollbar = self.ui.textEdit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        QApplication.processEvents()

    def atualizar_status(self, mensagem):
        self.ui.statusbar.showMessage(mensagem)
        if self.progress_dialog:
            self.progress_dialog.setLabelText(mensagem)
        QApplication.processEvents()

    def transcricao_finalizada(self, _=None):
        self.ui.btnTranscrever.setEnabled(True)
        self.ui.statusbar.showMessage("Transcrição concluída!")
        self.worker = None

    def transcricao_erro(self, msg):
        self.ui.btnTranscrever.setEnabled(True)
        QMessageBox.critical(self, "Erro na transcrição", msg)
        self.worker = None
        self.ui.statusbar.showMessage("Erro na transcrição.")

    def gerar_ata(self):
        texto_transcricao = self.ui.textEdit.toPlainText()
        if not texto_transcricao.strip():
            QMessageBox.warning(self, "Aviso", "Nenhuma transcrição disponível para gerar ATA.")
            return

        # Abre diálogo para coletar informações da assembleia (passando a transcrição)
        info_assembleia = DialogInfoAssembleia.obterInformacoesAssembleia(self, texto_transcricao)
        if not info_assembleia:
            return  # Usuario cancelou

        # Validação básica (apartamento não é mais obrigatório)
        campos_obrigatorios = ['nome_condominio', 'presidente_nome', 'secretario_nome']
        for campo in campos_obrigatorios:
            if not info_assembleia[campo]:
                QMessageBox.warning(
                    self, 
                    "Campos Obrigatórios", 
                    f"Por favor, preencha o campo: {campo.replace('_', ' ').title()}"
                )
                return

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Ata como...",
            f"ata_{info_assembleia['nome_condominio'].lower().replace(' ', '_')}_{info_assembleia['data_assembleia'].replace('/', '_')}.docx",
            "Documentos Word (*.docx)"
        )
        if not caminho:
            return

        self.progress_dialog = QProgressDialog("Gerando ATA...", "Cancelar", 0, 0, self)
        self.progress_dialog.setWindowTitle("Aguarde")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setModal(True)
        self.progress_dialog.show()

        self.worker = AtaWorker(texto_transcricao, caminho, info_assembleia)
        self.worker.signals.progress.connect(self.atualizar_status)
        self.worker.signals.finished.connect(self.finalizar_progresso)
        self.worker.signals.error.connect(self.erro_progresso)

        self.threadpool.start(self.worker)

    def finalizar_progresso(self):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        QMessageBox.information(self, "Sucesso", "Ata gerada com sucesso.")

    def erro_progresso(self, msg):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        QMessageBox.critical(self, "Erro", f"Ocorreu um erro:\n{msg}")

    def closeEvent(self, event):
        """Limpa threads ao fechar"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait(1000)
        event.accept()


if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.meuapp.transcreverata")

    app = QApplication(sys.argv)

    icon_path = resource_path(os.path.join("ui", "windowicon.ico"))
    app.setWindowIcon(QIcon(icon_path))

    style_path = resource_path(os.path.join("ui", "style.qss"))
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            style = f.read()
            app.setStyleSheet(style)
    else:
        print(f"Aviso: arquivo de estilo não encontrado em {style_path}")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())