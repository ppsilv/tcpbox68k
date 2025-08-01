#!/usr/bin/python3
from PyQt6.QtWidgets import (QMainWindow, QApplication, QPlainTextEdit, QVBoxLayout, 
                            QWidget, QToolBar, QStatusBar, QFileDialog, QLabel, QMenu)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor, QColor, QFont
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer, QEventLoop  # Adicione QEventLoop


class MyMenu:
    
    
    
    
    def _setup_toolbar(self, toolbar):
        actions = [
            (" Testes", self._show_menu_dialog),
            (" Conectar", self._toggle_serial),
            (" Enviar Arquivo", self._send_file),
            (" Salvar Log", self._save_log),
            (" Portas", self._scan_ports_2),
            (" Limpar Tela", self.terminal.clear),
            (" Sobre", self._show_about_menu),            
        ]
        for text, callback in actions:
            action = toolbar.addAction(text)
            action.triggered.connect(callback)

    def _meu_item(self):
        self.test_cores_ansi()

    def _toggle_serial(self):
        if not self.serial_port:
            self._show_port_dialog()
        else:
            self._disconnect_serial()

    def _scan_ports(self):
        """Lista apenas portas seriais relevantes (ttyACMx, ttyUSBx)"""
        ports = serial.tools.list_ports.comports()
        filtered_ports = []
        
        # Filtra portas relevantes
        for port in ports:
            if ('ttyACM' in port.device or
                'ttyUSB' in port.device):
                filtered_ports.append(port)
        
        if filtered_ports:
            msg = "\n[INFO] Portas disponíveis:\n"
            for port in filtered_ports:
                msg += f" - {port.device}: {port.description}\n"
            self.terminal.write_terminal(msg)
        else:
            self.terminal.write_terminal("\n[INFO] Nenhuma porta serial relevante encontrada\n")
        
        return filtered_ports

    def _scan_ports_2(self):
        """Mostra portas seriais em um menu popup (ao invés de escrever no terminal)"""
        ports = serial.tools.list_ports.comports()
        filtered_ports = []
        
        # Filtra portas relevantes (ttyACM*, ttyUSB*)
        for port in ports:
            if ('ttyACM' in port.device or 'ttyUSB' in port.device):
                filtered_ports.append(port)
        
        if not filtered_ports:
            self.terminal.write_terminal("\n[ERRO] Nenhuma porta serial encontrada!\n")
            return
        
        # Cria o menu popup
        menu = QMenu(self)
        menu.setTitle("Portas Disponíveis")
        
        # Adiciona cada porta como uma opção clicável
        for port in filtered_ports:
            action = menu.addAction(f"{port.device} - {port.description}")
            action.triggered.connect(
                lambda _, p=port.device: self._connect_to_port(p)
            )
        
        # Mostra o menu abaixo do botão "Portas" na toolbar
        toolbar = self.findChild(QToolBar)
        for action in toolbar.actions():
            if "Portas" in action.text():
                btn = toolbar.widgetForAction(action)
                menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
                break
    def _show_about_menu(self):
        """Mostra um menu popup com informações sobre o programa (não clicável)"""
        menu = QMenu(self)
        menu.setTitle("Sobre o PDTerm Pro")
        
        # Adiciona itens não clicáveis
        about_items = [
            "PDTerm Pro - Terminal Serial Avançado",
            "Versão: 1.0.0",
            "Autor: Seu Nome",
            "Licença: GPLv3",
            "GitHub: github.com/seuuser/pdterm",
            "🖥️🔥 PDSILVA - O Alquimista dos Bytes"
        ]
        
        for item in about_items:
            action = menu.addAction(item)
            action.setEnabled(False)  # Desabilita cliques
            
        # Mostra o menu abaixo do botão "Sobre" na toolbar
        toolbar = self.findChild(QToolBar)
        for action in toolbar.actions():
            if "Sobre" in action.text():
                btn = toolbar.widgetForAction(action)
                menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
                break
                                    
    def _show_port_dialog(self):
        """Mostra diálogo apenas com portas relevantes"""
        ports = self._scan_ports()  # Agora usa a lista filtrada
        
        if not ports:
            self.terminal.write_terminal("\n[ERRO] Nenhuma porta serial relevante encontrada!\n")
            return
        
        menu = QMenu(self)
        
        for port in ports:
            action = menu.addAction(f"{port.device} - {port.description}")
            action.triggered.connect(lambda _, p=port.device: self._connect_to_port(p))
        
        # Mostra menu abaixo do botão de conexão
        toolbar = self.findChild(QToolBar)
        for action in toolbar.actions():
            if "Conectar" in action.text():
                btn = toolbar.widgetForAction(action)
                menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
                break

    def _show_menu_dialog(self):
        options = [
            (" Option 1", self._toggle_serial),
            (" Option 2", self._send_file),
            (" Option 3", self._save_log),
            (" Option 4", self._scan_ports),
            (" Option 5", self._meu_item),
            (" Option 6", self.terminal.clear),
        ]
        menu = QMenu(self)
        
        for option, descript in ports:
            action = menu.addAction(f"{option} - {descript}")
            #action.triggered.connect(lambda _, p=option: self.descript(p))
            action.setEnabled(False)
            
        # Mostra menu abaixo do botão de conexão
        toolbar = self.findChild(QToolBar)
        for action in toolbar.actions():
            if "Conectar1" in action.text():
                btn = toolbar.widgetForAction(action)
                menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
                break

    def _show_menu_dialog(self):
        """Mostra um menu popup com opções personalizadas"""
        menu = QMenu(self)
        
        # Lista de opções (texto, método)
        options = [
            ("Option 1 - Toggle Serial", self._toggle_serial),
            ("Option 2 - Enviar Arquivo", self._send_file),
            ("Option 3 - Salvar Log", self._save_log),
            ("Option 4 - Scan Portas", self._scan_ports),
            ("Option 5 - Meu Item", self._meu_item),
            ("Option 6 - Limpar Terminal", self.terminal.clear),
        ]
        
        # Adiciona cada opção ao menu
        for text, callback in options:
            action = menu.addAction(text)
            action.triggered.connect(callback)
        
        # Mostra o menu abaixo do botão "Testes" na toolbar
        toolbar = self.findChild(QToolBar)
        for action in toolbar.actions():
            if "Testes" in action.text():
                btn = toolbar.widgetForAction(action)
                menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
                break        
    def menu_principal(self):
        #"""Menu que rivaliza com o Norton Commander"""
        #teste = (
        #    "iiiiiiiiii\n"  # 10 i minúsculos
        #    "MMMMMMMMMM\n"  # 10 M maiúsculos
        #    "1234567890\n"
        #    "----------\n"
        #    "┌───────┐\n"
        #    "│ TESTE │\n"
        #    "└───────┘\n\n\n"
        #)
        #self.terminal.write_terminal(teste)    
        ##self.terminal._ansi_processor.process_text(    
        #
        #self.terminal.write_terminal("\x1b[2J\x1b[1;1H")  # Limpa tela
        #self.terminal.write_terminal("\x1b[1;35;40m+-----------------------------------+\n"
        #"\x1b[1;35;40m│ \x1b[1;34m MENU PRINCIPAL\x1b[1;35m                   │\n"
        #"+-----------------------------------+\n"
        #"│                                   │\n"
        #"\x1b[1;31;40m│1 Turbo                            │\n"
        #"\x1b[1;31;40m│2 Banco Dados RETRO                │\n"
        #"\x1b[1;31;40m│3 Terminal MATRIX                  │\n"
        #"\x1b[1;31;40m+-----------------------------------+\n"
        #"\x1b[35mOpção: \x1b[37m")
        #
        #
        #self.terminal.write_terminal(f"\x1b[2J\x1b[1;1H")  # Limpa tela
        #self.terminal.write_terminal(f"\x1bc")
        #self.terminal.write_terminal( 
        #    "\n\n"       
        #    "+-----------------------------------+\n"
        #    "│            MENU PRINCIPAL         │\n"
        #    "├-----------------------------------|\n"
        #    "│                                   │\n"
        #    "│1 Turbo                            │\n"
        #    "│2 Banco Dados RETRO                │\n"
        #    "│3 Terminal MATRIX                  │\n"
        #    "+-----------------------------------+\n"
        #)
        #self.terminal._ansi_processor.process_text(f"\x1b[1;31m")
        #self.terminal._ansi_processor.process_text(f"\x1b[31mteste")
        #self.terminal._ansi_processor.process_text(f"\x1b[1;32m ")
        ##self.terminal._ansi_processor.process_text(f"\033[{row};{col}H")
        ## Primeiro limpe o terminal
        self.terminal.clear()
        self.terminal._ansi_processor.process_text(f"\x1b[1;37m ")
        self.terminal._move_cursor(0, 10)
        self.terminal.write_terminal1("*** row 0 col 10***")
        self.terminal._ansi_processor.process_text(f"\x1b[1;31m ")
        self.terminal._move_cursor(1, 10)
        self.terminal.write_terminal1("*** row 1 col 10***")
        self.terminal._ansi_processor.process_text(f"\x1b[1;32m ")
        self.terminal._move_cursor(2, 10)
        self.terminal.write_terminal1("*** row 2 col 10***")
        self.terminal._ansi_processor.process_text(f"\x1b[1;33m ")       
        self.terminal._move_cursor(3, 10)
        self.terminal.write_terminal1("*** row 3 col 10***")
        self.terminal._ansi_processor.process_text(f"\x1b[1;34m ")
        self.terminal._move_cursor(4, 10)
        self.terminal.write_terminal1("*** row 4 col 10***")
        self.terminal._ansi_processor.process_text(f"\x1b[1;35m ")
        self.terminal._move_cursor(5, 10)
        self.terminal.write_terminal1("*** row 5 col 10***")
        self.terminal._ansi_processor.process_text(f"\x1b[1;36m ")
        self.terminal._move_cursor(6, 10)
        self.terminal.write_terminal1("*** row 6 col 10***")
        self.terminal._ansi_processor.process_text(f"\x1b[1;37m ")
        self.terminal._move_cursor(7, 10)
        self.terminal.write_terminal1("*** row 7 col 10***")
        self.terminal._move_cursor(8, 10)
        self.terminal.write_terminal1("*** row 8 col 10***")
        self.terminal._move_cursor(9, 10)
        self.terminal.write_terminal1("*** row 9 col 10***")
        self.terminal._move_cursor(10, 10)
        self.terminal.write_terminal1("*** row 10 col 10***")
        self.terminal._move_cursor(11, 10)
        self.terminal.write_terminal1("*** row 11 col 10***")
        self.terminal._move_cursor(12, 10)
        self.terminal.write_terminal1("*** row 12 col 10***")
        self.terminal._move_cursor(13, 10)
        self.terminal.write_terminal1("*** row 13 col 10***")
        self.terminal._move_cursor(14, 10)
        self.terminal.write_terminal1("*** row 14 col 10***")
        self.terminal._move_cursor(15, 10)
        self.terminal.write_terminal1("*** row 15 col 10***")
        self.terminal._move_cursor(16, 10)
        self.terminal.write_terminal1("*** row 16 col 10***")
        self.terminal._move_cursor(17, 10)
        self.terminal.write_terminal1("*** row 17 col 10***")
        self.terminal._move_cursor(18, 10)
        self.terminal.write_terminal1("*** row 18 col 10***")
        self.terminal._move_cursor(19, 10)
        self.terminal.write_terminal1("*** row 19 col 10***")
        self.terminal._move_cursor(20, 10)
        self.terminal.write_terminal1("*** row 20 col 10***")
        self.terminal._move_cursor(21, 10)
        self.terminal.write_terminal1("*** row 21 col 10***")
        self.terminal._move_cursor(22, 10)
        self.terminal.write_terminal1("*** row 22 col 10***")
        self.terminal._move_cursor(23, 10)
        self.terminal.write_terminal1("*** row 23 col 10***")
        self.terminal._move_cursor(24, 10)
        #self.terminal.write_terminal1("*** row 24 col 10***")
        #self.terminal._move_cursor(25, 10)
        #self.terminal.write_terminal1("*** row 25 col 10***")
        #self.terminal._move_cursor(26, 10)
        #self.terminal.write_terminal1("*** row 26 col 10***")
        self.terminal._move_cursor(0, 0)
        self.terminal.write_terminal1("0        1         2         3         4         5         6         7         8")
        self.terminal._move_cursor(1, 0)
        self.terminal.write_terminal1("12345678901234567890123456789012345678901234567890123456789012345678901234567890")















