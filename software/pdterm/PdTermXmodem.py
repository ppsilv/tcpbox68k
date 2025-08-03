#!/usr/bin/python3
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget
import os  # Adicione esta linha
import sys
import tty
import termios
import time
from PyQt6.QtCore import QObject, pyqtSignal
from PdTermFileHandler import FileHandler  # Importe sua classe

TOTAL_REENVIOS = 3

class XMODEM_Transfer(QObject):

    def __init__(self):
        self.serial_conectada = True  # Flag booleana inicialmente desligada
        self._handler = FileHandler(self.parent)  # parent_window é sua janela principal Qt
        super().__init__()
        self.cancelled = False
        self.chunk =0
        self.current_packet_number = 0
        self.checksum = 0
        self.total_reenvios = 0;
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


    def receive_byte_from_serial(self,text):
        print("xmodem initiated...");
        length = len(str(text))
        print(f"receive_byte_from_serial:Len text = {length}")
        textc = self.extract_number(text)
        print(f"receive_byte_from_serial:Dado [{textc}]")
        #hex_str = hex(textc)  # Retorna string no formato '0xff'
        #print(hex_str) 


    def verificar_conexao(self):
        if self.serial_conectada:
            print("✅ Serial está conectada.")
        else:
            print("❌ Serial NÃO está conectada.")

    def _send_xmodem_packet(self,chunk, packet_num):
        print(f"chunk:{chunck}   packet_num:{packet_num}");
        return True
        
    def _transmite_pacote(self):
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
        while True:
            chunk, packet_num = self.handler.get_next_chunk()
            if chunk is None:
                break            
            try:
                if send_xmodem_packet(chunk, packet_num):  # Sucesso
                    self.handler.commit_chunk()
                else:  # Falha
                    self.handler.reset_to_packet(packet_num)  # Repete o mesmo pacote
                time.sleep(5)    
            except Exception:
                self.handler.reset_to_packet(packet_num)

    def calculate_checksum(self, chunk):
        """
        Calcula o checksum simples (soma de bytes módulo 256) para um chunk de dados
        Args:
            chunk: bytes - Dados binários a serem verificados
        Returns:
            int - Valor do checksum (0-255)
        """
        if not isinstance(chunk, (bytes, bytearray)):
            raise TypeError("O chunk deve ser do tipo bytes ou bytearray")
    
        return sum(chunk) % 256                



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
        self.total_reenvios = 0;        

        ################################################################
        # 1. Carrega o arquivo
        if self._handler.load_file_to_buffer():
            print(f"Arquivo {self._handler.file_path} aberto com sucesso!")

            ################################################################
            # 2 - Aguarda receiver enviar 
            resposta = self.ask_user_yes_no("Aguardando receiver enviar NACK?")            
            if resposta:
                print("Recebeu NACK")
                # Faça algo se for Sim
            else:
               print("Recebeu ACK")
                    
            # Recebido o NACK começar transmissão           
            send_next_packet = True
            chunk_counter = 1
            while True:
                if send_next_packet:
                    chunk, packet_number = self._handler.get_next_chunk(128,True)
                
                if chunk is None:
                    print("\nFim do arquivo alcançado")
                    break

                #print("Enviando SOH")
                
                print(f"Enviando pacote {packet_number:02X}")
                pn = ~packet_number & 0xFF
                print(f"Enviando pacote complemento 2 {pn:02X}")
           
                cs = sum(chunk) % 256 
                print(f"Enviando Bloco {chunk_counter} ({len(chunk)} bytes packet_number:{packet_number} checksum:{cs}) ---")
                print(f"Enviando cs:{cs:02X}")
                
                # Pegar apenas os 5 primeiros bytes
                primeiros_5_bytes = chunk[:5]
                print("Primeiros 5 bytes:", ' '.join(f"{b:02X}" for b in primeiros_5_bytes))
                #for i, byte in enumerate(primeiros_5_bytes):
                #    print(f"Byte {i}: "
                #          f"Hex: {byte:02X} | "
                #          f"Dec: {byte:3d} | "
                #          f"Bin: {byte:08b} | "
                #          f"Char: {chr(byte) if 32 <= byte <= 126 else '.'}")
    
                ################################################################
                # 2 - Aguarda receiver enviar 
                resposta = self.ask_user_yes_no("Aguardando receiver enviar ACK ou NACK?")            
                if resposta:
                    print("Recebeu ACK pacote enviado com sucesso")
                    chunk_counter += 1
                    send_next_packet = True
                    total_reenvios = 1
                else:
                    print(f"Recebeu NACK renviar mesmo pacote{packet_number}")
                    send_next_packet = False
                    total_reenvios += 1
                    if total_reenvios == TOTAL_REENVIOS:
                        total_reenvios += 1
                        print("Excedido o total de reenvios do mesmo pacote abortando")
                        return
                        
    
            self._handler.close_file()
        else:
            print("Falha ao carregar arquivo")


        #self._transmite_pacote()
