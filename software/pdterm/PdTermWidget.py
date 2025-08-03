#!/usr/bin/python3
#from PyQt6.QtWidgets import (QMainWindow, QApplication, QPlainTextEdit, QVBoxLayout, 
#                            QWidget, QToolBar, QStatusBar, QFileDialog, QLabel, QMenu)
from PyQt6.QtWidgets import (QPlainTextEdit)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor, QColor, QFont
from PyQt6.QtGui import QPainter, QColor  # Adicione esta importação
from PyQt6.QtCore import QTimer
from AnsiProcessor import AnsiProcessor
from PyQt6.QtGui import QFont, QFontMetrics  # Adicione esta importação
from PyQt6.QtGui import QTextOption  # Importação adicionada
from PdTermXmodem import XMODEM_Transfer

from PdTermMenu import PdTermMenu


class TerminalWidget(QPlainTextEdit):
    data_to_send = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_key_was_enter = False  
        self.transfer_in_progress = False
        # Configura fonte monoespaçada
        #font = QFont("Courier New", 12)  # Ou outra fonte monospace
        font = QFont()
        font.setFamily("Courier New")  # Fonte monoespaçada clássica
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)  # Garante monoespaçamento
        font.setPointSize(12)
        self.setFont(font)
        self.setFixedSize(800, 600)  # Ajuste baseado na sua fonte
         
        # Atualiza medidas reais
        fm = QFontMetrics(font)
        self.char_width = fm.horizontalAdvance('W')
        self.char_height = fm.height()        
        
        
        # Calcula o espaçamento de tabulação corretamente
        metrics = QFontMetrics(font)
        # Garante que tabulações usem espaços fixos
        self.setTabStopDistance(QFontMetrics(font).horizontalAdvance(' ') * 4)        
        self._setup_appearance()
        self._prompt = "> "
        self._init_terminal()
        self._history = []
        self._history_index = 0
        self._ansi_processor = AnsiProcessor(self)  # Novo processador ANSI
        self._xmodem = XMODEM_Transfer()

        # Tamanho baseado em colunas x linhas
        self.COLUNAS = 80
        self.LINHAS = 25
        self.char_width = 10  # Ajuste conforme sua fonte
        self.char_height = 18
        
        self.setFixedSize(
            self.COLUNAS * self.char_width + 20,  # Margem extra
            self.LINHAS * self.char_height + 20
        )
        
        # Configurações adicionais para seleção de texto
        self.setMouseTracking(True)  # Habilita tracking do mouse
        self.setReadOnly(False)      # Permite seleção mesmo em modo "terminal"
        self.setTextInteractionFlags(
            #self.textInteractionFlags() | 
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        

        #****************************************************************
        # 1. Configuração principal da barra de scroll
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Desabilita scroll horizontal
        # 2. Configurações complementares ESSENCIAIS
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)  # Sem quebra automática
        self.setWordWrapMode(QTextOption.WrapMode.NoWrap)  # Sem quebra de palavras
        # 3. Garantir que o conteúdo não force o scroll
        self.setMaximumBlockCount(1000)  # Limite de linhas no buffer
        self.setCenterOnScroll(False)  # Otimização de performance        
        
        #****************************************************************
        # Configuração do blink manual
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._toggle_cursor)
        self._cursor_visible = False
        self._cursor_position = 0
        self._blink_rate = 500  # ms
        
        # Desativa o cursor padrão do Qt
        self.setCursorWidth(0)  # Torna invisível
        
        # Timer para controle manual
        self._blink_timer.start(self._blink_rate)
        #****************************************************************
                    
    def test_largura(self):
        # Desenha uma linha de referência
        self.insertPlainText("|" + "-" * (self.COLUNAS-2) + "|\n")
        self.insertPlainText("Colunas: " + str(self.COLUNAS) + "\n")
    #Controle de largura
    def resizeEvent(self, event):
        """Garante que o texto respeite a largura visível"""
        fm = QFontMetrics(self.font())
        self.COLUNAS = int(self.viewport().width() / fm.horizontalAdvance('W'))
        super().resizeEvent(event)
    
    def resizeEvent(self, event):
        """Atualiza colunas quando o terminal é redimensionado"""
        fm = QFontMetrics(self.font())
        self.COLUNAS = max(40, int(self.width() / fm.horizontalAdvance('W')))
        super().resizeEvent(event)
                
    def _toggle_cursor(self):
        """Alterna a visibilidade do cursor desenhado manualmente"""
        #if not self.hasFocus():
        #    return
            
        self._cursor_visible = not self._cursor_visible
        self.viewport().update()  # Força redesenho

    def paintEvent(self, event):
        """Desenha o cursor manualmente"""
        super().paintEvent(event)
        
        if self._cursor_visible and self.hasFocus():
            painter = QPainter(self.viewport())
            try:
                # Obtém a geometria do cursor atual
                cursor = self.textCursor()
                cursor_rect = self.cursorRect(cursor)
                
                # Desenha um retângulo estilo terminal (2px de largura)
                painter.fillRect(
                    cursor_rect.x(), 
                    cursor_rect.y(), 
                    2,  # Largura do cursor
                    cursor_rect.height(), 
                    self.palette().color(self.palette().ColorRole.Text)
                )
            finally:
                painter.end()            
        #****************************************************************



    def write_terminal(self, text):
        """Escreve texto na posição atual do cursor"""
        cursor = self.textCursor()
        
        # Remove seleção se houver
        cursor.clearSelection()

        if 'A[' in text:  # Se tiver códigos Xmodem Init
            print("Xmodem INIT")
            self.transfer_in_progress = True
        if 'B[' in text:  # Se tiver códigos Xmodem End
            print("Xmodem END")
            self.transfer_in_progress = False
        if '\x1b[-' in text:  # Se tiver códigos ANSI
            print("ANSI")
            self._ansi_processor.process_text(text)
            
        if self.transfer_in_progress == True:    
            self._xmodem.receive_byte_from_serial(text)
        else:
            print("Normal")
            if cursor.positionInBlock() >= self.COLUNAS:
                cursor.insertText('\n')
            cursor.insertText(text)
        
        # Mantém o cursor visível
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

            
    def write_terminal1(self, text):
        """Escreve texto na posição atual do cursor"""
        cursor = self.textCursor()
        
        # Remove seleção se houver
        cursor.clearSelection()
        
        # Insere o texto na posição atual
        cursor.insertText(text)
        
        # Mantém o cursor visível
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
                   
    def _setup_appearance(self):
        """Configuração visual do terminal"""
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: black;
                color: #00FF00;
                font-family: 'Courier New';
                font-size: 12pt;
                border: 1px solid #00aa00;
            }
        """)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setCursorWidth(8)  # Cursor largo e visível
        self.setMouseTracking(False)
        self._ansi_processor = AnsiProcessor(self)
        
    def _init_terminal(self):
        self.clear()
        #self.insertPlainText(self._prompt)
        self._command_buffer = ""
        self._command_pos = 0
        self.setCursorWidth(10)  # Cursor mais visível
        self._move_cursor_to_end()
        self.setMouseTracking(False)  # Desativa tracking do mouse
        
    def keyPressEvent(self, event):
        key = event.key()
        char = event.text()
        self._move_cursor_to_end()  
                     
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_C:
            super().keyPressEvent(event)  # Executa a cópia padrão
            QTimer.singleShot(100, self._move_cursor_to_end)  # Volta após cópia
        else:  
            if event.text():  # Se for tecla imprimível
                cursor = self.textCursor()
                if cursor.hasSelection():  # Se havia texto selecionado
                    cursor.clearSelection()  # Limpa seleção
                    cursor.movePosition(QTextCursor.MoveOperation.End)  # Vai pro final
                    self.setTextCursor(cursor)
            
            super().keyPressEvent(event)  # Processa a tecla normalmente       
            #****************************************************************
            self._cursor_position = self.textCursor().position()
            self._restart_blink()
            #****************************************************************
            if char and key != Qt.Key.Key_Backspace and key != Qt.Key.Key_Return and key != Qt.Key.Key_Enter:
                self._command_buffer = char
                self._envia_char()
                return
                
            if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
                self._command_buffer = '\n'
                self._envia_enter()
                return
                
            if key == Qt.Key.Key_Backspace:
                if len(self._command_buffer) > 0:
                    self._command_buffer = self._command_buffer[:-1]
                return
                
            if key == Qt.Key.Key_Up:
                self._recall_history(-1)
                return
                
            if key == Qt.Key.Key_Down:
                self._recall_history(1)
                return
                
    
    def _key_to_str(self, key, text=""):
        """Versão simplificada que não requer o event completo"""
        key_map = {
            Qt.Key.Key_Return: "[ENTER]",
            Qt.Key.Key_Enter: "[NUM_ENTER]",
            Qt.Key.Key_Backspace: "[BACKSPACE]",
            Qt.Key.Key_Up: "[UP]",
            Qt.Key.Key_Down: "[DOWN]",
            Qt.Key.Key_Left: "[LEFT]",
            Qt.Key.Key_Right: "[RIGHT]",
            Qt.Key.Key_Tab: "[TAB]",
            Qt.Key.Key_Delete: "[DEL]",
            Qt.Key.Key_Home: "[HOME]",
            Qt.Key.Key_End: "[END]",
            Qt.Key.Key_PageUp: "[PGUP]",
            Qt.Key.Key_PageDown: "[PGDN]"
        }
        return key_map.get(key, text)  # Usa o texto fornecido para teclas normais
    
#Deprecada
#    def _recall_history(self, direction):
#        if not self._history:
#            return
#            
#        self._history_index = max(0, min(self._history_index + direction, len(self._history) - 1))
    
#Deprecada
#    def _update_display(self):
#        cursor = self.textCursor()
#        cursor.movePosition(QTextCursor.MoveOperation.End)
#        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
#        #cursor.removeSelectedText()
#        #cursor.insertText(self._prompt)
#        #cursor.insertText(self._prompt + self._command_buffer)
#        self.setTextCursor(cursor)
    
    def _envia_enter(self):
        cmd = self._command_buffer
        self.data_to_send.emit(cmd)
        self._command_buffer = ""
        
    def _envia_char(self):    
        cmd = self._command_buffer
        self.data_to_send.emit(cmd)
        self._command_buffer = ""
       
    def print_buffer_hex(self):
        """Imprime o buffer byte a byte em hexa"""
        hex_str = " ".join(f"{byte:02X}" for byte in self._command_buffer.encode('utf-8'))
        self.write_terminal(f"\nBuffer em HEX: {hex_str}\n")        
                  
    def _restart_blink(self):
        """Reinicia o ciclo de blink"""
        self._cursor_visible = True
        self._blink_timer.start(self._blink_rate)
        self.viewport().update()    
    def mousePressEvent(self, event):
        """Atualiza posição do cursor ao clicar"""
        super().mousePressEvent(event)
        self._cursor_position = self.textCursor().position()
        self._restart_blink()   

    def mouseReleaseEvent(self, event):
        """Só interfere se for clique esquerdo sem menu"""
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.textCursor().hasSelection():
                self.moveCursor(QTextCursor.MoveOperation.End)
        super().mouseReleaseEvent(event)
    
    def contextMenuEvent(self, event):
        """Menu de contexto padrão sem interferências"""
        menu = self.createStandardContextMenu()
        menu.exec(event.globalPos())
    
    def _move_cursor_to_end(self):
        """Move o cursor para o final do texto com rolagem"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()    

    def _move_cursor(self, row, col):
        """Move o cursor de forma confiável para linha/coluna específica"""
        # 1. Obtém o documento
        doc = self.document()
        
        # 2. Garante que a linha existe (cria se necessário)
        while row >= doc.blockCount():
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText("\n")
        
        # 3. Obtém o bloco (linha) desejado
        block = doc.findBlockByNumber(row)
        
        # 4. Prepara o cursor
        cursor = QTextCursor(block)
        
        # 5. Garante que a coluna existe (preenche com espaços se necessário)
        if col >= block.length() - 1:
            cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
            cursor.insertText(" " * (col - block.length() + 1))
        else:
            cursor.setPosition(block.position() + col)
        
        # 6. Aplica o cursor
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        
        # DEBUG (mostra a posição real)
        current_block = self.textCursor().block().blockNumber()
        print(f"Cursor REAL: linha {current_block+1}, col {self.textCursor().positionInBlock()+1}")

    def insertPlainText(self, text):
        """Sobrescreve para forçar quebra nas colunas corretas"""
        cursor = self.textCursor()
        #cursor.insertText(f"Colunas: {self.COLUNAS}\n")
        for char in text:
            if cursor.positionInBlock() >= self.COLUNAS:
                cursor.insertText('\n')
            cursor.insertText(char)
        self.setTextCursor(cursor)
