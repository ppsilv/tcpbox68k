#!/usr/bin/python3
import threading
import queue
import serial
from typing import Optional, Union

class SerialIO:
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 0.04):
        """
        Inicializa o leitor/escritor serial com uma porta específica.
        
        Args:
            port: Nome da porta serial (ex: 'COM3' ou '/dev/ttyUSB0')
            baudrate: Taxa de transmissão em bauds
            timeout: Timeout para operações de leitura
        """
        self.porta = "/dev/ttyUSB0"
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_port: Optional[serial.Serial] = None
        
        # Buffer de entrada (leitura)
        self.input_buffer = queue.Queue()
        
        # Buffer de saída (escrita)
        self.output_buffer = queue.Queue()
        
        # Controle de execução
        self.running = False
        
        # Threads
        self.read_thread = threading.Thread(target=self._read_serial, daemon=True)
        self.write_thread = threading.Thread(target=self._write_serial, daemon=True)
        
        # Locks
        self.reader_lock = threading.Lock()
        self.current_reader: Optional[str] = None
        
        # Inicializa a conexão serial
        self._connect()
    
    def _connect(self):
        """Estabelece a conexão serial."""
        try:
            self.serial_port = serial.Serial(
                port=self.porta,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.serial_port.reset_input_buffer()
            print(f"Conexão estabelecida com {self.porta}")
        except serial.SerialException as e:
            print(f"Falha ao conectar em {self.porta}: {e}")
            self.serial_port = None
    
    def start(self):
        """Inicia as threads de leitura e escrita serial."""
        if self.is_connected() and not self.running:
            self.running = True
            self.read_thread.start()
            self.write_thread.start()
            print("Threads de leitura e escrita iniciadas")
        else:
            print("Não foi possível iniciar - porta não conectada ou threads já em execução")
    
    def stop(self):
        """Para as threads e fecha a conexão."""
        self.running = False
        if self.read_thread.is_alive():
            self.read_thread.join()
        if self.write_thread.is_alive():
            self.write_thread.join()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        print("Threads paradas e conexão fechada")
    
    def is_connected(self) -> bool:
        """
        Verifica se a porta serial está conectada e aberta.
        
        Returns:
            True se a porta está conectada e aberta, False caso contrário
        """
        return self.serial_port is not None and self.serial_port.is_open
    
    def _read_serial(self):
        """Thread para leitura contínua da porta serial."""
        while self.running and self.is_connected():
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline().decode('utf-8').strip()
                    if data:
                        self.input_buffer.put(data)
            except (serial.SerialException, UnicodeDecodeError) as e:
                print(f"Erro na leitura serial: {e}")
                self._reconnect()
                continue
    
    def _write_serial(self):
        """Thread para escrita contínua na porta serial."""
        while self.running and self.is_connected():
            try:
                # Obtém dados do buffer de saída (com timeout para não bloquear indefinidamente)
                try:
                    data = self.output_buffer.get(timeout=0.1)
                    if isinstance(data, str):
                        data = data.encode('utf-8')
                    self.serial_port.write(data)
                    self.serial_port.flush()
                except queue.Empty:
                    continue
            except serial.SerialException as e:
                print(f"Erro na escrita serial: {e}")
                self._reconnect()
                continue
    
    def _reconnect(self):
        """Tenta reconectar à porta serial após falha."""
        self.stop()
        print("Tentando reconectar...")
        self._connect()
        if self.is_connected():
            self.start()
    
    def write(self, data: Union[str, bytes]):
        """
        Adiciona dados ao buffer de saída para serem escritos na porta serial.
        
        Args:
            data: Dados a serem escritos (string ou bytes)
            
        Returns:
            True se os dados foram adicionados ao buffer, False em caso de erro
        """
        if not self.is_connected():
            print("Aviso: dados adicionados ao buffer mas porta não está conectada")
        
        try:
            self.output_buffer.put(data)
            return True
        except Exception as e:
            print(f"Erro ao adicionar dados ao buffer de saída: {e}")
            return False
    
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
            return not self.input_buffer.empty()
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
                if not self.input_buffer.empty():
                    return self.input_buffer.get()
                return None
            finally:
                self.current_reader = None

    def non_blocking_input(self,prompt="", timeout=1):
        #print(prompt, end="", flush=True)
        
        # Verifica se há dados disponíveis no stdin
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        
        if ready:
            return sys.stdin.readline().rstrip("\n")
        else:
            return None  # Nenhum input disponível
import select
import sys
# Exemplo de uso
# Exemplo de uso
if __name__ == "__main__":
    # Configuração (substitua pela sua porta serial)
    PORT = '/dev/ttyUSB0'
    BAUD_RATE = 9600
    
    # Cria e inicia o leitor/escritor serial
    serial_io = SerialIO(PORT, BAUD_RATE)
    
    if serial_io.is_connected():
        tevedado=False
        serial_io.start()
        print("Digite um comando para enviar (ou 'sair' para terminar): ", flush=True)
        try:
            while True:
                user_input = serial_io.non_blocking_input(prompt="Digite um comando para enviar (ou 'sair' para terminar): ", timeout=0.05)
                if user_input is not None:
                    if user_input.lower() == "sair":
                       break
                    serial_io.write(user_input)
                    #print(f"Você digitou: {user_input}")
                else:
                    # Continua verificando se há dados recebidos
                    if serial_io.has_data('leitor1'):
                        data = serial_io.read_data('leitor1')
                        if data:
                            print(f"Dados recebidos: {data}")
                        tevedado = True    
                    else:
                        if tevedado == True:
                            print("Digite um comando para enviar (ou 'sair' para terminar): ", flush=True)
                            tevedado = False
 
                
                
                # Pequena pausa para evitar uso excessivo da CPU
                threading.Event().wait(0.1)
                
        except KeyboardInterrupt:
            print("\nEncerrando aplicação...")
        finally:
            serial_io.stop()
    else:
        print(f"Não foi possível conectar à porta {PORT}")


## Principais Alterações:
"""
1. **Thread de Escrita Dedicada**:
   - Adicionei uma thread separada (`_write_serial`) que fica responsável por monitorar o buffer de saída e escrever na porta serial
   - A thread usa um timeout pequeno no `get()` do buffer para não bloquear indefinidamente

2. **Buffer de Saída**:
   - Criei um buffer separado (`output_buffer`) apenas para dados de saída
   - O método `write()` agora apenas adiciona dados a este buffer
   - A thread de escrita cuida do processo real de envio para a porta serial

3. **Manutenção da Funcionalidade Existente**:
   - Todos os métodos de leitura (`has_data`, `read_data`) foram mantidos exatamente como estavam
   - O buffer de entrada (`input_buffer`) continua funcionando da mesma forma
   - O sistema de locks e controle de leitores permanece inalterado

4. **Vantagens da Nova Implementação**:
   - Escrita não-bloqueante (a aplicação principal não espera pela escrita serial)
   - Melhor desempenho em sistemas com muita escrita serial
   - Separação clara de responsabilidades entre leitura e escrita
   - Continuação do suporte a múltiplos leitores sem concorrência

## Como Usar a Nova Funcionalidade:

O uso permanece o mesmo para leitura. Para escrita, basta chamar:

```python
# Escrever string (será automaticamente convertida para bytes)
serial_io.write("COMANDO 1\n")

# Ou escrever bytes diretamente
serial_io.write(b"\x01\x02\x03")
```

A escrita agora é assíncrona - os dados são colocados no buffer de saída e a thread dedicada se encarrega de enviá-los quando possível.
"""
