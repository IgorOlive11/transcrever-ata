import os
from PySide6.QtWidgets import QDialog, QMessageBox, QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTextEdit, QSpinBox, QPushButton
from PySide6.QtCore import QTimer, QDate, QTime
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice


class DialogInfoAssembleia(QDialog):
    def __init__(self, parent=None, transcricao=""):
        super().__init__(parent)
        self.transcricao = transcricao
        self.ui_widget = None
        
        # Carregar o arquivo .ui
        self.load_ui()
        
        # Aplicar estilo
        self.apply_stylesheet()
        
        # Mapear widgets
        self.map_widgets()
        
        # Configurar sinais
        self.setup_connections()
        
        # Preencher valores padrão
        self.preencherValoresPadrao()

    def load_ui(self):
        """Carrega o arquivo .ui do Qt Designer"""
        # Determinar possíveis caminhos do arquivo .ui
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(current_dir, "ui", "dialog_assembleia.ui"),
            os.path.join(os.path.dirname(current_dir), "ui", "dialog_assembleia.ui"),
            os.path.join(current_dir, "..", "ui", "dialog_assembleia.ui"),
            "ui/dialog_assembleia.ui",  # Caminho relativo
            "dialog_assembleia.ui"      # Diretório atual
        ]
        
        ui_path = None
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            print(f"Testando caminho: {abs_path}")
            if os.path.exists(abs_path):
                ui_path = abs_path
                print(f"✓ Arquivo .ui encontrado em: {ui_path}")
                break
        
        if not ui_path:
            # Lista todos os caminhos testados no erro
            paths_str = "\n".join([f"  - {os.path.abspath(p)}" for p in possible_paths])
            raise FileNotFoundError(
                f"Arquivo dialog_assembleia.ui não encontrado.\n\n"
                f"Caminhos testados:\n{paths_str}\n\n"
                f"Diretório atual: {os.getcwd()}\n"
                f"Arquivo atual: {__file__}"
            )
        
        # Carregar o arquivo UI
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        
        if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
            raise RuntimeError(f"Não foi possível abrir o arquivo .ui: {ui_path}")
        
        print(f"Carregando arquivo .ui: {ui_path}")
        
        # Carrega a UI sem parent para evitar conflitos
        self.ui_widget = loader.load(ui_file)
        ui_file.close()
        
        if self.ui_widget is None:
            raise RuntimeError("Falha ao carregar o arquivo .ui - QUiLoader retornou None")
        
        print(f"✓ Arquivo .ui carregado com sucesso. Tipo: {type(self.ui_widget)}")
        
        # Configurar este diálogo com as propriedades do .ui
        self.setWindowTitle(self.ui_widget.windowTitle() or "Informações da Assembleia")
        self.setModal(True)
        
        # Copiar tamanho
        if hasattr(self.ui_widget, 'size'):
            size = self.ui_widget.size()
            self.resize(size.width(), size.height())
            print(f"Redimensionado para: {size.width()}x{size.height()}")
        else:
            self.resize(700, 716)
            print("Usando tamanho padrão: 700x716")
        
        # Simplesmente adicionar o widget carregado como conteúdo
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui_widget)
        print("✓ Widget .ui adicionado ao layout")

    def map_widgets(self):
        """Mapeia os widgets do .ui para atributos da classe"""
        if not self.ui_widget:
            print("ERRO: ui_widget é None, não é possível mapear widgets")
            return
        
        # Debug: listar todos os widgets filhos
        print("\n=== WIDGETS ENCONTRADOS ===")
        for child in self.ui_widget.findChildren(QLineEdit):
            print(f"QLineEdit: {child.objectName()}")
        for child in self.ui_widget.findChildren(QComboBox):
            print(f"QComboBox: {child.objectName()}")
        for child in self.ui_widget.findChildren(QPushButton):
            print(f"QPushButton: {child.objectName()}")
        for child in self.ui_widget.findChildren(QDateEdit):
            print(f"QDateEdit: {child.objectName()}")
        for child in self.ui_widget.findChildren(QTimeEdit):
            print(f"QTimeEdit: {child.objectName()}")
        for child in self.ui_widget.findChildren(QTextEdit):
            print(f"QTextEdit: {child.objectName()}")
        for child in self.ui_widget.findChildren(QSpinBox):
            print(f"QSpinBox: {child.objectName()}")
        print("=== FIM DA LISTA ===\n")
            
        # Inputs principais (seção Informações Gerais)
        self.edit_nome_condominio = self.ui_widget.findChild(QLineEdit, "editNomeCondominio")
        self.edit_endereco_condominio = self.ui_widget.findChild(QLineEdit, "editEnderecoCondominio")
        self.combo_tipo_assembleia = self.ui_widget.findChild(QComboBox, "comboTipoAssembleia")
        self.date_assembleia = self.ui_widget.findChild(QDateEdit, "dateAssembleia")
        self.time_inicio = self.ui_widget.findChild(QTimeEdit, "timeInicio")
        
        # Pauta
        self.edit_pautas = self.ui_widget.findChild(QTextEdit, "editPautas")
        
        # Mesa Diretora
        self.edit_presidente_nome = self.ui_widget.findChild(QLineEdit, "editPresidenteNome")
        self.edit_presidente_apto = self.ui_widget.findChild(QLineEdit, "editPresidenteApto")
        self.edit_secretario_nome = self.ui_widget.findChild(QLineEdit, "editSecretarioNome")
        self.edit_secretario_apto = self.ui_widget.findChild(QLineEdit, "editSecretarioApto")
        
        # Participação
        self.spin_presentes = self.ui_widget.findChild(QSpinBox, "spinNumPresentes")
        self.edit_local_realizacao = self.ui_widget.findChild(QLineEdit, "editLocalRealizacao")
        
        # Botões
        self.btn_ia_nome = self.ui_widget.findChild(QPushButton, "btnIaNomeCondominio")
        self.btn_ia_pautas = self.ui_widget.findChild(QPushButton, "btnIaPautas")
        self.btn_cancelar = self.ui_widget.findChild(QPushButton, "btnCancelar")
        self.btn_ok = self.ui_widget.findChild(QPushButton, "btnGerarAta")
        
        # Debug: verificar se widgets foram encontrados
        widgets_mapping = {
            'edit_nome_condominio': self.edit_nome_condominio,
            'edit_endereco_condominio': self.edit_endereco_condominio,
            'combo_tipo_assembleia': self.combo_tipo_assembleia,
            'date_assembleia': self.date_assembleia,
            'time_inicio': self.time_inicio,
            'edit_pautas': self.edit_pautas,
            'edit_presidente_nome': self.edit_presidente_nome,
            'edit_presidente_apto': self.edit_presidente_apto,
            'edit_secretario_nome': self.edit_secretario_nome,
            'edit_secretario_apto': self.edit_secretario_apto,
            'spin_presentes': self.spin_presentes,
            'edit_local_realizacao': self.edit_local_realizacao,
            'btn_ia_nome': self.btn_ia_nome,
            'btn_ia_pautas': self.btn_ia_pautas,
            'btn_cancelar': self.btn_cancelar,
            'btn_ok': self.btn_ok
        }
        
        print("\n=== MAPEAMENTO DE WIDGETS ===")
        for name, widget in widgets_mapping.items():
            status = "✓ ENCONTRADO" if widget is not None else "✗ NÃO ENCONTRADO"
            print(f"{name}: {status}")
        print("=== FIM DO MAPEAMENTO ===\n")

    def apply_stylesheet(self):
        """Aplica o stylesheet do arquivo style.qss"""
        # Tentar diferentes caminhos para o arquivo de estilo
        current_dir = os.path.dirname(os.path.abspath(__file__))
        style_paths = [
            os.path.join(current_dir, "ui", "style.qss"),
            os.path.join(os.path.dirname(current_dir), "ui", "style.qss"),
            os.path.join(current_dir, "..", "ui", "style.qss")
        ]
        
        stylesheet_loaded = False
        for style_path in style_paths:
            if os.path.exists(style_path):
                try:
                    with open(style_path, 'r', encoding='utf-8') as file:
                        stylesheet = file.read()
                        
                    # Aplicar apenas o stylesheet do arquivo, sem estilos adicionais
                    self.setStyleSheet(stylesheet)
                    stylesheet_loaded = True
                    print(f"✓ Stylesheet carregado de: {style_path}")
                    break
                    
                except Exception as e:
                    print(f"Erro ao carregar stylesheet de {style_path}: {e}")
        
        if not stylesheet_loaded:
            print("Nenhum arquivo de estilo encontrado, usando estilo padrão do sistema")

    def setup_connections(self):
        """Configura os sinais e slots"""
        if self.btn_ia_nome:
            self.btn_ia_nome.clicked.connect(
                lambda: self.detectar_por_ia('nome_condominio', self.btn_ia_nome)
            )
            print("✓ btn_ia_nome conectado")
        else:
            print("✗ btn_ia_nome não encontrado para conectar sinal")
        
        if self.btn_ia_pautas:
            self.btn_ia_pautas.clicked.connect(
                lambda: self.detectar_por_ia('pautas', self.btn_ia_pautas)
            )
            print("✓ btn_ia_pautas conectado")
        else:
            print("✗ btn_ia_pautas não encontrado para conectar sinal")
        
        if self.btn_cancelar:
            self.btn_cancelar.clicked.connect(self.reject)
            print("✓ btn_cancelar conectado")
        else:
            print("✗ btn_cancelar não encontrado para conectar sinal")
        
        if self.btn_ok:
            self.btn_ok.clicked.connect(self.accept)
            print("✓ btn_ok conectado")
        else:
            print("✗ btn_ok não encontrado para conectar sinal")

    def detectar_por_ia(self, campo, botao):
        """Detecta informações usando IA"""
        if not self.transcricao or not self.transcricao.strip():
            QMessageBox.information(self, "Aviso", "Nenhuma transcrição disponível para detecção por IA.")
            return

        botao.setEnabled(False)
        texto_original = botao.text()
        botao.setText("...")

        try:
            from openai import OpenAI
            import os
            from dotenv import load_dotenv

            load_dotenv()
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            prompts = {
                'nome_condominio': f"Da seguinte transcrição de assembleia, extraia apenas o nome do condomínio: {self.transcricao[:1000]}",
                'pautas': f"Da seguinte transcrição, liste as principais pautas/assuntos discutidos, separados por vírgula: {self.transcricao[:2000]}"
            }

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Extraia apenas a informação solicitada da transcrição, sem explicações adicionais."},
                    {"role": "user", "content": prompts[campo]}
                ],
                temperature=0.1,
                max_tokens=200,
            )

            resultado = response.choices[0].message.content.strip()
            sucesso = False

            if campo == 'nome_condominio' and resultado and self.edit_nome_condominio:
                self.edit_nome_condominio.setText(resultado)
                sucesso = True
            elif campo == 'pautas' and resultado and self.edit_pautas:
                self.edit_pautas.setPlainText(resultado)
                sucesso = True

            if sucesso:
                botao.setText("✓")
                QTimer.singleShot(1500, lambda: self.resetar_botao_ia(botao, texto_original))
            else:
                QMessageBox.warning(self, "IA - Não encontrado", f"Não foi possível detectar {campo.replace('_', ' ')} na transcrição. Tente preencher manualmente.")
                self.resetar_botao_ia(botao, texto_original)

        except Exception as e:
            QMessageBox.critical(self, "Erro na IA", f"Erro na detecção por IA: {str(e)}")
            self.resetar_botao_ia(botao, texto_original)

    def resetar_botao_ia(self, botao, texto_original="IA"):
        """Reseta o botão IA para o estado original"""
        if botao:
            botao.setText(texto_original)
            botao.setEnabled(True)

    def preencherValoresPadrao(self):
        """Preenche valores padrão nos campos"""
        try:
            if self.edit_nome_condominio:
                self.edit_nome_condominio.setText("CONDOMÍNIO MILLENNIUM RESIDENCE")
                print("✓ Nome do condomínio preenchido")
            
            if self.edit_endereco_condominio:
                self.edit_endereco_condominio.setText("Avenida Engenheiro Valdir Pedro Monachesi, 1.400, Aeroporto, Juiz de Fora/MG")
                print("✓ Endereço preenchido")
            
            if self.edit_local_realizacao:
                self.edit_local_realizacao.setText("pelo Zoom dentro do aplicativo Condomob condomínios")
                print("✓ Local de realização preenchido")
            
            if self.edit_pautas:
                self.edit_pautas.setPlainText("Retificação do planejamento orçamentário aprovado na AGO")
                print("✓ Pautas preenchidas")
            
            # Configurar data e hora atuais
            if self.date_assembleia:
                self.date_assembleia.setDate(QDate.currentDate())
                print("✓ Data configurada")
            
            if self.time_inicio:
                self.time_inicio.setTime(QTime.currentTime())
                print("✓ Horário configurado")
                
            # Configurar valor padrão do spinbox
            if self.spin_presentes:
                self.spin_presentes.setValue(20)
                print("✓ Número de presentes configurado")
                
        except Exception as e:
            print(f"Erro ao preencher valores padrão: {e}")

    def obterInformacoes(self):
        """Retorna dicionário com todas as informações preenchidas"""
        try:
            pautas_texto = ""
            if self.edit_pautas:
                pautas_texto = self.edit_pautas.toPlainText().strip()
            
            pautas = [p.strip() for p in pautas_texto.split(',') if p.strip()] if pautas_texto else ["assuntos diversos"]

            return {
                'nome_condominio': self.edit_nome_condominio.text().strip() if self.edit_nome_condominio else "",
                'endereco_condominio': self.edit_endereco_condominio.text().strip() if self.edit_endereco_condominio else "",
                'tipo_assembleia': self.combo_tipo_assembleia.currentText() if self.combo_tipo_assembleia else "EXTRAORDINÁRIA",
                'data_assembleia': self.date_assembleia.date().toString("dd/MM/yyyy") if self.date_assembleia else "",
                'horario_inicio': self.time_inicio.time().toString("hh'h'mm") if self.time_inicio else "",
                'presidente_nome': self.edit_presidente_nome.text().strip() if self.edit_presidente_nome else "",
                'presidente_apartamento': (self.edit_presidente_apto.text().strip() if self.edit_presidente_apto else "") or "N/A",
                'secretario_nome': self.edit_secretario_nome.text().strip() if self.edit_secretario_nome else "",
                'secretario_apartamento': (self.edit_secretario_apto.text().strip() if self.edit_secretario_apto else "") or "N/A",
                'numero_presentes': str(self.spin_presentes.value()) if self.spin_presentes else "20",
                'local_realizacao': self.edit_local_realizacao.text().strip() if self.edit_local_realizacao else "",
                'pautas': pautas
            }
        except Exception as e:
            print(f"Erro ao obter informações: {e}")
            return {}

    @staticmethod
    def obterInformacoesAssembleia(parent=None, transcricao=""):
        """Método estático para criar e exibir o diálogo"""
        try:
            print("=== INICIANDO CARREGAMENTO DO DIÁLOGO ===")
            dialog = DialogInfoAssembleia(parent, transcricao)
            print("=== DIÁLOGO CRIADO, EXIBINDO ===")
            resultado = dialog.exec()
            if resultado == QDialog.DialogCode.Accepted:
                return dialog.obterInformacoes()
            return None
        except Exception as e:
            import traceback
            error_msg = f"Erro ao carregar diálogo: {str(e)}\n\nDetalhes:\n{traceback.format_exc()}"
            print(error_msg)  # Para debug
            QMessageBox.critical(None, "Erro", error_msg)
            return None