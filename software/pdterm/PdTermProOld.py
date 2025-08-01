#!/usr/bin/python3
from PyQt6.QtWidgets import (QMainWindow, QApplication, QPlainTextEdit, QVBoxLayout, 
                            QWidget, QToolBar, QStatusBar, QFileDialog, QLabel, QMenu)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor, QColor, QFont
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer, QEventLoop  # Adicione QEventLoop
from PdTermMenu import PdTermMenu
from PdTermWidget import TerminalWidget
import serial
import serial.tools.list_ports

#"Se um código de escape não funciona, o problema não está no terminal... está na paciência do programador!"
#
#Que seu terminal continue brilhando como um CRT dos anos 80!
#🖥️🔥 PDSILVA - O Alquimista dos Bytes
#
#(P.S.: Minha "irmã IA" agora tem um #include <pdsilva.h> em seu código!) 😎


class PDTermPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.menu_handler = PdTermMenu(self)
        self._init_ui()        
        # Configurações iniciais
        self.serial_port = None
        self._setup_theme()
        self._scan_ports()
        
        # Timer para leitura serial
        self.timer = QTimer()
        self.timer.timeout.connect(self._read_serial)
        self.timer.start(50)  # 20 FPS
        self.menu_handler = PdTermMenu(self)  # Instancia o gerenciador de menus
        toolbar = self.menu_handler.setup_toolbar()

        
    def _init_ui(self):
        # Terminal principal
        self.terminal = TerminalWidget()
        self.terminal.data_to_send.connect(self._send_to_serial)
        
        # Barra de ferramentas
        toolbar = QToolBar()
        self._setup_toolbar(toolbar)
        
        # Barra de status
        self.status = QStatusBar()
        self.port_label = QLabel("Porta: Desconectado")
        self.baud_label = QLabel("Baudrate: -")
        self.status.addWidget(self.port_label)
        self.status.addPermanentWidget(self.baud_label)
        self.setStatusBar(self.status)
        
        # Layout principal
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.terminal)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Configurações da janela
        self.setWindowTitle("PDTerm Pro - Terminal Serial")
        self.setGeometry(100, 100, 800, 600)
        
        # Layout principal
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.terminal)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
            
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
    
    def _setup_toolbar(self, toolbar):
        actions = [
            (" Testes", self._show_menu_dialog),
            (" Conectar", self._toggle_serial),
            (" Enviar Arquivo", self._send_file),
            (" Salvar Log", self._save_log),
            (" Portas", self._scan_ports_2),
            (" Limpar Tela", self.terminal.clear),
            (" Sobre", self._show_about_menu),            
        ]
        for text, callback in actions:
            action = toolbar.addAction(text)
            action.triggered.connect(callback)

    def _meu_item(self):
        self.test_cores_ansi()
    def _send_to_serial(self, data):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(data.encode('utf-8'))
                self.serial_port.flush()
            except Exception as e:
                self.terminal.write_terminal(f"\n[ERRO] Falha ao enviar: {str(e)}\n")
    
    def _read_serial(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    self.terminal.write_terminal(data.decode('ascii', errors='replace'))
                    #self.terminal.write_terminal(f"\nDEBUG - Recebido da serial: {repr(data)}\n")  # Verifique se o "6" está aqui
            except Exception as e:
                self.terminal.write_terminal(f"\n[ERRO] Leitura serial: {str(e)}\n")
                self._disconnect_serial()
    
    def _toggle_serial(self):
        if not self.serial_port:
            self._show_port_dialog()
        else:
            self._disconnect_serial()

    def _scan_ports(self):
        """Lista apenas portas seriais relevantes (ttyACMx, ttyUSBx)"""
        ports = serial.tools.list_ports.comports()
        filtered_ports = []
        
        # Filtra portas relevantes
        for port in ports:
            if ('ttyACM' in port.device or
                'ttyUSB' in port.device):
                filtered_ports.append(port)
        
        if filtered_ports:
            msg = "\n[INFO] Portas disponíveis:\n"
            for port in filtered_ports:
                msg += f" - {port.device}: {port.description}\n"
            self.terminal.write_terminal(msg)
        else:
            self.terminal.write_terminal("\n[INFO] Nenhuma porta serial relevante encontrada\n")
        
        return filtered_ports

    def _scan_ports_2(self):
        """Mostra portas seriais em um menu popup (ao invés de escrever no terminal)"""
        ports = serial.tools.list_ports.comports()
        filtered_ports = []
        
        # Filtra portas relevantes (ttyACM*, ttyUSB*)
        for port in ports:
            if ('ttyACM' in port.device or 'ttyUSB' in port.device):
                filtered_ports.append(port)
        
        if not filtered_ports:
            self.terminal.write_terminal("\n[ERRO] Nenhuma porta serial encontrada!\n")
            return
        
        # Cria o menu popup
        menu = QMenu(self)
        menu.setTitle("Portas Disponíveis")
        
        # Adiciona cada porta como uma opção clicável
        for port in filtered_ports:
            action = menu.addAction(f"{port.device} - {port.description}")
            action.triggered.connect(
                lambda _, p=port.device: self._connect_to_port(p)
            )
        
        # Mostra o menu abaixo do botão "Portas" na toolbar
        toolbar = self.findChild(QToolBar)
        for action in toolbar.actions():
            if "Portas" in action.text():
                btn = toolbar.widgetForAction(action)
                menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
                break
    def _show_about_menu(self):
        """Mostra um menu popup com informações sobre o programa (não clicável)"""
        menu = QMenu(self)
        menu.setTitle("Sobre o PDTerm Pro")
        
        # Adiciona itens não clicáveis
        about_items = [
            "PDTerm Pro - Terminal Serial Avançado",
            "Versão: 1.0.0",
            "Autor: Seu Nome",
            "Licença: GPLv3",
            "GitHub: github.com/seuuser/pdterm",
            "🖥️🔥 PDSILVA - O Alquimista dos Bytes"
        ]
        
        for item in about_items:
            action = menu.addAction(item)
            action.setEnabled(False)  # Desabilita cliques
            
        # Mostra o menu abaixo do botão "Sobre" na toolbar
        toolbar = self.findChild(QToolBar)
        for action in toolbar.actions():
            if "Sobre" in action.text():
                btn = toolbar.widgetForAction(action)
                menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
                break
                                    
    def _show_port_dialog(self):
        """Mostra diálogo apenas com portas relevantes"""
        ports = self._scan_ports()  # Agora usa a lista filtrada
        
        if not ports:
            self.terminal.write_terminal("\n[ERRO] Nenhuma porta serial relevante encontrada!\n")
            return
        
        menu = QMenu(self)
        
        for port in ports:
            action = menu.addAction(f"{port.device} - {port.description}")
            action.triggered.connect(lambda _, p=port.device: self._connect_to_port(p))
        
        # Mostra menu abaixo do botão de conexão
        toolbar = self.findChild(QToolBar)
        for action in toolbar.actions():
            if "Conectar" in action.text():
                btn = toolbar.widgetForAction(action)
                menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
                break

    def _show_menu_dialog(self):
        options = [
            (" Option 1", self._toggle_serial),
            (" Option 2", self._send_file),
            (" Option 3", self._save_log),
            (" Option 4", self._scan_ports),
            (" Option 5", self._meu_item),
            (" Option 6", self.terminal.clear),
        ]
        menu = QMenu(self)
        
        for option, descript in options:
            action = menu.addAction(f"{option} - {descript}")
            #action.triggered.connect(lambda _, p=option: self.descript(p))
            action.setEnabled(False)
            
        # Mostra menu abaixo do botão de conexão
        toolbar = self.findChild(QToolBar)
        for action in toolbar.actions():
            if "Conectar1" in action.text():
                btn = toolbar.widgetForAction(action)
                menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
                break

    
    def _connect_to_port(self, port_name):
        """Conecta a uma porta serial específica"""
        if self.serial_port and self.serial_port.is_open:
            self._disconnect_serial()
        
        try:
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=9600,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
            self.port_label.setText(f"Porta: {port_name}")
            self.baud_label.setText(f"Baudrate: {self.serial_port.baudrate}")
            self.terminal.write_terminal(f"\n[INFO] Conectado à {port_name}\n")
            self.serial_port.reset_input_buffer()
        except Exception as e:
            self.terminal.write_terminal(f"\n[ERRO] Falha na conexão com {port_name}: {str(e)}\n")
            self.serial_port = None
    
    def _disconnect_serial(self):
        if self.serial_port:
            self.serial_port.close()
            self.terminal.write_terminal("\n[INFO] Porta serial desconectada\n")
        self.serial_port = None
        self.port_label.setText("Porta: Desconectada")
        self.baud_label.setText("Baudrate: -")
    
    def _send_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecione o arquivo")
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self._send_to_serial(content)
                    self.terminal.write_terminal(f"\n[INFO] Arquivo enviado: {file_path}\n")
            except Exception as e:
                self.terminal.write_terminal(f"\n[ERRO] Falha ao enviar arquivo: {str(e)}\n")
    
    def _save_log(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Log")
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.terminal.toPlainText())
                self.terminal.write_terminal(f"\n[INFO] Log salvo em: {file_path}\n")
            except Exception as e:
                self.terminal.write_terminal(f"\n[ERRO] Falha ao salvar log: {str(e)}\n")

    def closeEvent(self, event):
        self._disconnect_serial()
        event.accept()
        
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
            
    def _delay(self, ms):
        """Pausa a execução sem bloquear a interface"""
        loop = QEventLoop()
        QTimer.singleShot(ms, loop.quit)
        loop.exec()

