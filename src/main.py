import sys
import os

def resource_path(relative_path):
    """
    Retorna o caminho absoluto para recursos, funcionando
    tanto no modo desenvolvimento quanto no executável PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # Executável PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

if getattr(sys, 'frozen', False):
    cache_path = resource_path("tiktoken_cache")
    os.environ["TIKTOKEN_CACHE_DIR"] = cache_path

env_path = resource_path(".env")

if os.path.exists(env_path):
    from dotenv import load_dotenv
    load_dotenv(env_path)
else:
    print(f"Aviso: arquivo .env não encontrado em {env_path}")

import traceback
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QProgressDialog
)
from PySide6.QtCore import QThread, QObject, Signal, QRunnable, QThreadPool
from PySide6.QtGui import QIcon
from transcrever import transcrever_audio
from gerar_ata import gerar_ata_formal
from interface import Ui_MainWindow


class AtaWorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    progress = Signal(str)


class AtaWorker(QRunnable):
    def __init__(self, texto_transcricao, caminho_saida):
        super().__init__()
        self.texto_transcricao = texto_transcricao
        self.caminho_saida = caminho_saida
        self.signals = AtaWorkerSignals()

    def run(self):
        try:
            self.signals.progress.emit("Dividindo texto em blocos...")
            gerar_ata_formal(
                self.texto_transcricao,
                caminho_saida=self.caminho_saida,
                status_callback=self.signals.progress.emit
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

        self.thread = None
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
        self.ui.textEdit.setPlainText("Transcrevendo, aguarde...")
        self.ui.statusbar.showMessage("")

        self.ui.btnTranscrever.setEnabled(False)

        self.thread = WorkerThread(caminho)
        self.thread.finished.connect(self.transcricao_finalizada)
        self.thread.error.connect(self.transcricao_erro)
        self.thread.status.connect(self.atualizar_status)
        self.thread.start()

    def atualizar_status(self, mensagem):
        self.ui.statusbar.showMessage(mensagem)
        if self.progress_dialog:
            self.progress_dialog.setLabelText(mensagem)
        QApplication.processEvents()

    def transcricao_finalizada(self, texto):
        self.ui.btnTranscrever.setEnabled(True)
        self.ui.textEdit.setPlainText(texto)
        self.thread = None
        self.ui.statusbar.showMessage("Transcrição concluída.")

    def transcricao_erro(self, msg):
        self.ui.btnTranscrever.setEnabled(True)
        QMessageBox.critical(self, "Erro na transcrição", msg)
        self.thread = None
        self.ui.statusbar.showMessage("Erro na transcrição.")

    def gerar_ata(self):
        texto_transcricao = self.ui.textEdit.toPlainText()
        if not texto_transcricao.strip():
            QMessageBox.warning(self, "Aviso", "Nenhuma transcrição disponível para gerar ATA.")
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Ata como...",
            "ata_gerada.docx",
            "Documentos Word (*.docx)"
        )
        if not caminho:
            return

        self.progress_dialog = QProgressDialog("Gerando ATA...", "Cancelar", 0, 0, self)
        self.progress_dialog.setWindowTitle("Aguarde")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setModal(True)
        self.progress_dialog.show()

        self.worker = AtaWorker(texto_transcricao, caminho)
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = resource_path(os.path.join("ui", "windowicon.ico"))
    app.setWindowIcon(QIcon(icon_path))  # Ícone global do app

    style_path = resource_path(os.path.join("ui", "style.qss"))
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            style = f.read()
            app.setStyleSheet(style)
    else:
        print(f"Aviso: arquivo de estilo não encontrado em {style_path}")

    window = MainWindow()
    window.setWindowIcon(QIcon(icon_path))  # Ícone da janela
    window.show()
    sys.exit(app.exec())

