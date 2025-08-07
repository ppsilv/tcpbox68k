import threading
import queue
import serial
from typing import Optional, Union

class SerialReaderWriter:
    buffer = queue.Queue()  # Thread-safe buffer
   
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        """
        Inicializa o leitor/escritor serial com uma porta específica.
        
        Args:
            port: Nome da porta serial (ex: 'COM3' ou '/dev/ttyUSB0')
            baudrate: Taxa de transmissão em bauds
            timeout: Timeout para operações de leitura
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_port: Optional[serial.Serial] = None
        #self.buffer = queue.Queue()  # Thread-safe buffer
        self.running = False
        self.thread = threading.Thread(target=self._read_serial, daemon=True)
        
        # Lock para controlar o acesso dos leitores
        self.reader_lock = threading.Lock()
        self.current_reader: Optional[str] = None
        
        # Lock para operações de escrita (para não misturar com leituras)
        self.write_lock = threading.Lock()
        
        # Inicializa a conexão serial
        self._connect()
    
    def _connect(self):
        """Estabelece a conexão serial."""
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            print(f"Conexão estabelecida com {self.port}")
        except serial.SerialException as e:
            print(f"Falha ao conectar em {self.port}: {e}")
            self.serial_port = None
    
    def start(self):
        if self.is_connected() and not self.running:
            self.running = True
            if not self.thread or not self.thread.is_alive():
                self.thread = threading.Thread(target=self._read_serial, daemon=True)
                self.thread.start()
               
    def stop(self):
        """Para a thread de leitura serial e fecha a conexão."""
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        print("Thread de leitura parada e conexão fechada")
    
    def is_connected(self) -> bool:
        """
        Verifica se a porta serial está conectada e aberta.
        
        Returns:
            True se a porta está conectada e aberta, False caso contrário
        """
        return self.serial_port is not None and self.serial_port.is_open
    
    def _read_serial(self):
        """Método interno executado pela thread para ler dados da porta serial."""
        while self.running and self.is_connected():
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline().decode('utf-8').strip()
                    if data:
                        SerialReaderWriter.buffer.put(data)
            except (serial.SerialException, UnicodeDecodeError) as e:
                print(f"Erro na leitura serial: {e}")
                # Tentar reconectar após erro
                self._reconnect()
                continue
    
    def _reconnect(self):
        """Tenta reconectar sem vazamento de threads."""
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)  # Limpa a thread anterior
        
        self.stop()  # Fecha a porta serial
        print("Tentando reconectar...")
        self._connect()
        
        if self.is_connected():
            self.running = True
            self.thread = threading.Thread(target=self._read_serial, daemon=True)
            self.thread.start()
    
    def write(self, data: Union[str, bytes]):
        """
        Escreve dados na porta serial.
        
        Args:
            data: Dados a serem escritos (string ou bytes)
            
        Returns:
            True se a escrita foi bem-sucedida, False caso contrário
        """
        if not self.is_connected():
            print("Não é possível escrever - porta não conectada")
            return False
        
        with self.write_lock:
            try:
                if isinstance(data, str):
                    data = data.encode('utf-8')
                self.serial_port.write(data)
                self.serial_port.flush()
                return True
            except serial.SerialException as e:
                print(f"Erro ao escrever na porta serial: {e}")
                self._reconnect()
                return False
    
    def has_data(self, reader_id: str) -> bool:
        """
        Verifica se há dados disponíveis para um leitor específico.
        Usa um bloqueio temporário para evitar race condition.
        """
        # Se outro leitor estiver ativo, retorna False imediatamente
        if self.reader_lock.locked() and self.current_reader != reader_id:
            return False
        
        # Caso contrário, verifica o buffer com lock (atomicamente)
        with self.reader_lock:
            return not SerialReaderWriter.buffer.empty()
    
    
    
    def read_data(self, reader_id: str) -> Optional[str]:
        """
        Lê dados do buffer para um leitor específico.
        
        Args:
            reader_id: Identificador do leitor
            
        Returns:
            Os dados lidos ou None se não houver dados disponíveis ou se outro leitor
            estiver com o acesso no momento.
        """
        # Se outro leitor estiver usando, retorna None
        if self.reader_lock.locked() and self.current_reader != reader_id:
            return None
        
        with self.reader_lock:
            self.current_reader = reader_id
            try:
                if not SerialReaderWriter.buffer.empty():
                    return SerialReaderWriter.buffer.get()
                return None
            finally:
                self.current_reader = None

# Exemplo de uso aprimorado
#if __name__ == "__main__":
    def test():
        # Configuração (substitua pela sua porta serial)
        PORT = 'COM3'
        BAUD_RATE = 9600
        
        # Cria e inicia o leitor/escritor serial
        serial_io = SerialReaderWriter(PORT, BAUD_RATE)
        
        # Verifica se está conectado antes de iniciar
        if serial_io.is_connected():
            serial_io.start()
            
            try:
                while True:
                    # Leitor 1 verifica e lê dados
                    if serial_io.has_data('leitor1'):
                        data = serial_io.read_data('leitor1')
                        if data:
                            print(f"Leitor 1 recebeu: {data}")
                            # Exemplo de escrita como resposta
                            serial_io.write(f"ACK {data}\n")
                    
                    # Leitor 2 verifica e lê dados
                    if serial_io.has_data('leitor2'):
                        data = serial_io.read_data('leitor2')
                        if data:
                            print(f"Leitor 2 recebeu: {data}")
                    
                    # Verifica periodicamente a conexão
                    if not serial_io.is_connected():
                        print("Conexão perdida, tentando recuperar...")
                        serial_io._reconnect()
                    
                    # Simula outros processamentos
                    threading.Event().wait(0.1)
                    
            except KeyboardInterrupt:
                print("\nEncerrando aplicação...")
                serial_io.stop()
        else:
            print(f"Não foi possível conectar à porta {PORT}")
