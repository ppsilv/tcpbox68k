from PyQt5.QtWidgets import QPlainTextEdit, QApplication
from PyQt5.QtGui import QTextCharFormat, QColor, QTextCursor
from PyQt5.QtCore import Qt
from ANSIInterpreter import ANSIInterpreter, Color, TextAttribute
import sys

class TerminalWidget(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.interpreter = ANSIInterpreter(width=80, height=24)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setStyleSheet("font-family: 'Courier New'; font-size: 12pt;")
        
        # Mapeamento de cores ANSI para Qt
        self.color_map = {
            Color.BLACK: QColor('#000000'),
            Color.RED: QColor('#FF0000'),
            Color.GREEN: QColor('#00FF00'),
            Color.YELLOW: QColor('#FFFF00'),
            Color.BLUE: QColor('#0000FF'),
            Color.MAGENTA: QColor('#FF00FF'),
            Color.CYAN: QColor('#00FFFF'),
            Color.WHITE: QColor('#FFFFFF')
        }
        
        # Estado atual de formatação
        self.current_format = self._create_char_format()
    
    def write(self, data):
        # Processa os dados com o interpretador
        self.interpreter.process_input(data)
        
        # Atualiza a exibição
        self._update_display()
    
    def _update_display(self):
        self.clear()
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        
        # Renderiza toda a tela com formatação
        for y in range(self.interpreter.height):
            line_start = True
            current_format = None
            
            for x in range(self.interpreter.width):
                char = self.interpreter.screen[y][x]
                
                # Obtém a formatação para esta posição
                new_format = self._get_char_format(y, x)
                
                # Aplica nova formatação apenas quando mudar
                if new_format != current_format or line_start:
                    cursor.setCharFormat(new_format)
                    current_format = new_format
                
                cursor.insertText(char)
                line_start = False
            
            if y < self.interpreter.height - 1:
                cursor.insertText("\n")
        
        # Posiciona o cursor
        self._position_cursor()
    
    def _get_char_format(self, y, x):
        # Cria um novo formato baseado no estado do interpretador
        fmt = QTextCharFormat()
        
        # Aplica cor do texto
        fmt.setForeground(self.color_map.get(self.interpreter.cursor.fg_color, QColor('#FFFFFF')))
        
        # Aplica cor de fundo
        fmt.setBackground(self.color_map.get(self.interpreter.cursor.bg_color, QColor('#000000')))
        
        # Aplica atributos de texto
        if self.interpreter.cursor.attribute == TextAttribute.BOLD:
            fmt.setFontWeight(75)  # Negrito
        if self.interpreter.cursor.attribute == TextAttribute.UNDERLINE:
            fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        if self.interpreter.cursor.attribute == TextAttribute.INVERSE:
            fg = fmt.foreground().color()
            bg = fmt.background().color()
            fmt.setForeground(bg)
            fmt.setBackground(fg)
        
        return fmt
    
    def _position_cursor(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        
        # Move para a linha correta
        for _ in range(self.interpreter.cursor.y - 1):
            cursor.movePosition(QTextCursor.Down)
        
        # Move para a coluna correta
        for _ in range(self.interpreter.cursor.x - 1):
            cursor.movePosition(QTextCursor.Right)
        
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
    
    def _create_char_format(self):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor('#FFFFFF'))
        fmt.setBackground(QColor('#000000'))
        return fmt

if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal = TerminalWidget()
    terminal.setWindowTitle("Terminal ANSI - Funcional")
    terminal.resize(800, 600)
    terminal.show()
    
    # Teste com comandos ANSI - AGORA COM CORES VISÍVEIS
    test_commands = [
        "\x1b[2J",  # Limpa a tela
        "\x1b[31mTexto Vermelho\x1b[0m\n",
        "\x1b[32mTexto Verde\x1b[0m\n",
        "\x1b[44mFundo Azul\x1b[0m\n",
        "\x1b[1;31mNegrito Vermelho\x1b[0m\n",
        "\x1b[4mSublinhado\x1b[0m\n",
        "\x1b[7mInvertido\x1b[0m\n",
        "\x1b[10;20HPosicionado na linha 10, coluna 20"
    ]
    
    for cmd in test_commands:
        terminal.write(cmd)
        QApplication.processEvents()  # Força atualização da interface
    
    sys.exit(app.exec_())
