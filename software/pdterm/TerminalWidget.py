#!/usr/bin/python3
#from PyQt6.QtWidgets import (QMainWindow, QApplication, QPlainTextEdit, QVBoxLayout, 
#                            QWidget, QToolBar, QStatusBar, QFileDialog, QLabel, QMenu)
from PyQt6.QtWidgets import (QPlainTextEdit)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor, QColor, QFont

from AnsiProcessor import AnsiProcessor



class TerminalWidget(QPlainTextEdit):
    data_to_send = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_appearance()
        self._prompt = "> "
        self._init_terminal()
        self._history = []
        self._history_index = 0
        self._ansi_processor = AnsiProcessor(self)  # Novo processador ANSI
        
    def write_terminal(self, text):
        """Processa texto contendo códigos ANSI antes de exibir"""
        #self._ansi_processor.process_text(text)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        #if text.find('6') != -1:
        #    self.insertPlainText("Text == 6 ")
        self.insertPlainText(text)
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
        
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self._execute_command()
            return
            
        if key == Qt.Key.Key_Backspace:
            if len(self._command_buffer) > 0:
                self._command_buffer = self._command_buffer[:-1]
                #self._update_display()
            return
            
        if key == Qt.Key.Key_Up:
            self._recall_history(-1)
            return
            
        if key == Qt.Key.Key_Down:
            self._recall_history(1)
            return
            
        if char and key != Qt.Key.Key_Backspace:
            cursor = self.textCursor()
            self._command_buffer += char
            #Write char digited to screen 
            cursor.insertText(self._command_buffer)
            #self._update_display()
    
    def _recall_history(self, direction):
        if not self._history:
            return
            
        self._history_index = max(0, min(self._history_index + direction, len(self._history) - 1))
        #self._command_buffer = self._history[self._history_index]
        #self._update_display()
    
    def _update_display(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        #cursor.removeSelectedText()
        #cursor.insertText(self._prompt)
        #cursor.insertText(self._prompt + self._command_buffer)
        self.setTextCursor(cursor)
    
    def _execute_command(self):
        #self.insertPlainText(self._prompt)
        self.ensureCursorVisible()
        command = self._command_buffer.strip()
        if command:
            self._history.append(command)
            self._history_index = len(self._history)
            #Send digited char to serial
            self.data_to_send.emit(command)
        self._command_buffer = ""
                  
    
    def mousePressEvent(self, event):
        """Ignora cliques do mouse para manter o cursor na posição correta"""
        self._move_cursor_to_end()
    
    def mouseDoubleClickEvent(self, event):
        """Ignora duplo-clique"""
        self._move_cursor_to_end()
    
    def mouseMoveEvent(self, event):
        """Ignora movimentos do mouse"""
        pass
    
    def _move_cursor_to_end(self):
        """Move o cursor para o final da linha de comando"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
