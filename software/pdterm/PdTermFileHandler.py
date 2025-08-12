from PyQt6.QtWidgets import QApplication,QFileDialog, QMessageBox,QWidget

class FileHandler:
    def __init__(self, parent=None):
        self.parent = parent  # Opcional: referência para a janela principal
        self.file_buffer = None  # Buffer para armazenar o conteúdo
        self.file_path = ""  # Caminho do arquivo selecionado
        self.current_position = 0  # Para controle dos chunks
        self.current_packet_number = 1  # Contador de pacotes XMODEM

    def load_file_to_buffer(self):
        """Abre diálogo de arquivo, lê o conteúdo e armazena no buffer"""
        effective_parent = self.parent if isinstance(self.parent, QWidget) else QApplication.activeWindow()

        # 1. Abre o diálogo para seleção de arquivo
        file_path, _ = QFileDialog.getOpenFileName(
            effective_parent,
            "Selecione o Arquivo",  # Título
            "",  # Diretório inicial (vazio = diretório atual)
            "Todos os Arquivos (*);;Arquivos de Texto (*.txt)"  # Filtros
        )

        if not file_path:  # Usuário cancelou
            return False

        # 2. Tenta ler o arquivo
        try:
            with open(file_path, 'rb') as file:
                self.file_buffer = file.read()  # Lê todo o conteúdo
                self.file_path = file_path
                self.current_position = 0  # Reseta a posição
            return True

        except Exception as e:
            # 3. Mostra erro se ocorrer
            QMessageBox.critical(
                self.parent,
                "Erro",
                f"Não foi possível ler o arquivo:\n{str(e)}"
            )
            return False
#DEPRECADA EM 02/08/2025 19:54
#    def get_next_chunk(self, chunk_size=128):
#        """Retorna o próximo chunk do buffer já carregado"""
#        if self.file_buffer is None:
#            raise ValueError("Nenhum arquivo carregado. Chame load_file_to_buffer() primeiro.")
#        
#        if self.current_position >= len(self.file_buffer):
#            return None  # Fim do arquivo
#            
#        chunk = self.file_buffer[self.current_position:self.current_position + chunk_size]
#        self.current_position += len(chunk)
#        return chunk
    
    def reset_position(self):
        """Reinicia a leitura do buffer desde o início"""
        self.current_position = 0

    def close_file(self):
        """Fecha o arquivo de forma segura"""
        if hasattr(self, 'file_handle') and self.file_handle and not self.file_handle.closed:
            self.file_handle.close()
        self.file_handle = None
        self.current_position = 0

    def __del__(self):
        """Destrutor - garante que o arquivo será fechado"""
        self.close_file()
    
    def reset_current_packet_number(self):
        self.current_packet_number = 1

    def get_next_chunk(self, chunk_size=128, include_packet_number=False, include_checksum=False):
        """
        Formas de chamar
        chunk = handler.get_next_chunk(128)
        chunk, pkt_num = handler.get_next_chunk(128, include_packet_number=True)
        chunk, pkt_num, checksum = handler.get_next_chunk(128, include_packet_number=True, include_checksum=True)
        
        Retorna o próximo chunk do buffer com opções adicionais
        Args:
            chunk_size: tamanho do bloco (padrão: 128 bytes)
            include_packet_number: se True, inclui o número do pacote
            include_checksum: se True, calcula checksum do chunk
        Returns:
            Dependendo dos parâmetros:
            - chunk (bytes)
            - (chunk, packet_number) 
            - (chunk, packet_number, checksum)
            - (chunk, checksum)
            Retorna None ou (None, None) ou (None, None, None) quando acabar
        """
        if self.file_buffer is None:
            raise ValueError("Nenhum arquivo carregado. Chame load_file_to_buffer() primeiro.")
        
        if self.current_position >= len(self.file_buffer):
            if include_packet_number and include_checksum:
                return (None, None, None)
            elif include_packet_number or include_checksum:
                return (None, None)
            return None
            
        chunk = self.file_buffer[self.current_position:self.current_position + chunk_size]
        result = [chunk]
        
        if include_packet_number:
            result.append(self.current_packet_number)
        
        if include_checksum:
            checksum = self._calculate_checksum(chunk)
            result.append(checksum)
        
        self.current_position += len(chunk)
        self.current_packet_number += 1
        
        return tuple(result) if len(result) > 1 else chunk

    def _calculate_checksum(self, data):
        """Calcula checksum simples (soma de bytes modulo 256)"""
        if not data:
            return 0
        return sum(data) % 256

    
#DEPRECADA        
#    def get_next_chunk(self, chunk_size=128, include_packet_number=False):
#        """
#        Retorna o próximo chunk do buffer
#        Args:
#            chunk_size: tamanho do bloco (padrão: 128 bytes)
#            include_packet_number: se True, retorna também o número do pacote
#        Returns:
#            Se include_packet_number=False: bytes ou None
#            Se include_packet_number=True: tuple (bytes, int) ou (None, None)
#        """
#        if self.file_buffer is None:
#            raise ValueError("Nenhum arquivo carregado. Chame load_file_to_buffer() primeiro.")
#        
#        if self.current_position >= len(self.file_buffer):
#            return (None, None) if include_packet_number else None
#            
#        chunk = self.file_buffer[self.current_position:self.current_position + chunk_size]
#        
#        if include_packet_number:
#            result = (chunk, self.current_packet_number)
#        else:
#            result = chunk
#            
#        self.current_position += len(chunk)
#        self.current_packet_number += 1
#        return result
        
    #DEPRECADAS
    #def commit_chunk(self):
    #    """Confirma o envio bem-sucedido, avançando para o próximo chunk"""
    #    self.current_position += 128
    #    self.current_packet_number += 1
    #
    #def reset_to_packet(self, packet_number):
    #    """Reinicia a posição para um pacote específico (retry)"""
    #    self.current_position = (packet_number - 1) * 128
    #    self.current_packet_number = packet_number    
