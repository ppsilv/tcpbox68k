#!/usr/bin/python3
from PyQt6.QtWidgets import (QMainWindow, QApplication, QPlainTextEdit, QVBoxLayout, 
                            QWidget, QToolBar, QStatusBar, QFileDialog, QLabel)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer, QEventLoop
from PyQt6.QtGui import QTextCursor, QColor, QFont
from PdTermMenu import PdTermMenu
from PdTermWidget import TerminalWidget
from PdTermSerial import PdSerial
from PdTermXmodem import XMODEM_Transfer
from PdTermFileHandler import FileHandler  # Importe sua classe
import serial
import serial.tools.list_ports

import os

class PDTermPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler(parent=self)
        #self.serial_port = None
        self.terminal = TerminalWidget()

        # Cria PdSerial UMA ÚNICA VEZ com todos os parâmetros necessários
        self.cserial = PdSerial(
            pdterminal=self.terminal,
            parent=self,  # Garante que parent não seja None
            menu_handler=None  # Será definido depois
        )
        # Depois cria o menu
        self.menu_handler = PdTermMenu(parent=self, pdserial=self.cserial)
        # Completa a referência
        self.cserial.menu_handler = self.menu_handler
        
        self.xmodem = XMODEM_Transfer(parent=self, pdserial=self.cserial)

        
        self.current_data_handler = None  # Pode ser None, terminal ou xmodem

        self._init_ui()
        self._setup_theme()
        #self._scan_ports()
        
        # Timer para leitura serial
        #self.timer = QTimer()
        #self.timer.timeout.connect(self._read_serial)
        #self.timer.start(50)

        # Configura terminal
        #self.terminal.data_to_send.connect(self._send_to_serial)

    def _start_xmodem_transfer(self):
        self.xmodem = XMODEM_Transfer(parent=self, pdserial=self.cserial)
        self.xmodem.serial = self.cserial  # Injeta dependência
        self.xmodem._send_file_xmodem()

    def _init_ui(self):
        """Configuração única da interface"""
        # Configura toolbar através do menu_handler
        toolbar = self.menu_handler.setup_toolbar()
        
        # Barra de status
        self.status = QStatusBar()
        self.port_label = QLabel("Porta: Desconectado")
        self.baud_label = QLabel("Baudrate: -")
        self.status.addWidget(self.port_label)
        self.status.addPermanentWidget(self.baud_label)
        self.setStatusBar(self.status)
        
        # Layout principal (configurado uma única vez)
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.terminal)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.setWindowTitle("PDTerm Pro - Terminal Serial V1")
        self.setGeometry(100, 100, 800, 600)


            
    def _setup_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QToolBar {
                background-color: #2e2e2e;
                border: none;
                padding: 2px;
            }
            QToolButton {
                color: #00ff00;
                background-color: transparent;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #3e3e3e;
            }
            QStatusBar {
                background-color: #FFFFFF;
                color: #FF0000;
            }
            QMenu {
                background-color: #2e2e2e;
                color: #00ff00;
                border: 1px solid #00aa00;
            }
            QMenu::item:selected {
                background-color: #3e3e3e;
            }
        """)
########################################################################
#      SERIAL  INICIO
#    

        
#
#      SERIAL  FIM
########################################################################



########################################################################
#       LOG INICIO
#    
    
    def _save_log(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Log")
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.terminal.toPlainText())
                self.terminal.write_terminal(f"\n[INFO] Log salvo em: {file_path}\n")
            except Exception as e:
                self.terminal.write_terminal(f"\n[ERRO] Falha ao salvar log: {str(e)}\n")


#
#      FILE E LOG  FIM
########################################################################

 
 
    def clear_screen(self):
        """Limpa a tela e envia comando VT102 para limpeza"""
        self.terminal.clear()
        # Envia sequência VT102 para limpar tela
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(b'\x1b[2J')
    
    def set_cursor_position(self, row, col):
        """Posiciona o cursor e envia comando VT102"""
        # Envia sequência VT102 para posicionar cursor
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(f'\x1b[{row};{col}H'.encode('utf-8'))
            
    def pgordao_terminal_mode(self):
        """Ativa o modo lenda do terminal"""
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000066;  /* Azul memória ROM */
                color: #FFFF00;            /* Amarelo display LED */
                font-family: 'Courier New';
                border: 3px solid #FF0000; /* Vermelho do 68k */
            }
        """)
        self.terminal.write_terminal("\n>>> MODO PGORDÃO ATIVADO <<<\n")

    def test_cores_ansi(self):
        """Demonstração épica de cores pelo PGORDÃO"""
        """Teste que não quebra linhas prematuramente"""
        cores = [
            ('Preto', '30'), ('Vermelho', '31'), ('Verde', '32'),
            ('Amarelo', '33'), ('Azul', '34'), ('Magenta', '35'),
            ('Ciano', '36'), ('Branco', '37')
        ]
        
        # Cabeçalho (agora sem afetar contagem)
        self.terminal._ansi_processor.process_text(
            "\x1b[1;31;42m>>> \x1b[3;33mPGORDÃO MODE ACTIVATED\x1b[0;42m \x1b[5;36m<<<\x1b[0m\n"
        )
        # Lista de cores
        for nome, codigo in cores:
            self.terminal._ansi_processor.process_text(f"\x1b[{codigo}m{nome}\x1b[0m ")
        self.tela_login_pgordao()
        self.menu_principal()
        
    def tela_login_pgordao(self):
        """Tela de login que fará o Unix chorar"""
        self.terminal._ansi_processor.process_text(
            #"\x1b[2J\x1b[1;1H"  # Limpa tela
            "\x1b[1;34;40m╔════════════════════════╗\n"
            "\x1b[1;34;40m║ \x1b[1;31mSISTEMA PGORDÃO v1.0 \x1b[1;34m  ║\n"
            "\x1b[1;34;40m╚════════════════════════╝\n"
            "\x1b[33mUsuário: \x1b[37m"
        )


