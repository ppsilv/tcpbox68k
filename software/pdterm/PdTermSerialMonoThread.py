import threading
from threading import  Thread,Lock
import serial
import queue
import serial.tools.list_ports
from typing import Optional
from typing import Optional, Union
import time


class SerialReadWrite:
    # Buffer de saída (escrita)
    output_buffer = queue.Queue()    
    # Buffer de entrada (leitura)
    input_buffer = queue.Queue()
    reconnection = False
    serial_port = None  # Variável privada
    port = None
    baud = None
    def __init__(self, terminal):
        """
        Inicializa o leitor/escritor serial com uma porta específica.
        
        Args:
            port: Nome da porta serial (ex: 'COM3' ou '/dev/ttyUSB0')
            baudrate: Taxa de transmissão em bauds
            timeout: Timeout para operações de leitura
        """
        self.terminal = terminal
        self.port = None
        #self._serial_port = None  # Variável privada
        
        # Controle de execução
        self.running = False
        
        # Threads
        self.read_thread           = threading.Thread(target=self._read_serial, daemon=True)
        self.write_thread          = threading.Thread(target=self._write_serial, daemon=True)
        self.write_terminal_thread = threading.Thread(target=self._write_terminal, daemon=True)
        
        # Locks
        self.reader_lock = threading.Lock()
        self.current_reader: Optional[str] = None
        
        # Inicializa a conexão serial
        #self._connect()
    
    def _connect(self, port: str="/dev/ttyUSB0", baudrate: int = 9600):
        try:
            print(f"_connect: {port} baudrate{baudrate}")
            SerialReadWrite.port = port
            SerialReadWrite.baud = baudrate
            if SerialReadWrite.reconnection:
                self.read_thread           = threading.Thread(target=self._read_serial, daemon=True)
                self.write_thread          = threading.Thread(target=self._write_serial, daemon=True)
                self.write_terminal_thread = threading.Thread(target=self._write_terminal, daemon=True)

            if SerialReadWrite.serial_port and SerialReadWrite.serial_port.is_open:
                SerialReadWrite.serial_port.close()
                
            SerialReadWrite.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=0.04
            )
            #self._serial_port.reset_input_buffer()
            if SerialReadWrite.serial_port and SerialReadWrite.serial_port.is_open:
                print(f"_connect:Conexão estabelecida. Porta: {SerialReadWrite.serial_port.port}, Status: {SerialReadWrite.serial_port.is_open}")
                reconnection = True
        except Exception as e:
            print(f"Falha crítica na conexão: {str(e)}")
            SerialReadWrite.serial_port = None
            raise  # Re-lança a exceção para tratamento externo

    def is_connected(self) -> bool:
        if SerialReadWrite.serial_port is not None and SerialReadWrite.serial_port.is_open:
            return True
        else:
            return False    
    
    def start(self):
        """Inicia as threads de leitura e escrita serial."""
        self.read_thread           = threading.Thread(target=self._read_serial, daemon=True)
        self.write_thread          = threading.Thread(target=self._write_serial, daemon=True)
        self.write_terminal_thread = threading.Thread(target=self._write_terminal, daemon=True)
        if self.running:
            print("start: threads já em execução")
            return
        if not self.running and SerialReadWrite.serial_port:
            self.running = True
            print("start: starting read thread")
            self.read_thread.start()
            print("start: starting write thread")
            self.write_thread.start()
            print("start: starting write terminal thread")
            self.write_terminal_thread.start()
            print("start: Threads de leitura e escrita iniciadas")
        else:
            if not SerialReadWrite.serial_port:
                print("start: porta não conectada")
                return
            print("start: ERRO: desconhecido");    
    
    def stop(self):
        """Para threads e conexão serial sem recursão"""
        if not hasattr(self, '_stopping'):
            self._stopping = True  # Flag para evitar recursão
            try:
                # 1. Sinaliza parada
                self.running = False
                
                time.sleep(1)
                
                # 2. Desbloqueia threads (se necessário)
                try:
                    self.output_buffer.put(None, block=False)
                except:
                    pass
                
                # 3. Para threads com timeout
                threads = []
                if hasattr(self, 'read_thread'):
                    threads.append(self.read_thread)
                if hasattr(self, 'write_thread'):
                    threads.append(self.write_thread)
                if hasattr(self, 'write_terminal_thread'):
                    threads.append(self.write_terminal_thread)
                    
                for t in threads:
                    if t and t.is_alive():
                        t.join(timeout=0.5)
                        if t.is_alive():
                            print(f"Aviso: Thread {t.name} não parou normalmente")
                
                # 4. Fecha porta serial (sem chamar stop() novamente)
                if hasattr(self, '_serial_port') and SerialReadWrite.serial_port:
                    try:
                        SerialReadWrite.serial_port.close()
                        SerialReadWrite.serial_port = None
                    except Exception as e:
                        print(f"Erro ao fechar porta: {e}")
                    finally:
                        SerialReadWrite.serial_port = None
                
                # 5. Limpa referências
                self.read_thread = None
                self.write_thread = None
                self.write_terminal_thread = None
                
            finally:
                del self._stopping  # Remove o flag após conclusão
      
    
    def _read_serial(self):
        """Thread para leitura contínua da porta serial."""
        while self.running and self.is_connected():
            try:
                if SerialReadWrite.serial_port.in_waiting > 0:
                    data = SerialReadWrite.serial_port.readline().decode('utf-8').strip()
                    if data:
                        SerialReadWrite.input_buffer.put(data)     
            except (serial.SerialException, UnicodeDecodeError) as e:
                print(f"Erro na leitura serial: {e}")
                self._reconnect()
                continue
        print("Thread read serial encerrada...");
    def _write_serial(self):
        """Thread para escrita contínua na porta serial."""
        current_port = SerialReadWrite.serial_port
        while self.running: # and self.is_connected():
            try:
                try:
                    #print(f"\n[DEBUG] Tamanho do buffer: {self.output_buffer.qsize()}")  
                    #print(f"Lendo do buffer (ID: {id(SerialReadWrite.output_buffer)})")
                    #if current_port and current_port.is_open:
                    #    print("_write_serial: SerialReadWrite.serial_port conectada")
                    #else:
                    #    print("_write_serial: SerialReadWrite.serial_port Desconectada")
                    data="VAZIO"   
                    data = SerialReadWrite.output_buffer.get(timeout=0.1)
                    if isinstance(data, str):
                        data = data.encode('utf-8')
                        print(f"_write_serial: Thread  data to send{data}")    
                    else:
                        print("_write_serial: Thread No data to send") 
                        continue   
                    current_port.write(data)
                    current_port.flush()
                except queue.Empty:
                    #print("DEBUG: Buffer vazio (comportamento esperado)")
                    continue
            except serial.SerialException as e:
                print(f"Erro na escrita serial: {e}")
                self._reconnect()
                continue
        print("Thread write serial encerrada...");

    def _write_terminal(self):
        """Thread para escrita contínua no terminal."""
        while self.running and self.is_connected():
            try:
                # Obtém dados do buffer de saída (com timeout para não bloquear indefinidamente)
                try:
                    if self.has_data('leitor1'):
                        data = self.read_data('leitor1')
                        data = data.encode('utf-8')
                        if data:
                            print(f"Dados recebidos: {data}")
                except queue.Empty:
                    continue
            except serial.SerialException as e:
                print(f"Erro na escrita no terminal: {e}")
                continue
        print("Thread write terminal encerrada...");

    
    def _reconnect(self):
        """Tenta reconectar à porta serial após falha."""
        self.stop()
        print("Tentando reconectar...")
        self._connect()
        if self.is_connected():
            self.start()
    
    def write(self, data: Union[str, bytes]):
        #print("Pondo dados no buffer de saida: output_buffer");
        #print(f"Lendo do buffer (ID: {id(SerialReadWrite.output_buffer)})")
        SerialReadWrite.output_buffer.put(data)
        return True
    
    # Métodos de leitura (mantidos exatamente como estavam)
    def has_data(self, reader_id: str) -> bool:
        """
        Verifica se há dados disponíveis para um leitor específico.
        
        Args:
            reader_id: Identificador do leitor (ex: 'leitor1' ou 'leitor2')
            
        Returns:
            True se houver dados disponíveis para o leitor especificado
        """
        if not self.reader_lock.locked() or self.current_reader == reader_id:
            return not SerialReadWrite.input_buffer.empty()
        return False
    
    def read_data(self, reader_id: str) -> Optional[str]:
        """
        Lê dados do buffer para um leitor específico.
        
        Args:
            reader_id: Identificador do leitor
            
        Returns:
            Os dados lidos ou None se não houver dados disponíveis ou se outro leitor
            estiver com o acesso no momento.
        """
        if self.reader_lock.locked() and self.current_reader != reader_id:
            return None
        
        with self.reader_lock:
            self.current_reader = reader_id
            try:
                if not SerialReadWrite.input_buffer.empty():
                    return SerialReadWrite.input_buffer.get()
                return None
            finally:
                self.current_reader = None

    def non_blocking_input(self,prompt="", timeout=1):
      
        # Verifica se há dados disponíveis no stdin
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        
        if ready:
            return sys.stdin.readline().rstrip("\n")
        else:
            return None  # Nenhum input disponível
            
    def _disconnect_serial(self, silent=True):
        """Desconecta a porta serial. Se silent=True, não mostra mensagem."""
        if SerialReadWrite.serial_port:
            try:
                self.stop()
                if not silent:
                    print("_disconnect_serial: Quem esta fazendo isso?????")
            except Exception as e:
                self.terminal.write_terminal(f"\n[ERRO] Falha ao desconectar: {str(e)}\n")
                return False
            finally:
                if not silent:
                    print("_disconnect_serial: Quem esta fazendo isso?????")
                SerialReadWrite.serial_port = None
                return True

    def reset_input_buffer(self):
        SerialReadWrite.serial_port.reset_input_buffer()

 
