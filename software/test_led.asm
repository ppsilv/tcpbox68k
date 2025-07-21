        ORG     $00000000
        DC.L    $00880000       ; SP (ignorado sem RAM)
        DC.L    START           ; PC inicial

START:
        ; --- Não use pilha! ---
        ; --- Configuração inicial ---
        MOVE.B  #$FF,D0        ; Todos LEDs acesos inicialmente
        MOVE.B  D0,$2000        ; Escreve nos LEDs

MAIN_LOOP:
        ; --- Padrão 1: Todos apagados ---
        MOVE.B  #$00,D0
        MOVE.B  D0,$2000        ; Byte LOW apenas!

        ; Delay preciso (~100ms)
        MOVE.L  #1600000,D1     ; Ajustado para 16MHz
DELAY_OFF:
        SUBQ.L  #1,D1
        BNE     DELAY_OFF

        ; --- Padrão 2: Todos acesos ---
        MOVE.B  #$FF,D0
        MOVE.B  D0,$2000

        ; Delay igual
        MOVE.L  #1600000,D1
DELAY_ON:
        SUBQ.L  #1,D1
        BNE     DELAY_ON

        BRA     MAIN_LOOP
        END
