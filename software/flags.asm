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

; --- Macro para Setar Flag ---
SET_FLAG   MACRO \flag
    BSET    #\flag,MEU_FLAGS
    ENDM

; --- Macro para Testar Flag ---
TEST_FLAG  MACRO \flag,\rotulo
    BTST    #\flag,MEU_FLAGS
    BNE     \rotulo
    ENDM

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

; --- Macro para Enfileirar ---
ENQUEUE MACRO \valor
    TST.B   (FIFO_PONTEIRO_ENTRADA)+
    BNE     FIFO_CHEIA          ; Se bit 0=1 (cheio)
    MOVE.B  \valor,(A0)+        ; Adiciona dado
    BCLR    #FIFO_VAZIO,FIFO_FLAGS  ; Já não está vazio
    ENDM


📌 Dica de Ouro
Combine com tabelas de jump para criar máquinas de estado:

asm
    MOVEQ   #0,D0
    MOVE.B  ESTADO_ATUAL,D0
    LSL.W   #2,D0               ; x4 (cada entrada é 4 bytes)
    JMP     ([TABELA_ESTADOS.L,D0.W])

TABELA_ESTADOS:
    DC.L    ESTADO_0,ESTADO_1,ESTADO_2  ; Ponteiros para rotinas


🔧 Faça Você Mesmo
Que tal uma macro WAIT_FLAG que espera um flag com timeout?

asm
WAIT_FLAG MACRO \flag,\timeout,\timeout_rotulo
    MOVE.W  #\timeout,D7
.LOOP:
    BTST    #\flag,MEU_FLAGS
    BNE     .SAI
    DBRA    D7,.LOOP
    BRA     \timeout_rotulo     ; Timeout atingido
.SAI:
    ENDM



