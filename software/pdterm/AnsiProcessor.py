#!/usr/bin/python3

from PyQt6.QtGui import QTextCursor, QColor, QFont


class AnsiProcessor:
    def __init__(self, terminal):
        self.terminal = terminal
        self.escape = False
        self.csi = False
        self.buffer = ""
        self.current_pos = [0, 0]  # Linha, coluna atual

    def process_text(self, text):
        for char in text:
            if self.escape:
                self._handle_escape(char)
            elif char == '\x1b':  # ESC
                self.escape = True
                self.buffer = char
            else:
                self._insert_char(char)

    def _handle_escape(self, char):
        self.buffer += char
        
        if len(self.buffer) == 2 and char == '[':
            self.csi = True
            return
            
        if self.csi and char.isalpha():
            self._execute_csi(self.buffer[2:])
            self._reset_state()
        elif char.isalpha():
            self._execute_esc(char)
            self._reset_state()

    def _execute_csi(self, seq):
        """Processa sequências CSI (Control Sequence Introducer)"""
        if seq.endswith('J'):  # Limpar tela
            if seq.startswith('2'):
                self.terminal.clear()
                self.current_pos = [0, 0]
        elif seq.endswith('H'):  # Posicionar cursor
            parts = seq[:-1].split(';')
            row = int(parts[0]) - 1 if parts[0] else 0
            col = int(parts[1]) - 1 if len(parts) > 1 else 0
            self._move_cursor(row, col)
            
        elif seq.endswith('m'):  # Cores ANSI
            self._handle_sgr(seq[:-1])  # Remove o 'm' final

    def _execute_esc(self, cmd):
        if cmd == 'c':  # Reset terminal
            self.terminal.clear()
            self.current_pos = [0, 0]

    def _move_cursor(self, row, col):
        """Move o cursor para posição específica (linha/coluna base 0)"""
        cursor = self.terminal.textCursor()
        
        # Posiciona no início do documento
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        # Move para a linha desejada
        for _ in range(row):
            if not cursor.movePosition(QTextCursor.MoveOperation.Down):
                break  # Chegou ao final do documento
        
        # Move para a coluna desejada
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        for _ in range(col):
            if not cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor):
                break  # Chegou ao final da linha
        
        self.terminal.setTextCursor(cursor)
        self.current_pos = [row, col]
        
        # DEBUG (opcional)
        self.terminal.insertPlainText(f"Cursor movido para L{row+1}C{col+1}\n")

    def _insert_char(self, char):
        """Insere caractere na posição atual"""
        if char == '\x1b':  # Início de sequência ANSI
            self.escape = True
            self.buffer = char
            return
            
        if self.escape:  # Se processando ANSI, não conta como coluna
            return
            
        # Envia o caractere para o terminal processar
        self.terminal.insertPlainText(char)
        
        # Atualiza posição (simulação)
        self.current_pos[1] += 1
        
        # Quebra de linha em 80 colunas (opcional)
        if self.current_pos[1] >= 80:
            self.current_pos[0] += 1
            self.current_pos[1] = 0
            self.terminal.insertPlainText('\n')

    def _reset_state(self):
        self.escape = False
        self.csi = False
        self.buffer = ""

    def _handle_sgr(self, codes_str):
        """Processa códigos SGR (Select Graphic Rendition)"""
        if not codes_str:
            codes = ['0']  # Reset padrão se nenhum código for fornecido
        else:
            codes = codes_str.split(';')
        
        cursor = self.terminal.textCursor()
        fmt = cursor.charFormat()
        
        for code in codes:
            if not code:
                continue
                
            code = int(code)
            
            # Cores básicas
            if code == 0:  # Reset
                fmt.setForeground(QColor('white'))
                fmt.setBackground(QColor('black'))
            elif 30 <= code <= 37:  # Cores do texto
                colors = [
                    'black', 'red', 'green', 'yellow', 
                    'blue', 'magenta', 'cyan', 'white'
                ]
                fmt.setForeground(QColor(colors[code-30]))
            elif 40 <= code <= 47:  # Cores de fundo
                colors = [
                    'black', 'red', 'green', 'yellow', 
                    'blue', 'magenta', 'cyan', 'white'
                ]
                fmt.setBackground(QColor(colors[code-40]))
            elif code == 1:  # Bold (negrito)
                fmt.setFontWeight(QFont.Weight.Bold)
            elif code == 4:  # Underline (sublinhado)
                fmt.setFontUnderline(True)
            elif code == 7:  # Reverse video (inverte cores)
                bg = fmt.background().color()
                fg = fmt.foreground().color()
                fmt.setBackground(fg)
                fmt.setForeground(bg)
        
        cursor.setCharFormat(fmt)
        self.terminal.setTextCursor(cursor)
