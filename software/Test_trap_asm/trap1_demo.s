; ==================================================
; Programa demonstração do TRAP #1 para vasmm68k_mot
; Funcões: CCONIN (ler char) e CCONOUT (escrever char)
; ==================================================

    section code
    BRA     start

    include "rom_routines.inc"
; ==================================================
; Programa principal
; ==================================================
start:
    LEA     mensagem,A0    ; Coloca endereço da mensagem na pilha
    BSR     imprimir_string    ; Chama rotina de impressão

    LEA     pergunta,A0    ; Pergunta para usuário
    BSR     imprimir_string

; Lê caractere do teclado
ler_caractere:
    MOVE.W  #1,D0              ; Função CCONIN (ler caractere)
    TRAP    #1                 ; Chama TRAP #1
    CMP.B   #27,D0             ; Verifica se é ESC (ASCII 27)
    BEQ     fim_programa       ; Se for ESC, termina

; Mostra o caractere lido
    MOVE.L  D0,-(SP)
    LEA     eco,A0             ; Mensagem "Você digitou: "
    BSR     imprimir_string
    MOVE.L  (SP)+,D0
    BSR     imprimir_caractere ; Imprime o caractere
    LEA     nova_linha,A0  ; Nova linha
    BSR     imprimir_string
    BRA     ler_caractere      ; Repete

; Finaliza programa
fim_programa:
    JMP     MenuLoop

; ==================================================
; Rotinas de apoio
; ==================================================

; Imprimir string (endereço em pilha)
imprimir_string:
    MOVE.L  A0,-(SP)           ; Salva A0 na Pinha
imprimir_loop:
    MOVE.B  (A0)+,D1           ; Pega próximo caractere
    CMP.B   #0,D1
    BEQ     imprimir_fim       ; Se for zero, termina
    MOVE.W  #2,D0              ; Função CCONOUT
    TRAP    #1                 ; Chama TRAP #1
    BRA     imprimir_loop
imprimir_fim:
    MOVE.L  (SP)+,A0           ; Restaura A0 da Pinha
    RTS

; Imprimir caractere (caractere em pilha)
imprimir_caractere:
    MOVE.L  D0,D1              ; Pega caractere
    MOVE.W  #2,d0              ; Função CCONOUT
    TRAP    #1                 ; Chama TRAP #1
    RTS

; ==================================================
; Dados do programa
; ==================================================
    section data

mensagem:
    dc.b    "Demo do TRAP #1 - MC68000",13,10
    dc.b    "Funcoes GEMDOS: CCONIN/CCONOUT",13,10,0

pergunta:
    dc.b    "Digite um caractere (ESC para sair): ",0

eco:
    dc.b    "Voce digitou: ",0

nova_linha:
    dc.b    13,10,0

    end
