#!/usr/bin/python3
from PyQt6.QtWidgets import QMenu, QToolBar
from PyQt6.QtGui import QAction, QIcon  # QAction agora está em QtGui
from PyQt6.QtCore import Qt
import serial.tools.list_ports

class PdTermMenu:
    def __init__(self, parent):
        self.parent = parent  # Referência para PDTermPro
        self._verify_methods()
        self._setup_styles()
    
    def setup_toolbar(self):
        """Configura toda a toolbar e seus menus"""
        toolbar = QToolBar()
        
        # Lista de ações: (texto, ícone, menu ou callback)
        actions = [
            ("Opções", None, self._create_main_menu()),
            ("Conectar", None, self.parent._toggle_serial),
            ("Enviar Arquivo", None, self.parent._send_file),
            ("Salvar Log", None, self.parent._save_log),
            ("Portas", None, self.parent._show_ports_dialog),
            ("Limpar", None, self.parent.terminal.clear),
            ("Limpar Buffer", None, self.parent.terminal._emergency_clear),            
            ("Sobre", None, self._create_about_menu())
        ]

        for text, icon, target in actions:
            action = QAction(text, self.parent)
            if icon:  # Se quiser usar ícones posteriormente
                action.setIcon(QIcon.fromTheme(icon))            
            if isinstance(target, QMenu):
                action.triggered.connect(lambda _, m=target: self._show_menu(m, text))
            else:
                action.triggered.connect(target)                
            toolbar.addAction(action)
        return toolbar
    
    def _verify_methods(self):
        required_methods = ['test_cores_ansi', 'pgordao_terminal_mode']
        for method in required_methods:
            if not hasattr(self.parent, method):
                raise AttributeError(f"O método '{method}' não existe na classe principal!")

    def _create_main_menu(self):
        """Menu principal de opções"""
        menu = QMenu(self.parent)
        options = [
            ("Alternar Serial", self.parent._toggle_serial),
            ("Testar Cores ANSI", self.parent.test_cores_ansi),  # Nome corrigido aqui
            ("Modo PGORDÃO", self.parent.pgordao_terminal_mode)
        ]
        for text, callback in options:
            menu.addAction(text, callback)
        return menu
#Deprecada
#    def _create_ports_menu(self):
#        """Menu de portas seriais"""
#        menu = QMenu(self.parent)
#        ports = [p for p in serial.tools.list_ports.comports() 
#                if 'ttyACM' in p.device or 'ttyUSB' in p.device]
#        
#        for port in ports:
#            menu.addAction(
#                f"{port.device} - {port.description}",
#                lambda p=port.device: self.parent._connect_to_port(p)
#            )
#        return menu

    def create_ports_menu(self):
        """Cria e retorna o menu de portas serial"""
        ports = [p for p in serial.tools.list_ports.comports() 
                if 'ttyACM' in p.device or 'ttyUSB' in p.device]
        
        menu = QMenu(self.parent)
        menu.setTitle("Portas Disponíveis")
        
        if not ports:
            menu.addAction("Nenhuma porta encontrada").setEnabled(False)
            return menu
        
        for port in ports:
            menu.addAction(
                f"{port.device} - {port.description}",
                lambda p=port.device: self.parent._connect_to_port(p)
            )
        return menu 


    def _create_about_menu(self):
        """Menu 'Sobre' informativo"""
        menu = QMenu(self.parent)
        info = [
            "PDTerm Pro v1.0",
            "Desenvolvido por PDSILVA",
            "Licença: GPLv3",
            "github.com/pdsilva/pdterm"
        ]
        for item in info:
            action = menu.addAction(item)
            action.setEnabled(False)
        return menu

    def _show_menu(self, menu, button_text):
        """Mostra menu abaixo do botão correspondente"""
        toolbar = self.parent.findChild(QToolBar)
        for action in toolbar.actions():
            if button_text in action.text():
                menu.exec(toolbar.widgetForAction(action).mapToGlobal(
                    toolbar.widgetForAction(action).rect().bottomLeft()
                ))
                break

    def _setup_styles(self):
        """Configura estilos consistentes"""
        self.parent.setStyleSheet("""
            QMenu {
                background-color: #2e2e2e;
                color: #00ff00;
                border: 1px solid #00aa00;
            }
            QMenu::item:selected {
                background-color: #3e3e3e;
            }
        """)
