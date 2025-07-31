#!/usr/bin/python3
from PyQt6.QtWidgets import (QMainWindow, QApplication, QPlainTextEdit, QVBoxLayout, 
                            QWidget, QToolBar, QStatusBar, QFileDialog, QLabel, QMenu)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor, QColor, QFont
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer, QEventLoop  # Adicione QEventLoop

from TerminalWidget import TerminalWidget
import serial
import serial.tools.list_ports

class PDTermPro(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configurações iniciais
        self.serial_port = None
        self._init_ui()
        self._setup_theme()
        self._scan_ports()
        
        # Timer para leitura serial
        self.timer = QTimer()
        self.timer.timeout.connect(self._read_serial)
        self.timer.start(50)  # 20 FPS

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
            (" Conectar", self._toggle_serial),
            (" Enviar Arquivo", self._send_file),
            (" Testar ANSI", self.test_ansi_support),  # Novo botão de teste            
            (" Salvar Log", self._save_log),
            (" Portas", self._scan_ports),
            (" MeuItem", self._meu_item),
            (" Limpar", self.terminal.clear),
        ]
        
        for text, callback in actions:
            action = toolbar.addAction(text)
            action.triggered.connect(callback)
    def _meu_item(self):
        self.terminal.write_terminal("Meu item")
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
            
    def test_ansi_support(self):
        self.pgordao_terminal_mode()
        """Testa os comandos ANSI/VT100 no terminal"""
        from PyQt6.QtCore import QTimer, QEventLoop  # Import local para garantir
        
        tests = [
            ("Limpar tela", b'\x1b[2J'),
            ("Cursor pos 5,5", b'\x1b[5;5H'),
            ("Texto vermelho", b'\x1b[31mTeste\x1b[0m'),
            ("Reset terminal", b'\x1bc')
        ]
        
        self.terminal.write_terminal("\n=== TESTE DE SUPORTE ANSI ===\n")
        for desc, code in tests:
            self.terminal.write_terminal(f"\nTestando {desc}: ")
            self.terminal.write_terminal(code.decode('ascii'))
            
            # Processa eventos e espera 500ms
            timer = QTimer(self)
            timer.setSingleShot(True)
            loop = QEventLoop(self)
            timer.timeout.connect(loop.quit)
            timer.start(500)
            loop.exec()


    def _delay(self, ms):
        """Pausa a execução sem bloquear a interface"""
        loop = QEventLoop()
        QTimer.singleShot(ms, loop.quit)
        loop.exec()

