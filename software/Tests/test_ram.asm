        ORG     $00000000
        DC.L    $000FFFFF       ; SP
        DC.L    MAIN            ; PC

MAIN:
        MOVE.L  #$0007FFFF,A7   ; Inicializa o Stack Pointer (SP = A7)
        LEA     RAM_START,A0
        MOVE.L  #RAM_END,A1
        MOVE.L  #$10000,D4
        MOVE.W  #$0100,D5

        ; ---- Teste real da RAM ----
        MOVE.L  #$A5A5A5A5,D0
        MOVE.L  D0,$80000         ; Escreve
        ;CMP.L   ($0007FFFF),D0         ; Lê e compara
        ;BNE     MEM_ERROR           ; Se ≠, vai para erro

        ;JSR     MOSTRA_D5_2
TEST_LOOP:
        ; ---- Teste real da RAM ----
        MOVE.L  #$A5A5A5A5,D0
        MOVE.L  D0,(A0)         ; Escreve
        CMP.L   (A0),D0         ; Lê e compara
        BNE     MEM_ERROR           ; Se ≠, vai para erro
        ; ---- Próximo endereço ----
        ADDA.L  #4,A0           ; Avança 4 bytes
        ;Verifica se é hora de ascender um led
        ; --- Comparação segura ---
        MOVE.L  A0,D7          ; Copia A0 para D7 (se necessário)
        CMP.L   D7,D4          ; Compara D4 com D7 (antigo A0)
        BCS     MOSTRA_D5   ;.call_sub       ; Se D4 < D7 (sem sinal)
;        BRA     .skip

;.call_sub:
;        JSR     MOSTRA_D5       ; Chama subrotina

skip:
        ; --- Verificação do loop ---
        CMPA.L  A1,A0          ; A0 chegou ao fim (A1)?
        BLO     TEST_LOOP        ; Se A0 < A1, continua
        BRA     LOOP_FINAL

MOSTRA_D5:
        ; --- Escrita segura na memória ---
        MOVE.W  D5,$2000     ; *Verifique se $2000 é válido!*
        ADD.W   #$0100,D5
        BRA     skip
        ;RTS
MOSTRA_D5_2:
        ; --- Escrita segura na memória ---
        MOVE.W  #$0100,$2000     ; *Verifique se $2000 é válido!*
        RTS
        ;USA D3
        ; --- PISCA OS LEDS ---
        ; Delay loop (ajuste conforme clock)
        ;MOVE.W  #$A500,D0       ; Ativa todos os LEDs (D8-D15 = 0xFF)
        MOVE.W  #$A500,$2000        ; Escreve no barramento (word access)
        move.l  #125000,D3
DELAY_00:
        subq.l  #1,D3
        bne     DELAY_00
        ;MOVE.W  #$0000,D0       ; Ativa todos os LEDs (D8-D15 = 0xFF)
        MOVE.W  #$0000,$2000        ; Escreve no barramento (word access)
        ; Delay loop (ajuste conforme clock)
        move.l  #125000,D3
DELAY_01:
        subq.l  #1,D3
        bne     DELAY_01


        ;BRA     TEST_LOOP

LOOP_FINAL:
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
        BRA     LOOP_FINAL            ; Loop infinito
MEM_ERROR:
        ; --- Seu código principal ---
        MOVE.W  #$0A00,D0       ; Ativa todos os LEDs (D8-D15 = 0xFF)
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

; Macro para "JSR condicional se D0 < D1 (unsigned)"
JSR_IF_D0_BELOW_D1_UNSIGNED MACRO
    CMP.L   D1, D0
    BCC     .skip\@      ; Se D0 >= D1, pula
;    JSR     SUBA
.skip\@:
    ENDM

RAM_START   EQU $00080000
RAM_END     EQU $000DFFFF
