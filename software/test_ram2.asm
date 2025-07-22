        ORG     $00000000
        DC.L    $00100000       ;SP inicial
        DC.L    MAIN            ;PC inicial

MAIN:
        MOVE.L  #$80000,A0      ;Início da RAM
        MOVE.L  #$FFFFF,A1      ;Fim da RAM
        MOVE.W  #$0000,D5       ;D5=0 (sem erro)
        MOVE.L  #$A5A5A5A5,D0
        MOVE.L  $7FFFC,A0
        MOVE.L  D0,(A0)
        MOVE.L  #$80000,A0      ;Início da RAM

        JSR     WARN

TEST_LOOP:
        MOVE.L  #$A5A5A5A5,D0   ;Padrão 1
        MOVE.L  D0,(A0)         ;Escreve na RAM
        CMP.L   (A0),D0         ;Compara
        BNE     ERROR           ;Se diferente, erro
        MOVE.L  #$5A5A5A5A,D0   ;Padrão 2
        MOVE.L  D0,(A0)         ;Escreve novamente
        CMP.L   (A0),D0         ;Compara
        BNE     ERROR           ;Se diferente, erro
        ADDQ.L  #4,A0           ;Próximo endereço (4 bytes)
        CMPA.L  A1,A0           ;Chegou ao fim?
        BLS     TEST_LOOP        ;Se não, continua
        BRA     SUCCESS         ;Se passou, fim sem erros

ERROR:
        MOVE.W  #$FF00,D5       ;Sinaliza erro (LEDs acesos)
        MOVE.W  D5,$2000        ;Ativa LEDs (byte high)
        BRA     *               ;Trava em caso de erro

SUCCESS:
        MOVE.W  #$5500,D5       ;Padrão de sucesso (LEDs alternados)
        MOVE.W  D5,$2000        ;Exibe nos LEDs
        BRA     *               ;Trava após teste completo

WARN:
        MOVE.W  #$AA00,D5       ;Sinaliza erro (LEDs acesos)
        MOVE.W  D5,$2000        ;Ativa LEDs (byte high)
        RTS
