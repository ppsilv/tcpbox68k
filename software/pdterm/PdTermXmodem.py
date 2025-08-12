#!/usr/bin/python3
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget
import os  # Adicione esta linha
import sys
import tty
import termios
import time
from PyQt6.QtCore import QObject, pyqtSignal
from PdTermFileHandler import FileHandler  # Importe sua classe
from PdTermSerial import PdSerial

TOTAL_REENVIOS = 3

class XMODEM_Transfer(QObject):

    def __init__(self, parent, pdserial):
        self.parent = parent
        self.serial = pdserial
        self.serial_conectada = False  # Flag booleana inicialmente desligada
        self._handler = FileHandler(self.parent)  # parent_window é sua janela principal Qt
        super().__init__()
        self.cancelled = False
        self.chunk =0
        self.current_packet_number = 0
        self.checksum = 0
        self.total_reenvios = 1;
        
        # Máquina de estados
        #self.state = 'IDLE'  # Estados possíveis: IDLE, WAIT_NAK, SEND_BLOCK, WAIT_ACK, WAIT_EOT_ACK
        #self.current_block = 0
        #self.retry_count = 0
        #self.total_blocks = 0
        #self.current_block_data = None

        # Constantes XMODEM
        self.SOH = 0x01
        self.EOT = 0x04
        self.ACK = 0x06
        self.NAK = 0x15
        self.CAN = 0x18
        self.timeout = 50
        self.retries = 10
        self.buffer = bytearray()  # Buffer para armazenar dados

    def append_data(self, data: bytes):
        """Adiciona dados ao buffer."""
        self.buffer.extend(data)

    def read_data(self, size: int) -> bytes:
        """Lê 'size' bytes do buffer (e os remove)."""
        chunk = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return bytes(chunk)

    def extract_number(self, text):
        """
        Extrai o valor HEX após '[-' em strings como "$41,'[-',$31,13,10,0"
        Retorna como inteiro (ou 0 se falhar)
        """
        try:
            #DEBUG#DEBUG#DEBUG#DEBUG#DEBUG#DEBUG#DEBUG#DEBUG#DEBUG#DEBUG#
            """
            print("extract_number:")
            print("--------------------------------------------")
            for i in range(len(text)):
                print(text[i])
            print("--------------------------------------------")
            for caractere in text:
                print(f"'{caractere}' -> {hex(ord(caractere))}")
            print("--------------------------------------------")
            length = len(str(text))
            print(F"extract_number:Len text = {length}")
            print("extract_number: text= "+text)
            """
            #DEBUG#DEBUG#DEBUG#DEBUG#DEBUG#DEBUG#DEBUG#DEBUG#DEBUG#DEBUG#
            
            pos=text.find("[-")+2
            """#DEBUG print(f"extract_number: pos= {pos}")"""
            caractere = text[pos]
            """#DEBUG print("extract_number: char = "+caractere)"""
            return caractere
            
        except (ValueError, IndexError) as e:
            print(f"[ERRO] Falha ao extrair valor: {e}")
            return 0


    def verificar_conexao(self):
        if self.serial_conectada:
            print("✅ Serial está conectada.")
        else:
            print("❌ Serial NÃO está conectada.")


        

        #0. The sender says it is ready to transmit
        #   wait for receiver start 
        #1. The receiver start a transmission sending $15
        #2. Packet Transmission:
        #   The sender responds with a packet containing:
        #   A Start of Header (SOH) character. 
        #   A block number (and its one's complement for error checking). 
        #   128 bytes of data (or less for the last packet). 
        #   An 8-bit checksum or CRC.
        #3. Receiver answer with ACK no NACK
        #4. If sender receive ACK send next packet
        #5. If sender receive NACK send the same packet
        #   but this happens just for X times
        #6. When sender sent all packets it send EOT          
           



    def ask_user_yes_no(self, question):
        """Pergunta ao usuário Sim/Não e retorna True para Sim, False para Não"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)  # Corrigido aqui
        msg_box.setWindowTitle("Confirmação")
        msg_box.setText(question)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        reply = msg_box.exec()
        return reply == QMessageBox.StandardButton.Yes


    def _send_file_xmodem(self):
        include_packet_number=True
        mf=True

        total_reenvios = 0
        self.chunk =0
        self._handler.reset_current_packet_number()
        self.checksum = 0
        self.total_reenvios = 1;        

        #Set flag
        self.serial.stop_thread_write_terminal()

        ################################################################
        # 1. Carrega o arquivo
        if self._handler.load_file_to_buffer():
            print(f"Arquivo {self._handler.file_path} aberto com sucesso!")

            ################################################################
            # 2 - Aguarda receiver enviar 
            resposta = self.ask_user_yes_no("Aguardando receiver enviar NACK?")            
            if resposta:
                print("Recebeu NACK do dialogo")
                # Faça algo se for Sim
            else:
               print("Recebeu ACK")
            self.serial.write_to_serial('3')
            
            print("Lendo primeira")
            byte = self.serial.read_serial_input_buffer()
            while byte == None:
                byte = self.serial.read_serial_input_buffer()
                time.sleep(1)
                if byte != None:
                    print(f"Recebido Oque?: {byte.encode('utf-8')}")
            
            byte_as_bytes = byte.encode('latin1')  # latin1 preserva os bytes 0-255

            if byte_as_bytes == b'\x15':
                print("É um NACK")
            else:
                print("[ERRO] Terminando Xmodem com erro: Não veio NACK inicial")
                self.serial.start_thread_write_terminal()
                self._handler.close_file()
                return

            # Recebido o NACK começar transmissão           
            send_next_packet = True
            chunk_counter = 1
            while True:
                if send_next_packet:
                    #chunk, packet_number = self._handler.get_next_chunk(128,True)
                    chunk, packet_number, checksum = self._handler.get_next_chunk(128, include_packet_number=True, include_checksum=True)
                
                if chunk is None:
                    print("\nFim do arquivo alcançado")
                    break

                print(f"pacote numero {packet_number}");
                #Escrevendo na serial
                resposta = self.ask_user_yes_no("Enviar soh")  
                print(f"Enviando: {self.SOH:02X}")   
                self.serial.write_to_serial(self.SOH)
                resposta = self.ask_user_yes_no("Enviar packet_number")     


                print(f"Enviando: {packet_number:02X}")   
                self.serial.write_to_serial(packet_number)

                pn = ~packet_number & 0xFF
                resposta = self.serial._send_to_serial("Enviar ~packet_number")     
                self.serial.write_to_serial(pn)
                resposta = self.ask_user_yes_no("Enviar chunk")     
                self.serial.write_to_serial(chunk)
                resposta = self.ask_user_yes_no("Enviar checksum")     
                self.serial.write_to_serial(checksum)
                resposta = self.ask_user_yes_no("Aguardando receiver enviar ACK?")     
 
                print("Pacote enviado, aguardando ACK")
                byte = self.serial.read_serial_input_buffer()
                while byte == None:
                    byte = self.serial.read_serial_input_buffer()
                    time.sleep(1)
                    if byte != None:
                        print(f"Recebido Oque?: {byte.encode('utf-8')}")

                byte_as_bytes = byte.encode('latin1')  # latin1 preserva os bytes 0-255
    
                if byte_as_bytes == b'\x15':
                    print("É um NACK")
                else:
                    print("[ERRO] Terminando Xmodem com erro: Não veio NACK de pacote")
                    self.serial.start_thread_write_terminal()
                    self._handler.close_file()
                    return

                #print("Enviando SOH")
                print(f"{self.SOH:02X}", end='')
                #print(f"Enviando pacote {packet_number:02X}")
                print(f"{packet_number:02X}", end='')
                pn = ~packet_number & 0xFF
                print(f"{pn:02X}", end='')
           
                print(f"Enviando Bloco {chunk_counter} ({len(chunk)} bytes packet_number:{packet_number} checksum:{cs}) ---")
                
                # Pegar apenas os 5 primeiros bytes
                primeiros_5_bytes = chunk[:5]
                #print("Primeiros 5 bytes:", ' '.join(f"{b:02X}" for b in primeiros_5_bytes))
                print( ''.join(f"{b:02X}" for b in primeiros_5_bytes), end='' )
                
                #for i, byte in enumerate(primeiros_5_bytes):
                #    print(f"Byte {i}: "
                #          f"Hex: {byte:02X} | "
                #          f"Dec: {byte:3d} | "
                #          f"Bin: {byte:08b} | "
                #          f"Char: {chr(byte) if 32 <= byte <= 126 else '.'}")
    
                ################################################################

                cs = sum(chunk) % 256 
                print(f"{cs:02X} ->", end='', flush=True)        
            
                # 2 - Aguarda receiver enviar 
                resposta = self.ask_user_yes_no("Aguardando receiver enviar ACK ou NACK?")            
                if resposta:
                    print("Recebeu ACK pacote enviado com sucesso")
                    chunk_counter += 1
                    send_next_packet = True
                    self.total_reenvios = 1
                else:
                    print(f"Recebeu NACK renviar mesmo pacote{packet_number}")
                    send_next_packet = False
                    if self.total_reenvios == TOTAL_REENVIOS:
                        self.total_reenvios = 1
                        print("[ERRO] Excedido o total de reenvios do mesmo pacote abortando")
                        self.serial.start_thread_write_terminal()
                        self._handler.close_file()
                        return
                    self.total_reenvios += 1
            #Fim do while de transmissão
            print("[INFO] Terminando Xmodem com sucesso")
            self.serial.start_thread_write_terminal()
            self._handler.close_file()
        else:
            print("Falha ao carregar arquivo")


        #self._transmite_pacote()

    def _bytes_to_hex(self, data):
        """Converte bytes para string hexadecimal formatada"""
        return ' '.join(f'{b:02X}' for b in data)  
        
