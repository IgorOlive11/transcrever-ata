# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'interface.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 602)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.background = QWidget(self.centralwidget)
        self.background.setObjectName(u"background")
        self.gridLayout = QGridLayout(self.background)
        self.gridLayout.setObjectName(u"gridLayout")
        self.btnEscolher = QPushButton(self.background)
        self.btnEscolher.setObjectName(u"btnEscolher")
        self.btnEscolher.setMinimumSize(QSize(0, 30))
        font = QFont()
        font.setFamilies([u"Bahnschrift"])
        font.setBold(True)
        self.btnEscolher.setFont(font)

        self.gridLayout.addWidget(self.btnEscolher, 3, 0, 1, 1)

        self.textEdit = QTextEdit(self.background)
        self.textEdit.setObjectName(u"textEdit")

        self.gridLayout.addWidget(self.textEdit, 6, 0, 1, 3)

        self.label_status = QLabel(self.background)
        self.label_status.setObjectName(u"label_status")
        font1 = QFont()
        font1.setFamilies([u"Bahnschrift"])
        font1.setPointSize(10)
        font1.setBold(False)
        font1.setItalic(False)
        self.label_status.setFont(font1)
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_status, 8, 0, 1, 1)

        self.label = QLabel(self.background)
        self.label.setObjectName(u"label")
        font2 = QFont()
        font2.setFamilies([u"Bahnschrift"])
        font2.setPointSize(14)
        font2.setBold(False)
        self.label.setFont(font2)

        self.gridLayout.addWidget(self.label, 5, 0, 1, 3)

        self.lineEditArquivo = QLineEdit(self.background)
        self.lineEditArquivo.setObjectName(u"lineEditArquivo")
        self.lineEditArquivo.setMinimumSize(QSize(0, 30))

        self.gridLayout.addWidget(self.lineEditArquivo, 3, 1, 1, 1)

        self.btnGerar = QPushButton(self.background)
        self.btnGerar.setObjectName(u"btnGerar")
        self.btnGerar.setMinimumSize(QSize(0, 30))
        font3 = QFont()
        font3.setFamilies([u"Bahnschrift"])
        font3.setPointSize(12)
        font3.setBold(True)
        self.btnGerar.setFont(font3)

        self.gridLayout.addWidget(self.btnGerar, 7, 0, 1, 3)

        self.btnTranscrever = QPushButton(self.background)
        self.btnTranscrever.setObjectName(u"btnTranscrever")
        self.btnTranscrever.setMinimumSize(QSize(0, 30))
        self.btnTranscrever.setFont(font3)

        self.gridLayout.addWidget(self.btnTranscrever, 4, 0, 1, 2)

        self.tittle = QLabel(self.background)
        self.tittle.setObjectName(u"tittle")
        font4 = QFont()
        font4.setFamilies([u"Bahnschrift"])
        font4.setPointSize(22)
        self.tittle.setFont(font4)
        self.tittle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.tittle, 0, 0, 1, 2)


        self.verticalLayout.addWidget(self.background)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 25))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Transcrever ATA", None))
        self.btnEscolher.setText(QCoreApplication.translate("MainWindow", u"Escolher Arquivo", None))
        self.label_status.setText(QCoreApplication.translate("MainWindow", u"Status da opera\u00e7\u00e3o...", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Transcri\u00e7\u00e3o:", None))
        self.btnGerar.setText(QCoreApplication.translate("MainWindow", u"Gerar Sintese", None))
        self.btnTranscrever.setText(QCoreApplication.translate("MainWindow", u"Transcrever", None))
        self.tittle.setText(QCoreApplication.translate("MainWindow", u"Transcrever ATA", None))
    # retranslateUi

