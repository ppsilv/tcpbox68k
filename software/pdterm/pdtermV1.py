#!/usr/bin/python3
import sys
from PyQt6.QtWidgets import (QMainWindow, QApplication, QPlainTextEdit, QVBoxLayout, 
                            QWidget, QToolBar, QStatusBar, QFileDialog, QLabel, QMenu)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor, QColor, QFont
import serial
import serial.tools.list_ports

class TerminalWidget(QPlainTextEdit):
    data_to_send = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_appearance()
        self._prompt = "> "
        self._init_terminal()
        self._history = []
        self._history_index = 0

    def _setup_appearance(self):
        """Configuração visual do terminal"""
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: black;
                color: #00FF00;
                font-family: 'Courier New';
                font-size: 12pt;
                border: 1px solid #00aa00;
            }
        """)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setCursorWidth(8)  # Cursor largo e visível
        self.setMouseTracking(False)
    
    def _init_terminal(self):
        self.clear()
        self.insertPlainText(self._prompt)
        self._command_buffer = ""
        self._command_pos = 0
        self.clear()
        self.insertPlainText(self._prompt)
        self._command_buffer = ""
        self._command_pos = 0
        self.setCursorWidth(10)  # Cursor mais visível
        self._move_cursor_to_end()
        self.setMouseTracking(False)  # Desativa tracking do mouse
        
    def keyPressEvent(self, event):
        key = event.key()
        char = event.text()
        self._move_cursor_to_end()        
        
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self._execute_command()
            return
            
        if key == Qt.Key.Key_Backspace:
            if len(self._command_buffer) > 0:
                self._command_buffer = self._command_buffer[:-1]
                self._update_display()
            return
            
        if key == Qt.Key.Key_Up:
            self._recall_history(-1)
            return
            
        if key == Qt.Key.Key_Down:
            self._recall_history(1)
            return
            
        if char and key != Qt.Key.Key_Backspace:
            self._command_buffer += char
            self._update_display()
    
    def _recall_history(self, direction):
        if not self._history:
            return
            
        self._history_index = max(0, min(self._history_index + direction, len(self._history) - 1))
        self._command_buffer = self._history[self._history_index]
        self._update_display()
    
    def _update_display(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.insertText(self._prompt + self._command_buffer)
        self.setTextCursor(cursor)
    
    def _execute_command(self):
        command = self._command_buffer.strip()
        if command:
            self._history.append(command)
            self._history_index = len(self._history)
            self.data_to_send.emit(command)
            
        self.insertPlainText("\n")
        self._command_buffer = ""
        self.insertPlainText(self._prompt)
        self.ensureCursorVisible()
    
    def append_output(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        self.insertPlainText(text)
        self.ensureCursorVisible()
    def mousePressEvent(self, event):
        """Ignora cliques do mouse para manter o cursor na posição correta"""
        self._move_cursor_to_end()
    
    def mouseDoubleClickEvent(self, event):
        """Ignora duplo-clique"""
        self._move_cursor_to_end()
    
    def mouseMoveEvent(self, event):
        """Ignora movimentos do mouse"""
        pass
    
    def _move_cursor_to_end(self):
        """Move o cursor para o final da linha de comando"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        
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
                background-color: #2e2e2e;
                color: #00aa00;
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
            (" Salvar Log", self._save_log),
            (" Portas", self._scan_ports),
            (" Limpar", self.terminal.clear),
        ]
        
        for text, callback in actions:
            action = toolbar.addAction(text)
            action.triggered.connect(callback)
    
    def _send_to_serial(self, data):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(data.encode('utf-8'))
                self.serial_port.flush()
            except Exception as e:
                self.terminal.append_output(f"\n[ERRO] Falha ao enviar: {str(e)}\n")
    
    def _read_serial(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    self.terminal.append_output(data.decode('ascii', errors='replace'))
            except Exception as e:
                self.terminal.append_output(f"\n[ERRO] Leitura serial: {str(e)}\n")
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
            self.terminal.append_output(msg)
        else:
            self.terminal.append_output("\n[INFO] Nenhuma porta serial relevante encontrada\n")
        
        return filtered_ports
            
    def _show_port_dialog(self):
        """Mostra diálogo apenas com portas relevantes"""
        ports = self._scan_ports()  # Agora usa a lista filtrada
        
        if not ports:
            self.terminal.append_output("\n[ERRO] Nenhuma porta serial relevante encontrada!\n")
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
            self.baud_label.setText(f"Baudrate: 9600")
            self.terminal.append_output(f"\n[INFO] Conectado à {port_name}\n")
        except Exception as e:
            self.terminal.append_output(f"\n[ERRO] Falha na conexão com {port_name}: {str(e)}\n")
            self.serial_port = None
    
    def _disconnect_serial(self):
        if self.serial_port:
            self.serial_port.close()
            self.terminal.append_output("\n[INFO] Porta serial desconectada\n")
        self.serial_port = None
        self.port_label.setText("Porta: Desconectado")
        self.baud_label.setText("Baudrate: -")
    

    
    def _send_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecione o arquivo")
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self._send_to_serial(content)
                    self.terminal.append_output(f"\n[INFO] Arquivo enviado: {file_path}\n")
            except Exception as e:
                self.terminal.append_output(f"\n[ERRO] Falha ao enviar arquivo: {str(e)}\n")
    
    def _save_log(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Log")
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.terminal.toPlainText())
                self.terminal.append_output(f"\n[INFO] Log salvo em: {file_path}\n")
            except Exception as e:
                self.terminal.append_output(f"\n[ERRO] Falha ao salvar log: {str(e)}\n")
    
    def closeEvent(self, event):
        self._disconnect_serial()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = PDTermPro()
    window.show()
    sys.exit(app.exec())
