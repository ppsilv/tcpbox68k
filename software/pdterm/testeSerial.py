#!/usr/bin/env python3
# Autor: Fernando Krein Pinheiro (atualizado com verificações de conexão)

import serial
import serial.tools.list_ports
import sys
import os
class SerialManager:
    def __init__(self):
        self.porta_serial = None
        self.porta_atual = None
        self.baudrate_atual = None
        
    def verificar_conexao(self):
        """Verifica se a porta está conectada e aberta"""
        if self.porta_serial is None:
            return False, "Nenhum objeto serial criado"
            
        if not hasattr(self.porta_serial, 'is_open'):
            return False, "Objeto serial inválido"
            
        if not self.porta_serial.is_open:
            return False, "Porta serial fechada"
            
        # Verificação extra no Linux
        if sys.platform == 'linux':
            if not os.path.exists(self.porta_serial.port):
                return False, "Porta não existe no sistema"
                
        return True, "Conectado e operacional"

    def listar_portas(self):
        """Lista todas as portas seriais disponíveis com verificação"""
        try:
            portas = serial.tools.list_ports.comports()
            if not portas:
                print("\n[STATUS] Nenhuma porta serial encontrada!")
                return []
                
            print("\n[PORTAS DISPONÍVEIS]")
            for i, porta in enumerate(portas, 1):
                status = "(Disponível)"
                try:
                    teste = serial.Serial(porta.device)
                    teste.close()
                except:
                    status = "(Em uso/inacessível)"
                print(f"{i}. {porta.device} - {porta.description} {status}")
            return portas
            
        except Exception as e:
            print(f"\n[ERRO] Falha ao listar portas: {e}")
            return []

    def conectar(self, porta, baudrate):
        """Estabelece conexão serial com verificações"""
        # Verifica se já está conectado à mesma porta
        status, msg = self.verificar_conexao()
        if status and self.porta_atual == porta:
            print(f"\n[STATUS] Já conectado a {porta}")
            return True
            
        # Fecha conexão existente se houver
        self.desconectar()
        
        try:
            print(f"\n[CONEXÃO] Tentando conectar a {porta} @ {baudrate} bauds...")
            self.porta_serial = serial.Serial(
                port=porta,
                baudrate=baudrate,
                timeout=1
            )
            
            # Verificação pós-conexão
            if not self.porta_serial.is_open:
                raise serial.SerialException("Porta não abriu após conexão")
                
            self.porta_atual = porta
            self.baudrate_atual = baudrate
            
            print(f"[SUCESSO] Conectado a {porta}")
            return True
            
        except serial.SerialException as e:
            self.porta_serial = None
            print(f"\n[ERRO] Falha na conexão: {e}")
            return False
            
        except Exception as e:
            self.porta_serial = None
            print(f"\n[ERRO INESPERADO] {e}")
            return False

    def ler_dados(self, tamanho=1):
        """Lê dados com verificação de conexão"""
        status, msg = self.verificar_conexao()
        if not status:
            print(f"\n[ERRO] {msg}")
            return None
            
        try:
            print(f"\n[LEITURA] Tentando ler {tamanho} bytes...")
            dados = self.porta_serial.read(tamanho)
            
            if not dados:
                print("[AVISO] Nenhum dado recebido (timeout)")
                return None
                
            print(f"[DADOS] Recebidos {len(dados)} bytes: {dados}")
            return dados
            
        except serial.SerialException as e:
            print(f"\n[ERRO] Falha na leitura: {e}")
            self.desconectar()
            return None

    def escrever_dados(self, dados):
        """Envia dados com verificação de conexão"""
        status, msg = self.verificar_conexao()
        if not status:
            print(f"\n[ERRO] {msg}")
            return False
        print(f"Conteúdo real: {dados!r}")    
        try:
            
            #if isinstance(dados, str):
            #    dados = dados.encode('utf-8')              

            escritos = self.porta_serial.write(dados)
            self.porta_serial.flush()
            
            print(f"[SUCESSO] {escritos} bytes enviados")
            return True
            
        except serial.SerialException as e:
            print(f"\n[ERRO] Falha na escrita: {e}")
            self.desconectar()
            return False

    def desconectar(self):
        """Fecha a conexão com verificações"""
        if self.porta_serial is not None:
            try:
                if hasattr(self.porta_serial, 'is_open') and self.porta_serial.is_open:
                    self.porta_serial.close()
                    print("\n[STATUS] Porta serial fechada")
            except Exception as e:
                print(f"\n[AVISO] Erro ao fechar porta: {e}")
            finally:
                self.porta_serial = None
                self.porta_atual = None
                self.baudrate_atual = None

def main():
    import os
    import sys
    
    gerenciador = SerialManager()
    
    while True:
        print("\n" + "="*50)
        print("GERENCIADOR SERIAL COM VERIFICAÇÕES")
        print("="*50)
        
        # Mostra status atual da conexão
        status, msg = gerenciador.verificar_conexao()
        print(f"\n[STATUS ATUAL] {msg}")
        if status:
            print(f"Porta: {gerenciador.porta_atual}")
            print(f"Baudrate: {gerenciador.baudrate_atual}")
        
        print("\n1. Listar portas seriais")
        print("2. Conectar a uma porta")
        print("3. Ler dados")
        print("4. Enviar dados")
        print("5. Desconectar")
        print("0. Sair")
        print("="*50)
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            gerenciador.listar_portas()
            
        elif opcao == "2":
            porta = input("\nPorta (ex: /dev/ttyUSB0): ").strip()
            porta = "/dev/ttyUSB0"
            if not porta:
                print("[ERRO] Nome da porta não pode ser vazio")
                continue
                
            baud = input("Baud rate (padrão: 9600): ").strip() or "9600"
            baud = "9600"
            if not baud.isdigit():
                print("[ERRO] Baud rate deve ser numérico")
                continue
                
            gerenciador.conectar(porta, int(baud))
            
        elif opcao == "3":
            tamanho = input("\nQuantidade de bytes a ler (padrão: 1): ").strip() or "1"
            if not tamanho.isdigit():
                print("[ERRO] Quantidade deve ser numérica")
                continue
                
            gerenciador.ler_dados(int(tamanho))
            
        elif opcao == "4":
            dados = input("\nDados a enviar: ").strip()
            print(f"tamanho dados {len(dados)}")
            
            if not dados:
                print("[ERRO] Dados não podem ser vazios")
                continue
        
            try:
                # Se for um único dígito (0-9)
                if len(dados) == 1 and dados.isdigit():
                    valor_numerico = int(dados)
                    print(f"Valor numérico: {valor_numerico}")
                # Se for um número maior
                else:
                    valor_numerico = int(dados)
                    
                gerenciador.escrever_dados(valor_numerico)
        
            except ValueError:
                print("[ERRO] Os dados devem ser um número válido")
            
        elif opcao == "5":
            gerenciador.desconectar()
            
        elif opcao == "0":
            gerenciador.desconectar()
            print("\nEncerrando programa...")
            break
            
        else:
            print("\n[ERRO] Opção inválida!")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
