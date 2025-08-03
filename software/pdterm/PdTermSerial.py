from PyQt6.QtCore import QThread, pyqtSignal,QTimer
import serial
import serial.tools.list_ports

class PdSerial():
    def __init__(self):
        super().__init__()

        self.serial_port = None
        # Timer para leitura serial
        self.timer = QTimer()
        self.timer.timeout.connect(self._read_serial)
        self.timer.start(50)


    def _emergency_clear(self):
        """Limpeza de emergência estilo Ctrl+J nos antigos terminais"""
        if self.serial_port:
            self.serial_port.reset_input_buffer()
            self.terminal.clear()
            self.terminal.write_terminal("\n[SISTEMA] Buffer limpo com sucesso!\n")
        
########################################################################
#       _connect_to_port
    def _connect_to_port(self, port_name):
        lockfile = "/var/lock/LCK..ttyUSB0"  # ou /run/lock/LCK..ttyUSB0
        if os.path.exists(lockfile):
            print("Erro: A porta está travada por outro programa (Minicom?)")
            exit(1)
         
        """Conecta à porta serial com limpeza de buffers"""
        try:
            if self.serial_port and self.serial_port.is_open:
                self._disconnect_serial()
            
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=9600,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
                       
        except Exception as e:
            self.terminal.write_terminal(f"\n[ERRO] Falha na conexão: {str(e)}\n")
            self.serial_port = None        
            
########################################################################
#       _disconnect_serial
    def _disconnect_serial(self):
        if self.serial_port:
            self.serial_port.close()
            self.terminal.write_terminal("\n[INFO] Porta serial desconectada\n")
        self.serial_port = None
        self.port_label.setText("Porta: Desconectada")
        self.baud_label.setText("Baudrate: -")

########################################################################
#       _read_serial
    def _read_serial(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                # Limita a quantidade de dados lidos por vez
                max_bytes_per_read = 1024
                available = min(self.serial_port.in_waiting, max_bytes_per_read)                
                if available > 0:
                    data = ""
                    data = self.serial_port.read(available)

                    self.terminal.write_terminal(data.decode('ascii', errors='replace'))
            except Exception as e:
                self.terminal.write_terminal(f"\n[ERRO]1011 Leitura serial: {str(e)}\n")
                self._disconnect_serial()
    
    def _bytes_to_hex(self, data):
        """Converte bytes para string hexadecimal formatada"""
        return ' '.join(f'{b:02X}' for b in data)        
        
########################################################################
#       _send_to_serial
    def _send_to_serial(self, data):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(data.encode('utf-8'))
                self.serial_port.flush()
            except Exception as e:
                self.terminal.write_terminal(f"\n[ERRO] Falha ao enviar: {str(e)}\n")        
        
        
        
        
        
        
        
        
