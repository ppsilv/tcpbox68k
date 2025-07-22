        ORG     $00000000       ; Vetor de reset (obrigatório!)
        DC.L    $00008000       ; SP inicial (exemplo: pilha em 0x8000)
        DC.L    MAIN            ; PC inicial (ponto de entrada do programa)

        ; Outros vetores de exceção (opcional)
        DC.L    ERROR_HANDLER   ; Bus Error
        DC.L    ERROR_HANDLER   ; Address Error
        ; ... (pode preencher com 0xFFFFFFFF se não for usar)

MAIN:
        ; --- Configuração inicial ---
        MOVE.L  #$0007FFFF,A7   ; Inicializa SP novamente (redundante)

        MOVE.L  #$00080000,A0   ; Endereço base da RAM
        MOVE.L  #$A5A5A5A5,D0   ; Padrão de teste

        ; Escreve na RAM
        MOVE.L  D0,(A0)

        ; Lê de volta
        MOVE.L  (A0),D1

        ; Verifica se D1 == D0
        CMP.L   D0,D1
        BNE     MEM_ERROR           ; Se ≠, pula para tratamento de erro

LOOP:
        ; --- Seu código principal ---
        MOVE.W  #$FF00,D0       ; Ativa todos os LEDs (D8-D15 = 0xFF)
        MOVE.W  D0,$2000        ; Escreve no barramento (word access)

        ; Delay loop (ajuste conforme clock)
        move.l  #500000,d3
DELAY:
        subq.l  #1,d3
        bne     DELAY

        MOVE.W  #$0000,D0       ; Ativa todos os LEDs (D8-D15 = 0xFF)
        MOVE.W  D0,$2000        ; Escreve no barramento (word access)

        ; Delay loop (ajuste conforme clock)
        move.l  #500000,d3
DELAY1:
        subq.l  #1,d3
        bne     DELAY1



        BRA     LOOP            ; Loop infinito

ERROR_HANDLER:
        MOVE.W  #$AA00,$2000      ; Padrão de erro nos LEDs
        BRA     ERROR_HANDLER

MEM_ERROR:
        ; --- Seu código principal ---
        MOVE.W  #$FF00,D0       ; Ativa todos os LEDs (D8-D15 = 0xFF)
        MOVE.W  D0,$2000        ; Escreve no barramento (word access)

        ; Delay loop (ajuste conforme clock)
        move.l  #50000,d3
DELAY3:
        subq.l  #1,d3
        bne     DELAY3

        MOVE.W  #$0000,D0       ; Ativa todos os LEDs (D8-D15 = 0xFF)
        MOVE.W  D0,$2000        ; Escreve no barramento (word access)

        ; Delay loop (ajuste conforme clock)
        move.l  #50000,d3
DELAY4:
        subq.l  #1,d3
        bne     DELAY4
        BRA     MEM_ERROR
