import threading
import serial
import queue
import serial
import serial.tools.list_ports
from typing import Optional
from typing import Optional, Union

class SerialReadWrite:
    buffer = queue.Queue()  # Buffer compartilhado (só a thread de leitura escreve aqui)
    
    def __init__(self):
        #self.port = port
        #self.baudrate = baudrate
        self._port_lock = threading.Lock()
        self.timeout = 1
        self.porta_serial: Optional[serial.Serial] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.current_reader: Optional[str] = None  # Leitor ativo no momento
        #self._connect()

    def _connect(self, porta: str, baudrate: int = 9600):
        """Método de conexão robusto"""
        with self._port_lock:
            self._disconnect_serial(silent=True)  # Fecha qualquer conexão existent        
        """Abre a conexão serial."""
        try:
            self.porta_serial = serial.Serial(
                porta,
                baudrate=baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
            self.porta_serial.open() 
            return self.porta_serial
        except serial.SerialException as e:
            print(f"Erro ao conectar: {e}")
            return None

    def _disconnect_serial(self, silent=False):
        """Desconecta a porta serial. Se silent=True, não mostra mensagem."""
        if self.porta_serial:
            try:
                self.porta_serial.close()
                #if not silent:
                    #self.terminal.write_terminal("\n[INFO] Porta serial desconectada\n")
            except Exception as e:
                #self.terminal.write_terminal(f"\n[ERRO] Falha ao desconectar: {str(e)}\n")
                return False
            finally:
                self.porta_serial = None
                return True
            
    def start(self):
        """Inicia a thread de leitura serial."""
        if not self.running and self.porta_serial:
            self.running = True
            self.thread = threading.Thread(target=self._read, daemon=True)
            self.thread.start()

    def stop(self):
        """Para a thread e fecha a porta serial."""
        self.running = False
        if self.thread:
            self.thread.join()
        if self.porta_serial:
            self.porta_serial.close()
    
    #def is_connected(self) -> bool:
    #    """
    #    Verifica se a porta serial está conectada e aberta.
    #    
    #    Returns:
    #        True se a porta está conectada e aberta, False caso contrário
    #    """
    #    return self.porta_serial is not None and self.porta_serial.is_open

    def is_connected(self) -> bool:
        """Verificação robusta de conexão"""
        with self._port_lock:
            return (self.porta_serial is not None and
                    hasattr(self.porta_serial, 'is_open') and
                    self.porta_serial.is_open)
        
    def _read(self):
        #print(f"Debug - Port status: {self.porta_serial.is_open if self.porta_serial else 'None'}")
        #print(f"Debug - Port object: {id(self.porta_serial)}")        
        while self.running and self.porta_serial and self.porta_serial.is_open:
            try:
                raw_data = self.porta_serial.readline()  # Lê com \r\n
                data = raw_data.decode('utf-8', errors='replace')  # Decodifica sem remover nada
                SerialReadWrite.buffer.put(data)  # Preserva todos os caracteres
            except Exception as e:
                print(f"Erro na leitura: {e}")
                break

    def port_write(self, data):
       """Método de escrita com verificação robusta"""
       print(f"\n[DEBUG] Tentando escrever: {data}")
       
       # Verificação EXTRA de existência do objeto
       if not hasattr(self, 'porta_serial') or self.porta_serial is None:
           print("[ERRO CRÍTICO] Objeto serial não existe. Estado atual:")
           print(f"- Thread ativa: {threading.current_thread().name}")
           print(f"- Conexão existente: {hasattr(self, 'porta_serial')}")
           print(f"- Porta aberta: {getattr(self.porta_serial, 'is_open', False) if hasattr(self, 'porta_serial') else 'N/A'}")
           #return False
       
       try:
           with self._port_lock:
               print(f"[DEBUG] Estado pré-escrita:")
               print(f"- Porta: {self.porta_serial.port}")
               print(f"- Baudrate: {self.porta_serial.baudrate}")
               print(f"- Timeout: {self.porta_serial.timeout}")
               print(f"- Aberta: {self.porta_serial.is_open}")
               
               if isinstance(data, str):
                   data = data.encode('utf-8')
               
               bytes_written = self.porta_serial.write(data)
               self.porta_serial.flush()
               print(f"[SUCESSO] {bytes_written} bytes escritos")
               return True
               
       except Exception as e:
           print(f"[ERRO] Falha na escrita: {str(e)}")
           return False
    
    def write1(self, data: Union[str, bytes]) -> bool:
       """Método de escrita com verificação robusta"""
       print(f"\n[DEBUG] Tentando escrever: {data}")
       
       # Verificação EXTRA de existência do objeto
       if not hasattr(self, 'porta_serial') or self.porta_serial is None:
           print("[ERRO CRÍTICO] Objeto serial não existe. Estado atual:")
           print(f"- Thread ativa: {threading.current_thread().name}")
           print(f"- Conexão existente: {hasattr(self, 'porta_serial')}")
           print(f"- Porta aberta: {getattr(self.porta_serial, 'is_open', False) if hasattr(self, 'porta_serial') else 'N/A'}")
           return False
       
       try:
           with self._port_lock:
               print(f"[DEBUG] Estado pré-escrita:")
               print(f"- Porta: {self.porta_serial.port}")
               print(f"- Baudrate: {self.porta_serial.baudrate}")
               print(f"- Timeout: {self.porta_serial.timeout}")
               print(f"- Aberta: {self.porta_serial.is_open}")
               
               if isinstance(data, str):
                   data = data.encode('utf-8')
               
               bytes_written = self.porta_serial.write(data)
               self.porta_serial.flush()
               print(f"[SUCESSO] {bytes_written} bytes escritos")
               return True
               
       except Exception as e:
           print(f"[ERRO] Falha na escrita: {str(e)}")
           return False
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#    def write(self, data: Union[str, bytes]):
#        """
#        Escreve dados na porta serial.
#        
#        Args:
#            data: Dados a serem escritos (string ou bytes)
#        Returns:
#            True se bem sucedido, False caso contrário
#        """
#        print("We are here, if no more messages from me you are in trouble....LoL")
#        print(f"Debug - Port status: {self.porta_serial.is_open if self.porta_serial else 'None'}")
#        print(f"Debug - Port object: {id(self.porta_serial)}")        
#
#        if self.is_connected():
#            try:
#                if isinstance(data, str):
#                    data = data.encode('utf-8')
#                print(f"write: Sending data {str}")
#                self.porta_serial.write(data)
#                self.porta_serial.flush()  # Garante que os dados foram enviados
#                return True
#            except serial.SerialException as e:
#                print(f"Erro ao escrever: {e}")
#                return False
#        else:
#            print("Porta serial não está aberta")
#            return False
    

    def has_data(self, reader_id: str) -> bool:
        return not SerialReadWrite.buffer.empty()

    def set_active_reader(self, reader_id: str):
        """Define qual leitor pode acessar o buffer."""
        self.current_reader = reader_id

    def read_data(self, reader_id: str) -> Optional[str]:
        """Lê dados apenas se for o leitor ativo."""
        if self.current_reader == reader_id and not SerialReadWrite.buffer.empty():
            return SerialReadWrite.buffer.get()
        return None
        
    def reset_input_buffer(self):
        return None
########################################################################
#       _emergency_clear
    def _emergency_clear(self):
        """Limpeza de emergência estilo Ctrl+J nos antigos terminais"""
        if self.porta_serial:
            self.porta_serial.reset_input_buffer()
            #self.terminal.clear()
            print("\n[SISTEMA] Buffer limpo com sucesso!\n")

########################################################################        
                
