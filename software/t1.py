# 📜 psterm.py - O Terminal dos Deuses (PyQt6 Edition)
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QTextEdit, QVBoxLayout, 
    QWidget, QToolBar, QStatusBar, QFileDialog, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QTextCharFormat
import serial
import serial.tools.list_ports

class PDTermPro(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 🎨 Configuração da Janela (Estilo Retrô-Moderno)
        self.setWindowTitle("PDTerm Pro 9000 - PYTHON POWER")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("""
            background-color: #1e1e1e;
            color: #00ff00;
        """)
        
        # 🔧 Componentes Principais
        self.console = QTextEdit()
        self.console.setFont(QFont("Courier New", 12))
        self._setup_console_theme()
        
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #00ff00;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00aa00;
            }
        """)
        
        # 🛠️ Toolbar (Ícones + Ações)
        toolbar = QToolBar()
        self._setup_toolbar(toolbar)
        
        # 📌 Layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.console)
        layout.addWidget(self.progress)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # 🌐 Status Bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Pronto para dominar o RS232!")
        
        # 🔌 Variáveis de Estado
        self.serial_port = None
        self._scan_ports()

    def _setup_console_theme(self):
        # Estilo do Console (Cores ANSI simuladas)
        palette = self.console.palette()
        palette.setColor(palette.ColorRole.Base, QColor(0, 0, 0))
        palette.setColor(palette.ColorRole.Text, QColor(0, 255, 0))
        self.console.setPalette(palette)

    def _setup_toolbar(self, toolbar):
        # Ícones e Ações
        actions = [
            ("🔌 Conectar", self._toggle_serial),
            ("📤 XMODEM", self._xmodem_send),
            ("💾 Salvar Log", self._save_log),
            ("🎚️ Config", self._show_settings),
        ]
        
        for text, callback in actions:
            action = toolbar.addAction(text)
            action.triggered.connect(callback)

    def _scan_ports(self):
        ports = serial.tools.list_ports.comports()
        self.status.showMessage(f"Portas encontradas: {[p.device for p in ports]}")

    def _toggle_serial(self):
        if not self.serial_port:
            try:
                self.serial_port = serial.Serial(
                    "/dev/ttyUSB0", 
                    baudrate=9600,
                    timeout=1
                )
                self._start_serial_monitor()
                self.status.showMessage(f"Conectado a {self.serial_port.name}")
            except Exception as e:
                self.console.append(f"ERRO: {str(e)}")
        else:
            self.serial_port.close()
            self.serial_port = None
            self.status.showMessage("Desconectado")

    def _start_serial_monitor(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._read_serial)
        self.timer.start(100)  # 10 FPS

    def _read_serial(self):
        if self.serial_port and self.serial_port.in_waiting:
            data = self.serial_port.read(self.serial_port.in_waiting)
            self.console.insertPlainText(data.decode('ascii', errors='replace'))
            self.console.ensureCursorVisible()

    def _xmodem_send(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecione o arquivo")
        if file_path:
            self.console.append(f"\n>>> Iniciando XMODEM: {file_path}")
            self.progress.setValue(0)
            # TODO: Implementar XMODEM aqui!
            self._simulate_transfer()

    def _simulate_transfer(self):
        # Simulação de transferência (remova no código real!)
        for i in range(1, 101):
            QApplication.processEvents()  # Mantém a UI responsiva
            self.progress.setValue(i)
            QTimer.singleShot(50, lambda: None)  # Pequeno delay

    def _save_log(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Log")
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.console.toPlainText())

    def _show_settings(self):
        self.console.append("\n⚙️ Configurações do PDTerm Pro:")
        self.console.append(" - Baud Rate: 9600")
        self.console.append(" - Data Bits: 8")
        self.console.append(" - Dark Mode: ON")

# 🚀 Inicialização
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo moderno
    
    window = PDTermPro()
    window.show()
    sys.exit(app.exec())
