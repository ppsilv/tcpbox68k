1. Definindo um Local para as Flags
asm
MY_FLAGS    EQU     $1000       ; Endereço de um byte para flags (exemplo)
FLAG_A      EQU     0           ; Bit 0 = Flag A
FLAG_B      EQU     1           ; Bit 1 = Flag B
2. Setar um Bit (Flag = 1)
asm
BSET    #FLAG_A, MY_FLAGS       ; Seta o bit 0 (Flag A = 1)
3. Limpar um Bit (Flag = 0)
asm
BCLR    #FLAG_A, MY_FLAGS       ; Limpa o bit 0 (Flag A = 0)
4. Testar um Bit (Verificar Flag)
asm
BTST    #FLAG_A, MY_FLAGS       ; Testa o bit 0
BNE     FLAG_A_IS_SET           ; Se Flag A = 1, salta
BEQ     FLAG_A_IS_CLEAR         ; Se Flag A = 0, salta

; --- Definição das Flags ---
FLAG_ERRO  EQU  0
FLAG_ATIVO EQU  1
FLAG_DADO  EQU  2



; --- Uso no Código ---
    SET_FLAG FLAG_ATIVO      ; Substitui por BSET #1,MEU_FLAGS
    TEST_FLAG FLAG_ERRO,TRATA_ERRO  ; Pula se FLAG_ERRO=1


    ; --- Macro para "Semáforo" ---
LOCK    MACRO
    BSET    #7,SEMAFORO      ; Bit 7 = Lock
    BNE     LOCK             ; Espera liberar
    ENDM

UNLOCK  MACRO
    BCLR    #7,SEMAFORO
    ENDM

; --- Flags de Eventos ---
EVENTO_TECLA   EQU  0
EVENTO_TIMER   EQU  1

; --- Dispara Evento ---
    BSET    #EVENTO_TECLA,EVENTOS  ; Tecla pressionada

; --- Trata Evento (em loop principal) ---
    BTST    #EVENTO_TECLA,EVENTOS
    BEQ     .SEM_TECLA
    BSR     TRATA_TECLA
    BCLR    #EVENTO_TECLA,EVENTOS  ; Consome evento
.SEM_TECLA:


🛠 Exemplo Avançado: FIFO com Flags
asm
; --- Buffer Circular ---
FIFO_FLAGS EQU  $1000
FIFO_CHEIO EQU  0
FIFO_VAZIO EQU  1




📌 Dica de Ouro
Combine com tabelas de jump para criar máquinas de estado:

asm
    MOVEQ   #0,D0
    MOVE.B  ESTADO_ATUAL,D0
    LSL.W   #2,D0               ; x4 (cada entrada é 4 bytes)
    JMP     ([TABELA_ESTADOS.L,D0.W])

TABELA_ESTADOS:
    DC.L    ESTADO_0,ESTADO_1,ESTADO_2  ; Ponteiros para rotinas




MACROS NO PADRAO NO vasmm68k_mot

asm
; --- Definição das Flags ---
FL_ESC      EQU     0       ; Bit 0 = Flag ESC
minhas_flags DC.B   0       ; Byte para flags

; --- Macro SET_FLAG corrigida ---
SET_FLAG   MACRO
    BSET    #\1,minhas_flags  ; \1 = primeiro argumento (bit)
    ENDM

; --- Macro TEST_FLAG corrigida ---
TEST_FLAG  MACRO
    BTST    #\1,minhas_flags
    ENDM

Uso (agora com sintaxe correta):
asm
    SET_FLAG FL_ESC          ; Seta o bit 0 (FL_ESC=1)
    TEST_FLAG FL_ESC         ; Testa o bit 0 (Z=0 se setado)
    BNE     ESC_PRESSED      ; Se FL_ESC=1, pula


    Aqui está a versão corrigida da macro ENQUEUE para o vasmm68k_mot, seguindo as regras do assembler:

asm
; --- Definições ---
FIFO_FLAGS          EQU     $1000       ; Endereço dos flags da FIFO
FIFO_PONTEIRO_ENTRADA EQU   $1004       ; Endereço do ponteiro de entrada
FIFO_CHEIA          EQU     0           ; Bit 0 = FIFO cheia
FIFO_VAZIO          EQU     1           ; Bit 1 = FIFO vazia

; --- Macro ENQUEUE corrigida ---
ENQUEUE MACRO
    TST.B   (FIFO_PONTEIRO_ENTRADA)+    ; Testa e incrementa ponteiro
    BNE     FIFO_CHEIA                  ; Se FIFO cheia, pula para tratamento
    MOVE.B  \1,(A0)+                   ; Adiciona o valor (passado como \1)
    BCLR    #FIFO_VAZIO,FIFO_FLAGS      ; Marca FIFO como não-vazia
    ENDM
