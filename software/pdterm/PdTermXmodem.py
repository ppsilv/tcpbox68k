#!/usr/bin/python3
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget
import os  # Adicione esta linha
import time
from PyQt6.QtCore import QObject, pyqtSignal
from PdTermFileHandler import FileHandler  # Importe sua classe

class XMODEM_Transfer(QObject):

    def __init__(self):
        self.serial_conectada = True  # Flag booleana inicialmente desligada
        self._handler = FileHandler(self.parent)  # parent_window é sua janela principal Qt
        super().__init__()
        self.cancelled = False
        self.chunk =0
        self.current_packet_number = 0
        self.checksum = 0
        
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

    def get_next_chunk_with_checksum(self, chunk_size=128):
        """
        Lê o próximo chunk e calcula o checksum (soma simples de bytes)
        Retorna:
            tuple: (chunk_bytes, checksum) ou (None, 0) se fim do arquivo
        """
        chunk = self._handler.get_next_chunk(chunk_size)
        if chunk is None:
            return None, 0
        
        # Calcula checksum (soma de todos os bytes módulo 256)
        checksum = sum(chunk) % 256
        return chunk, checksum

    def _send_xmodem_packet(self,chunk, packet_num):
        print(f"chunk:{chunck}   packet_num:{packet_num}");
        return True
        
    def _transmite_pacote(self):
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
                

    def _send_file_xmodem(self):
        include_packet_number=True
        packet_number = 0
        #if self._handler.load_file_to_buffer():
        #    print(f"Arquivo {self._handler.file_path} carregado!")
        #    print(f"Tamanho do buffer: {len(self._handler.file_buffer)} bytes")
        #    print(f"Primeiros 100 caracteres:\n{self._handler.file_buffer[:100]}")
        #else:
        #    print("Operação cancelada ou falhou")
        #    return_ok

        ################################################################
        # 1. Carrega o arquivo
        if self._handler.load_file_to_buffer():
            print(f"Arquivo {self._handler.file_path} aberto com sucesso!")
            
            chunk_counter = 0
            while True:
                # Modo compatível (sem número do pacote)
                chunk, packet_number = self._handler.get_next_chunk(128,True)
                
                if chunk is None:
                    print("\nFim do arquivo alcançado")
                    break
           
                chunk_counter += 1
                print(f"\n--- Bloco {chunk_counter} ({len(chunk)} bytes packet_number{packet_number}) ---")
                
                #for i, byte in enumerate(chunk):
                #    print(f"Byte {i}: "
                #          f"Hex: {byte:02X} | "
                #          f"Dec: {byte:3d} | "
                #          f"Bin: {byte:08b} | "
                #          f"Char: {chr(byte) if 32 <= byte <= 126 else '.'}")
    
            self._handler.close_file()
        else:
            print("Falha ao carregar arquivo")

        ################################################################
        # 1. Calcula checksum do chunk
        self.chunk, self.checksum = self.get_next_chunk_with_checksum()
        #if chunk is not None:
        print(f"Chunk de {len(self.chunk)} bytes | Checksum: {self.checksum:02X}")

        #self._transmite_pacote()
