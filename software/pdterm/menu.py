import tkinter as tk
from tkinter import messagebox

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Menu de Opções")
        
        # Botão principal que abre o menu
        self.btn_opcoes = tk.Button(root, text="Opções", command=self._mostrar_opcoes)
        self.btn_opcoes.pack(pady=20)

        # Terminal simulado (apenas para exemplo)
        self.terminal = tk.Text(root, height=10, width=50)
        self.terminal.pack()

    def _mostrar_opcoes(self):
        """Cria um menu popup com as opções."""
        menu_opcoes = tk.Menu(self.root, tearoff=0)  # tearoff=0 remove a linha tracejada
        
        # Lista de opções e seus métodos associados
        options = [
            ("Option 1", self._toggle_serial),
            ("Option 2", self._send_file),
            ("Option 3", self._save_log),
            ("Option 4", self._scan_ports),
            ("Option 5", self._meu_item),
            ("Option 6", self._clear_terminal),
        ]
        
        # Adiciona cada opção ao menu
        for text, command in options:
            menu_opcoes.add_command(label=text, command=command)
        
        # Mostra o menu na posição do mouse
        menu_opcoes.tk_popup(
            self.btn_opcoes.winfo_rootx(),
            self.btn_opcoes.winfo_rooty() + self.btn_opcoes.winfo_height()
        )

    # Métodos das opções
    def _toggle_serial(self):
        messagebox.showinfo("Ação", "Serial toggled!")

    def _send_file(self):
        messagebox.showinfo("Ação", "File sent!")

    def _save_log(self):
        messagebox.showinfo("Ação", "Log saved!")

    def _scan_ports(self):
        messagebox.showinfo("Ação", "Ports scanned!")

    def _meu_item(self):
        messagebox.showinfo("Ação", "Meu item selecionado!")

    def _clear_terminal(self):
        self.terminal.delete("1.0", tk.END)

# Executa a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
