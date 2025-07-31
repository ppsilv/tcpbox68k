#!/usr/bin/python3




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
        if seq.endswith('J'):  # Limpar tela
            if seq.startswith('2'):
                self.terminal.clear()
                self.current_pos = [0, 0]
        elif seq.endswith('H'):  # Posicionar cursor
            parts = seq[:-1].split(';')
            row = int(parts[0]) - 1 if parts[0] else 0
            col = int(parts[1]) - 1 if len(parts) > 1 else 0
            self._move_cursor(row, col)
        elif seq.endswith('m'):  # Cores (implementação básica)
            pass  # Pode implementar cores aqui

    def _execute_esc(self, cmd):
        if cmd == 'c':  # Reset terminal
            self.terminal.clear()
            self.current_pos = [0, 0]

    def _move_cursor(self, row, col):
        """Move o cursor para a posição especificada"""
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        # Move para a linha correta
        for _ in range(row):
            cursor.movePosition(QTextCursor.MoveOperation.Down)
        
        # Move para a coluna
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        for _ in range(col):
            cursor.movePosition(QTextCursor.MoveOperation.Right)
            
        self.terminal.setTextCursor(cursor)
        self.current_pos = [row, col]

    def _insert_char(self, char):
        """Insere caractere na posição atual"""
        cursor = self.terminal.textCursor()
        cursor.insertText(char)
        self.current_pos[1] += 1
        
        # Quebra de linha automática
        if self.current_pos[1] >= 80:  # 80 colunas padrão
            self.current_pos[0] += 1
            self.current_pos[1] = 0
            cursor.insertText('\n')

    def _reset_state(self):
        self.escape = False
        self.csi = False
        self.buffer = ""
