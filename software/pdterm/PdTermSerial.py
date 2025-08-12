from PyQt6.QtCore import QThread, pyqtSignal,QTimer
import serial
import os
import serial.tools.list_ports
import termios
import time
from PdTermSerialMonoThread import SerialReadWrite
from typing import Optional, Union

class PdSerial():
    def __init__(self, pdterminal, parent=None, menu_handler=None):
        super().__init__()  # Correto - sem argumentos extras
        self.parent = parent
        self.terminal = pdterminal
        #self.menu_handler = menu_handler
        self.thread_serial = SerialReadWrite(self.terminal)
        #self.thread_serial.set_active_reader("MainReader")
         
        self._scan_ports()

#       _toggle_serial
    def _toggle_serial(self):
     if not SerialReadWrite.serial_port or not SerialReadWrite.serial_port.is_open:
         menu = self.menu_handler.create_ports_menu()
         menu.triggered.connect(lambda action: self._connect_to_port(action.text()))
         self.menu_handler._show_menu(menu, "Conectar")
     else:
         print("_toggle_serial(): Disconect from menu...")
         self.thread_serial._disconnect_serial()
         self._update_connection_status()

########################################################################
#       _update_connection_status       COLORIDA
    def _update_connection_status(self):
        if not hasattr(self, 'parent') or self.parent is None:
            return  # Sai silenciosamente se não houver parent
        
        is_connected = self.thread_serial.is_connected()
        
        if is_connected:
            port = SerialReadWrite.port
            baud = SerialReadWrite.baud
            if hasattr(self.parent, 'port_label'):
                self.parent.port_label.setText(f"Porta: {port}")
                self.parent.port_label.setStyleSheet("color: blue;")
            if hasattr(self.parent, 'baud_label'):
                self.parent.baud_label.setText(f"Baudrate: {baud}")
        else:
            if hasattr(self.parent, 'port_label'):
                self.parent.port_label.setText("Porta: Desconectado")
                self.parent.port_label.setStyleSheet("color: red;")
            if hasattr(self.parent, 'baud_label'):
                self.parent.baud_label.setText("Baudrate: -")
########################################################################
#       _connect_to_port
    def _connect_to_port(self, port_name, baud: int = 9600):
        # Limpa o nome da porta (remove descrições extras)
        clean_port_name = port_name.split(' ')[0].strip()
        print(f"_connect_to_port: {clean_port_name} {baud}")
        # Verifica se já está conectado à MESMA porta
        if SerialReadWrite.serial_port and SerialReadWrite.serial_port.is_open:
            if SerialReadWrite.serial_port.port == clean_port_name:
                self.terminal.write_terminal(f"\n[INFO] Já conectado à porta {clean_port_name}\n")
                return True  # Já está conectado, não faz nada
        
        # Verifica se a porta está travada
        lockfile = f"/var/lock/LCK..{clean_port_name.split('/')[-1]}"
        if os.path.exists(lockfile):
            self.terminal.write_terminal(f"\n[ERRO] A porta {clean_port_name} está travada por outro programa\n")
            return False
            
            
        print(f"[_connect_to_port] Objeto Antes conexao: {SerialReadWrite.serial_port}")  # ⚠️ Verifique se não é None            
        
        try:
            # Tentativa de conexão serial
            self.thread_serial._connect(clean_port_name, baud)
            
            # Inicialização das threads
            try:
                self.thread_serial.start()
            except threading.ThreadError as e:
                self.terminal.write_terminal(f"\n[ERRO] Falha ao iniciar threads: {str(e)}\n")
                self.thread_serial._disconnect_serial()  # Garante limpeza
                self._update_connection_status()
                return False
        
            # Operações pós-conexão
            try:
                self.thread_serial.reset_input_buffer()
            except serial.SerialException as e:
                self.terminal.write_terminal(f"\n[ERRO] Falha ao limpar buffer: {str(e)}\n")
                self.thread_serial.stop()  # Para as threads primeiro
                self.thread_serial._disconnect_serial()
                self._update_connection_status()
                return False
        
            # Verificação final
            if SerialReadWrite.serial_port is not None:
                self.terminal.write_terminal(f"\n[INFO] Conectado à porta {clean_port_name}\n")
                self._update_connection_status()
                return True
                
            return False
    
        except serial.SerialException as e:
            # Falhas específicas da conexão serial
            error_msg = f"\n[ERRO] Falha na conexão serial ({e.__class__.__name__}): {str(e)}\n"
            self.terminal.write_terminal(error_msg)
            
        except Exception as e:
            # Falhas genéricas
            error_msg = f"\n[ERRO CRÍTICO] ({e.__class__.__name__}): {str(e)}\n"
            self.terminal.write_terminal(error_msg)
            
        finally:
            if not (SerialReadWrite.serial_port and SerialReadWrite.serial_port.is_open):
                self._update_connection_status()

    def stop_thread_write_to_terminal():
        print("PdTermSerial.py: Calling thread_serial.stop_thread_write_to_terminal" )
        self.thread_serial.stop_thread_write_to_terminal.stop()
                
