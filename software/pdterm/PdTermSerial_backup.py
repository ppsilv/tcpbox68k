from PyQt6.QtCore import QThread, pyqtSignal,QTimer
import serial
import os
import serial.tools.list_ports


class PdSerial():
    def __init__(self, pdterminal, parent=None, menu_handler=None):
        super().__init__()  # Correto - sem argumentos extras
        self.parent = parent
        self.terminal = pdterminal
        self.menu_handler = menu_handler
        self.serial_port = None
        
        
        # Timer para leitura serial
        self.timer = QTimer()
        self.timer.timeout.connect(self._read_serial)
        self.timer.start(50)

        self._scan_ports()

        # Configura terminal
       # self.terminal.data_to_send.connect(self._send_to_serial)

                    
########################################################################
#       _emergency_clear
    def _emergency_clear(self):
        """Limpeza de emergência estilo Ctrl+J nos antigos terminais"""
        if self.serial_port:
            self.serial_port.reset_input_buffer()
            #self.terminal.clear()
            print("\n[SISTEMA] Buffer limpo com sucesso!\n")

########################################################################
#       _toggle_serial
    def _toggle_serial(self):
     if not self.serial_port or not self.serial_port.is_open:
         menu = self.menu_handler.create_ports_menu()
         #menu.triggered.connect(lambda action: self._on_port_selected(action.text()))
         menu.triggered.connect(lambda action: self._connect_to_port(action.text()))
         self.menu_handler._show_menu(menu, "Conectar")
     else:
         self._disconnect_serial()

########################################################################
#       _on_port_selected
    def _on_port_selected(self, port_name):
        """Método chamado quando uma porta é selecionada no menu"""
        if self._connect_to_port(port_name):
            self._update_connection_status()

########################################################################
#       _update_connection_status       COLORIDA
    def _update_connection_status(self):
        """Atualiza a UI apenas se a conexão for válida"""
        if self.serial_port is not None and hasattr(self.serial_port, 'is_open') and self.serial_port.is_open:
            self.parent.port_label.setText(f"Porta: {self.serial_port.port}")
            self.parent.baud_label.setText(f"Baudrate: {self.serial_port.baudrate}")
            self.parent.port_label.setStyleSheet("color: blue;")
            self.parent.baud_label.setStyleSheet("color: blue;")
        else:
            self.parent.port_label.setText("Porta: Desconectado")
            self.parent.baud_label.setText("Baudrate: -")
            self.parent.serial_port = None  # Força limpeza se houver algum objeto inválido  
            self.parent.port_label.setStyleSheet("color: red;")
            self.parent.baud_label.setStyleSheet("color: red;")
                    
########################################################################
#       _connect_to_port
    def _connect_to_port(self, port_name):
        # Limpa o nome da porta (remove descrições extras)
        clean_port_name = port_name.split(' ')[0].strip()
        
        # Verifica se já está conectado à MESMA porta
        if self.serial_port and self.serial_port.is_open:
            if self.serial_port.port == clean_port_name:
                self.terminal.write_terminal(f"\n[INFO] Já conectado à porta {clean_port_name}\n")
                return True  # Já está conectado, não faz nada
            else:
                self._disconnect_serial()  # Desconecta se for uma porta diferente
        
        # Verifica se a porta está travada
        lockfile = f"/var/lock/LCK..{clean_port_name.split('/')[-1]}"
        if os.path.exists(lockfile):
            self.terminal.write_terminal(f"\n[ERRO] A porta {clean_port_name} está travada por outro programa\n")
            return False
        
        try:
            self.serial_port = serial.Serial(
                port=clean_port_name,
                baudrate=9600,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            # Mensagem única de sucesso
            self.terminal.write_terminal(f"\n[INFO] Conectado à porta {clean_port_name}\n")
            self._update_connection_status()
            return True
            
        except Exception as e:
            self.terminal.write_terminal(f"\n[ERRO] Falha na conexão: {str(e)}\n")
            self.serial_port = None
            self._update_connection_status()
            return False
            
########################################################################
#       _disconnect_serial
    def _disconnect_serial(self, silent=False):
        """Desconecta a porta serial. Se silent=True, não mostra mensagem."""
        if self.serial_port:
            try:
                self.serial_port.close()
                if not silent:
                    self.terminal.write_terminal("\n[INFO] Porta serial desconectada\n")
            except Exception as e:
                self.terminal.write_terminal(f"\n[ERRO] Falha ao desconectar: {str(e)}\n")
            finally:
                self.serial_port = None
        self._update_connection_status()

########################################################################
#       _send_to_serial
    def _send_to_serial(self, data):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(data.encode('utf-8'))
                self.serial_port.flush()
            except Exception as e:
                self.terminal.write_terminal(f"\n[ERRO] Falha ao enviar: {str(e)}\n")        

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
#       _scan_ports
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
            #self.terminal.write_terminal(msg)
            print(msg)
        else:
            #self.terminal.write_terminal("\n[INFO] Nenhuma porta serial relevante encontrada\n")
            print("\n[INFO] Nenhuma porta serial relevante encontrada\n")
        return filtered_ports
        
########################################################################
#       closeEvent
    def closeEvent(self, event):
        self._disconnect_serial()
        event.accept()
        
        
        
        
        
        
