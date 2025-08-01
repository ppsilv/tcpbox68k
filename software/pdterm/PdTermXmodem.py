#!/usr/bin/python3
import os  # Adicione esta linha
import time
from PyQt6.QtCore import QObject, pyqtSignal


class XMODEM_Transfer(QObject):
    # Sinais para comunicação com a interface
    progress_updated = pyqtSignal(int, str)  # porcentagem, mensagem
    transfer_complete = pyqtSignal(bool, str)  # sucesso, mensagem
    data_to_send = pyqtSignal(bytes)  # Dados a serem enviados pela serial

    def __init__(self, serial_handler, terminal):
        super().__init__()
        self.serial = serial_handler  # Referência ao handler serial do PDTermPro
        self.terminal = terminal      # Referência ao terminal
        self.cancelled = False
        self.transfer_in_progress = False

        # Máquina de estados
        self.state = 'IDLE'  # Estados possíveis: IDLE, WAIT_NAK, SEND_BLOCK, WAIT_ACK, WAIT_EOT_ACK
        self.current_block = 0
        self.retry_count = 0
        self.total_blocks = 0
        self.current_block_data = None

        # Constantes XMODEM
        self.SOH = 0x01
        self.EOT = 0x04
        self.ACK = 0x06
        self.NAK = 0x15
        self.CAN = 0x18
        self.timeout = 50
        self.retries = 10

    def _write_serial(self, data):
        """Envia dados através do sistema existente"""
        try:
            # Converte bytearray para bytes se necessário
            if isinstance(data, bytearray):
                data = bytes(data)
            
            # Verifica se é realmente do tipo bytes
            if not isinstance(data, bytes):
                raise TypeError(f"Dados devem ser bytes ou bytearray, recebido {type(data)}")
            
            self.data_to_send.emit(data)
            self.terminal.write_terminal(f"[XMODEM] TX: {self._hexdump(data)}\n")
        except Exception as e:
            self.terminal.write_terminal(f"\n[ERRO XMODEM] Falha ao enviar dados: {str(e)}\n")
            raise

    #def _read_serial(self, size=1, timeout=5):
    #    """Lê dados usando a serial do PDTermPro"""
    #    start_time = time.time()
    #    while time.time() - start_time < timeout:
    #        if self.serial.in_waiting >= size:
    #            data = self.serial.read(size)
    #            self.terminal.write_terminal(f"[XMODEM] RX: {self._hexdump(data)}\n")
    #            return data
    #        time.sleep(0.1)
    #    return None

    def _hexdump(self, data):
        """Formata dados para exibição no terminal"""
        return " ".join(f"{b:02X}" for b in data)

    def _wait_for(self, expected, description=""):
        """Espera por um byte específico com timeout"""
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            response = self._read_serial()
            if response:
                byte = response[0]
                if byte == expected:
                    return True
                elif byte == self.CAN:
                    raise Exception("Transferência cancelada pelo receptor")
        raise TimeoutError(f"Timeout esperando por {description}")

    def send_fileOLD(self, filename):
        """Envia um arquivo via XMODEM"""
        try:
            self.cancelled = False
            file_size = os.path.getsize(filename)
            self.progress_updated.emit(0, f"Iniciando XMODEM - {file_size} bytes")

            # 1. Espera pelo NAK inicial
            self.terminal.write_terminal("\n[XMODEM] Esperando NAK inicial...\n")
            if not self._wait_for(self.NAK, "NAK inicial"):
                raise Exception("Protocolo não iniciado")

            # 2. Envia o arquivo em blocos de 128 bytes
            block_num = 1
            with open(filename, 'rb') as file:
                while not self.cancelled:
                    data = file.read(128)
                    if not data:
                        break

                    # Preenche com CTRL-Z se necessário
                    if len(data) < 128:
                        data += bytes([26] * (128 - len(data)))

                    # Envia bloco
                    self._send_block(block_num, data)
                    block_num += 1

                    # Atualiza progresso
                    progress = min(100, int(file.tell() * 100 / file_size))
                    self.progress_updated.emit(progress, f"Enviando bloco {block_num}")

            # 3. Finaliza com EOT
            self.terminal.write_terminal("\n[XMODEM] Enviando EOT...\n")
            self._write_serial(bytes([self.EOT]))
            self._wait_for(self.ACK, "ACK final")

            self.transfer_complete.emit(True, "Transferência concluída com sucesso!")
            self.terminal.write_terminal("\n[XMODEM] Transferência completa!\n")

        except Exception as e:
            self.transfer_complete.emit(False, str(e))
            self.terminal.write_terminal(f"\n[XMODEM] ERRO: {str(e)}\n")
    
    def send_file(self, filename):
        """Inicia a transferência de arquivo via XMODEM"""
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Arquivo não encontrado: {filename}")
            
            self.file = open(filename, 'rb')
            file_size = os.path.getsize(filename)
            self.total_blocks = (file_size + 127) // 128  # Arredonda para cima
            
            self.transfer_in_progress = True
            self.cancelled = False
            self.state = 'WAIT_NAK'
            self.current_block = 1
            self.retry_count = 0
            
            self.progress_updated.emit(0, f"Iniciando XMODEM - {file_size} bytes")
            self.terminal.write_terminal("\n[XMODEM] Aguardando NAK inicial...")
            
            # Envia NAK inicial para solicitar início (algumas implementações precisam disso)
            self._write_serial(bytes([self.NAK]))
            
        except Exception as e:
            self.transfer_complete.emit(False, str(e))
            self.terminal.write_terminal(f"\n[XMODEM] ERRO: {str(e)}\n")
            if hasattr(self, 'file'):
                self.file.close()
            self.transfer_in_progress = False
    
    def _send_block(self, block_num, data):
        """Envia um único bloco XMODEM"""
        packet = bytearray()
        packet.append(self.SOH)
        packet.append(block_num % 256)
        packet.append(255 - (block_num % 256))
        packet.extend(data)
        packet.append(self._calc_checksum(data))

        for attempt in range(self.retries):
            self._write_serial(packet)
            
            response = self._read_serial(timeout=10)
            if not response:
                continue

            if response[0] == self.ACK:
                return
            elif response[0] == self.NAK:
                continue

        raise Exception("Falha após várias tentativas")

    def _calc_checksum(self, data):
        """Calcula checksum simples (XMODEM padrão)"""
        return sum(data) & 0xFF

    def cancel_transfer(self):
        """Cancela a transferência em andamento"""
        self.cancelled = True
        self._write_serial(bytes([self.CAN, self.CAN]))
        self.terminal.write_terminal("\n[XMODEM] Transferência cancelada\n")
    
    def handle_received_data(self, data):
        """Processa dados recebidos durante transferência XMODEM"""
        if not self.transfer_in_progress:
            return
        
        # Buffer para acumular bytes recebidos
        for byte in data:
            self._process_xmodem_byte(byte)
    
    def _process_xmodem_byte(self, byte):
        """Máquina de estados do protocolo XMODEM"""
        byte = ord(byte) if isinstance(byte, str) else byte  # Garante que é numérico
        
        if self.state == 'WAIT_NAK':
            if byte == self.NAK:
                self.terminal.write_terminal("\n[XMODEM] NAK recebido - iniciando transferência\n")
                self.state = 'SEND_BLOCK'
                self.current_block = 1
                self._send_next_block()
            elif byte == self.CAN:
                self._abort_transfer("Transferência cancelada pelo receptor")
        
        elif self.state == 'WAIT_ACK':
            if byte == self.ACK:
                self.terminal.write_terminal(f"\n[XMODEM] Bloco {self.current_block} confirmado\n")
                self.current_block += 1
                self.state = 'SEND_BLOCK'
                self._send_next_block()
            elif byte == self.NAK:
                self.retry_count += 1
                if self.retry_count >= self.retries:
                    self._abort_transfer("Número máximo de tentativas excedido")
                else:
                    self.terminal.write_terminal(f"\n[XMODEM] Retransmitindo bloco {self.current_block} (tentativa {self.retry_count})\n")
                    self._send_current_block()
            elif byte == self.CAN:
                self._abort_transfer("Transferência cancelada pelo receptor")
        
        elif self.state == 'WAIT_EOT_ACK':
            if byte == self.ACK:
                self.terminal.write_terminal("\n[XMODEM] Transferência concluída com sucesso!\n")
                self.transfer_complete.emit(True, "Transferência completa")
                self._cleanup()
            else:
                self._abort_transfer("Resposta inválida após EOT")
    
    def _send_next_block(self):
        """Prepara e envia o próximo bloco de dados"""
        if self.current_block > self.total_blocks:
            self._send_eot()
            return
        
        try:
            data = self.file.read(128)
            if not data:
                self._send_eot()
                return
            
            # Preenche com CTRL-Z se necessário
            if len(data) < 128:
                data += bytes([26] * (128 - len(data)))
            
            self.current_block_data = data
            self._send_current_block()
        
        except Exception as e:
            self._abort_transfer(f"Erro ao ler arquivo: {str(e)}")

    def _send_current_block(self):
        """Envia o bloco atual"""
        try:
            packet = bytearray()
            packet.append(self.SOH)
            packet.append(self.current_block % 256)
            packet.append(255 - (self.current_block % 256))
            packet.extend(self.current_block_data)
            packet.append(self._calc_checksum(self.current_block_data))
            
            self._write_serial(bytes(packet))  # Convertemos explicitamente para bytes aqui
            self.state = 'WAIT_ACK'
            self.retry_count = 0
            
            # Atualiza progresso
            progress = min(100, int(self.current_block * 100 / self.total_blocks))
            self.progress_updated.emit(progress, f"Enviando bloco {self.current_block}")
        except Exception as e:
            self._abort_transfer(f"Erro ao enviar bloco {self.current_block}: {str(e)}")
    
    def _send_eot(self):
        """Envia sinal de fim de transmissão"""
        try:
            self.terminal.write_terminal("\n[XMODEM] Enviando EOT...\n")
            self._write_serial(bytes([self.EOT]))  # Note o uso de bytes() aqui
            self.state = 'WAIT_EOT_ACK'
        except Exception as e:
            self._abort_transfer(f"Erro ao enviar EOT: {str(e)}")
    
    def _abort_transfer(self, message):
        """Cancela a transferência com mensagem de erro"""
        try:
            self.terminal.write_terminal(f"\n[XMODEM] ERRO: {message}\n")
            self._write_serial(bytes([self.CAN, self.CAN]))  # Convertido para bytes
            self.transfer_complete.emit(False, message)
            self._cleanup()
        except Exception as e:
            self.terminal.write_terminal(f"\n[ERRO CRÍTICO] Falha ao abortar: {str(e)}\n")
            self._cleanup()



    def _send_current_block1(self):
        """Envia o bloco atual"""
        packet = bytearray()
        packet.append(self.SOH)
        packet.append(self.current_block % 256)
        packet.append(255 - (self.current_block % 256))
        packet.extend(self.current_block_data)
        packet.append(self._calc_checksum(self.current_block_data))
        
        self._write_serial(packet)
        self.state = 'WAIT_ACK'
        self.retry_count = 0
        
        # Atualiza progresso
        progress = min(100, int(self.current_block * 100 / self.total_blocks))
        self.progress_updated.emit(progress, f"Enviando bloco {self.current_block}")
    
    def _send_eot1(self):
        """Envia sinal de fim de transmissão"""
        self.terminal.write_terminal("\n[XMODEM] Enviando EOT...\n")
        self._write_serial(bytes([self.EOT]))
        self.state = 'WAIT_EOT_ACK'
    
    def _abort_transfer1(self, message):
        """Cancela a transferência com mensagem de erro"""
        self.terminal.write_terminal(f"\n[XMODEM] ERRO: {message}\n")
        self._write_serial(bytes([self.CAN, self.CAN]))
        self.transfer_complete.emit(False, message)
        self._cleanup()
    
    def _cleanup(self):
        """Limpeza após transferência"""
        self.transfer_in_progress = False
        self.state = 'IDLE'
        if hasattr(self, 'file'):
            self.file.close()
    ## Integração com o PDTermPro existente
    #if __name__ == "__main__":
    #    # Exemplo de uso (teste)
    #    ser = serial.Serial('/dev/ttyUSB0', 9600)
    #    terminal = TerminalWidget()
    #    xmodem = XMODEM_Transfer(ser, terminal)
    #    xmodem.send_file('teste.bin')