#Deprecada
#    def _move_cursor1(self, row, col):
#        """Move o cursor de forma confiável para linha/coluna específica"""
#        # 1. Obtém o documento
#        doc = self.terminal.document()
#        
#        # 2. Garante que a linha existe (cria se necessário)
#        while row >= doc.blockCount():
#            cursor = self.terminal.textCursor()
#            cursor.movePosition(QTextCursor.MoveOperation.End)
#            cursor.insertText("\n")
#        
#        # 3. Obtém o bloco (linha) desejado
#        block = doc.findBlockByNumber(row)
#        
#        # 4. Prepara o cursor
#        cursor = QTextCursor(block)
#        
#        # 5. Garante que a coluna existe (preenche com espaços se necessário)
#        if col >= block.length() - 1:
#            cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
#            cursor.insertText(" " * (col - block.length() + 1))
#        else:
#            cursor.setPosition(block.position() + col)
#        
#        # 6. Aplica o cursor
#        self.terminal.setTextCursor(cursor)
#        self.terminal.ensureCursorVisible()
#        
#        # DEBUG (mostra a posição real)
#        current_block = self.terminal.textCursor().block().blockNumber()
#        print(f"Cursor REAL: linha {current_block+1}, col {self.terminal.textCursor().positionInBlock()+1}")