########################################################################
#       stop_thread_write_terminal
    def stop_thread_write_terminal(self, silent=False):
        self.thread_serial.stop_thread_write_to_terminal()
        
########################################################################
#       stop_thread_write_terminal
    def start_thread_write_terminal(self, silent=False):
        self.thread_serial.star_thread_write_to_terminal()

    def write_to_serial(self, data: Union[str, bytes]):
        self.thread_serial.write(data)
        
    def read_serial_input_buffer(self):
        return self.thread_serial.read_input_buffer()
########################################################################
#       _send_to_serial
    def _send_to_serial(self, data):
        print(f"Sending data through serial...{data}");
        self.thread_serial.write(data)      

########################################################################
#       _read_serial
#    def _read_serial(self):
#        if self.thread_serial.has_data("MainReader"):
#            data = self.thread_serial.read_data("MainReader")
#            self.terminal.write_terminal(data)
#            self.print_hex_buffer(data,8,True,True)
#            self._update_connection_status()

    def _read_serial(self):
        dados = self.thread_serial.ler_dados()
        self.terminal.write_terminal(dados)

    def ler(self):
        dados = self.thread_serial.ler_dados()
        print(dados)
        
#    def print_hex_buffer(self,buffer, bytes_per_line=16, show_offset=True, show_ascii=True):
#        """
#        Imprime um buffer em formato hexadecimal.
#        
#        Args:
#            buffer: Pode ser bytes, bytearray, lista de inteiros ou string
#            bytes_per_line: Número de bytes por linha (padrão 16)
#            show_offset: Mostra o offset hexadecimal (padrão True)
#            show_ascii: Mostra representação ASCII (padrão True)
#        """
#        # Converte strings para bytes se necessário
#        if isinstance(buffer, str):
#            buffer = buffer.encode('latin-1')
#        
#        offset = 0
#        for i in range(0, len(buffer), bytes_per_line):
#            chunk = buffer[i:i+bytes_per_line]
#            
#            # Linha de offset
#            if show_offset:
#                print(f"{offset:08x}:  ", end='')
#            
#            # Hex dump - converte cada elemento para inteiro primeiro
#            hex_str = []
#            for item in chunk:
#                if isinstance(item, str):
#                    num = ord(item)  # Converte char para int
#                else:
#                    num = item       # Já é int/byte
#                hex_str.append(f"{num:02x}")
#            
#            hex_part = ' '.join(hex_str)
#            print(hex_part.ljust(bytes_per_line * 3), end='  ')
#            
#            # Representação ASCII
#            if show_ascii:
#                ascii_part = []
#                for b in chunk:
#                    if isinstance(b, str):
#                        char = b if 32 <= ord(b) <= 126 else '.'
#                    else:
#                        char = chr(b) if 32 <= b <= 126 else '.'
#                    ascii_part.append(char)
#                print(f"|{''.join(ascii_part)}|", end='')
#            
#            print()
#            offset += bytes_per_line

            
########################################################################
#       _bytes_to_hex            
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
        self.thread_serial._disconnect_serial()
        event.accept()
        
        
        
        
        
        
