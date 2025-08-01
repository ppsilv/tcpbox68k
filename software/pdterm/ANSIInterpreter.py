#!/usr/bin/python3
import re
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto

class Color(Enum):
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

class TextAttribute(Enum):
    NORMAL = auto()
    BOLD = auto()
    UNDERLINE = auto()
    INVERSE = auto()

@dataclass
class CursorState:
    x: int = 1
    y: int = 1
    saved_x: int = 1
    saved_y: int = 1
    visible: bool = True
    fg_color: Color = Color.WHITE
    bg_color: Color = Color.BLACK
    attribute: TextAttribute = TextAttribute.NORMAL

class ANSIInterpreter:
    def __init__(self, width=80, height=24):
        self.width = width
        self.height = height
        self.cursor = CursorState()
        self.screen = [[' ' for _ in range(width)] for _ in range(height)]
        self.escape_parser = {
            'H': self._cursor_position,
            'A': self._cursor_up,
            'B': self._cursor_down,
            'C': self._cursor_forward,
            'D': self._cursor_backward,
            's': self._cursor_save,
            'u': self._cursor_restore,
            'J': self._clear_screen,
            'K': self._clear_line,
            '?25h': self._cursor_show,
            '?25l': self._cursor_hide,
            'm': self._set_attributes
        }
        self.minicom_commands = {
            '\x01Z': self._minicom_help,
            '\x01O': self._minicom_config,
            '\x01Q': self._minicom_quit,
            '\x01X': self._minicom_force_quit,
            '\x01L': self._minicom_capture,
            '\x01C': self._minicom_clear
        }
        self.ansi_pattern = re.compile(r'\x1b\[([\d;]*)([a-zA-Z])')

    def process_input(self, text):
        output = []
        i = 0
        while i < len(text):
            char = text[i]
            
            # Process Minicom commands (Ctrl+A)
            if char == '\x01' and i+1 < len(text):
                cmd = text[i:i+2]
                if cmd in self.minicom_commands:
                    self.minicom_commands[cmd]()
                    i += 2
                    continue
            
            # Process ANSI escape sequences
            if char == '\x1b':
                match = self.ansi_pattern.match(text[i:])
                if match:
                    params, command = match.groups()
                    self._handle_escape(params, command)
                    i += match.end()
                    continue
            
            # Process special characters
            if char == '\r':
                self.cursor.x = 1
            elif char == '\n':
                self.cursor.x = 1
                self.cursor.y += 1
                if self.cursor.y > self.height:
                    self._scroll_up()
                    self.cursor.y = self.height
            elif char == '\x7F':  # Backspace
                self.cursor.x = max(1, self.cursor.x - 1)
            elif char == '\x03':  # Ctrl+C
                self._handle_ctrl_c()
            else:
                # Printable character
                if self.cursor.x <= self.width and self.cursor.y <= self.height:
                    self.screen[self.cursor.y-1][self.cursor.x-1] = char
                    self.cursor.x += 1
                    if self.cursor.x > self.width:
                        self.cursor.x = 1
                        self.cursor.y += 1
                        if self.cursor.y > self.height:
                            self._scroll_up()
                            self.cursor.y = self.height
            
            i += 1
        
        return self._render_screen()

    def _handle_escape(self, params, command):
        handler = self.escape_parser.get(command)
        if handler:
            handler(params)

    def _cursor_position(self, params):
        if not params:
            row, col = 1, 1
        else:
            parts = params.split(';')
            row = int(parts[0]) if parts[0] else 1
            col = int(parts[1]) if len(parts) > 1 and parts[1] else 1
        self.cursor.x = max(1, min(col, self.width))
        self.cursor.y = max(1, min(row, self.height))

    def _cursor_up(self, params):
        n = int(params) if params else 1
        self.cursor.y = max(1, self.cursor.y - n)

    def _cursor_down(self, params):
        n = int(params) if params else 1
        self.cursor.y = min(self.height, self.cursor.y + n)

    def _cursor_forward(self, params):
        n = int(params) if params else 1
        self.cursor.x = min(self.width, self.cursor.x + n)

    def _cursor_backward(self, params):
        n = int(params) if params else 1
        self.cursor.x = max(1, self.cursor.x - n)

    def _cursor_save(self, _):
        self.cursor.saved_x = self.cursor.x
        self.cursor.saved_y = self.cursor.y

    def _cursor_restore(self, _):
        self.cursor.x = self.cursor.saved_x
        self.cursor.y = self.cursor.saved_y

    def _clear_screen(self, params):
        param = params if params else '0'
        if param == '2':  # Clear entire screen
            self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        elif param == '0':  # Clear from cursor to end of screen
            for y in range(self.cursor.y-1, self.height):
                start = self.cursor.x-1 if y == self.cursor.y-1 else 0
                self.screen[y][start:] = [' '] * (self.width - start)
        elif param == '1':  # Clear from beginning to cursor
            for y in range(0, self.cursor.y):
                end = self.cursor.x if y == self.cursor.y-1 else self.width
                self.screen[y][:end] = [' '] * end

    def _clear_line(self, params):
        param = params if params else '0'
        y = self.cursor.y - 1
        if y < 0 or y >= self.height:
            return
            
        if param == '2':  # Clear entire line
            self.screen[y] = [' '] * self.width
        elif param == '0':  # Clear from cursor to end of line
            start = self.cursor.x - 1
            if 0 <= start < self.width:
                self.screen[y][start:] = [' '] * (self.width - start)
        elif param == '1':  # Clear from beginning to cursor
            end = self.cursor.x
            if 0 < end <= self.width:
                self.screen[y][:end] = [' '] * end

    def _cursor_show(self, _):
        self.cursor.visible = True

    def _cursor_hide(self, _):
        self.cursor.visible = False

    def _set_attributes(self, params):
        if not params:
            params = '0'
        
        codes = list(map(int, params.split(';'))) if params else [0]
        
        for code in codes:
            if code == 0:  # Reset
                self.cursor.attribute = TextAttribute.NORMAL
                self.cursor.fg_color = Color.WHITE
                self.cursor.bg_color = Color.BLACK
            elif code == 1:
                self.cursor.attribute = TextAttribute.BOLD
            elif code == 4:
                self.cursor.attribute = TextAttribute.UNDERLINE
            elif code == 7:
                self.cursor.attribute = TextAttribute.INVERSE
            elif 30 <= code <= 37:
                self.cursor.fg_color = Color(code - 30)
            elif 40 <= code <= 47:
                self.cursor.bg_color = Color(code - 40)

    def _scroll_up(self):
        self.screen.pop(0)
        self.screen.append([' ' for _ in range(self.width)])

    def _minicom_help(self):
        print("Minicom Help - Implemente esta função conforme necessário")

    def _minicom_config(self):
        print("Minicom Config - Implemente esta função conforme necessário")

    def _minicom_quit(self):
        print("Minicom Quit - Implemente esta função conforme necessário")

    def _minicom_force_quit(self):
        print("Minicom Force Quit - Implemente esta função conforme necessário")

    def _minicom_capture(self):
        print("Minicom Capture - Implemente esta função conforme necessário")

    def _minicom_clear(self):
        self._clear_screen('2')

    def _handle_ctrl_c(self):
        print("Ctrl+C received - Implemente esta função conforme necessário")

    def _render_screen(self):
        """Renderiza a tela como texto com formatação (simplificado)"""
        lines = []
        for row in self.screen:
            line = ''.join(row)
            lines.append(line.rstrip())
        return '\n'.join(lines)

    def get_cursor_position(self):
        return (self.cursor.x, self.cursor.y)

# Exemplo de uso
if __name__ == "__main__":
    interpreter = ANSIInterpreter(width=80, height=24)
    
    # Testando comandos ANSI
    commands = [
        "\x1b[2J",  # Limpa a tela
        "\x1b[31mHello World!\x1b[0m",  # Texto vermelho
        "\x1b[10;20HTeste",  # Posiciona cursor e escreve
        "\x1b[1A",  # Move cursor para cima
        "Moved Up",
        "\x1b[s",  # Salva posição
        "\x1b[5B",  # Move cursor para baixo
        "Moved Down",
        "\x1b[u",  # Restaura posição
        " (Restored)",
        "\x1b[2K",  # Limpa linha
        "\n\x1b[44mBlue Background\x1b[0m",
        "\x01C"  # Minicom clear (Ctrl+A C)
    ]
    
    for cmd in commands:
        print(">>> Executing:", repr(cmd))
        output = interpreter.process_input(cmd)
        print("Screen:")
        print(output)
        print("Cursor position:", interpreter.get_cursor_position())
        print("-" * 40)
