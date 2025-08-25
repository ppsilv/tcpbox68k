;vasmm68k_mot -Fbin -L npisca.lst  -o npisca.bin nov_pisca.s
    ORG     $00081530          ; Endereço de carga do código
    ALIGN 4
NOVO_PISCA:
        MOVE.L  #$0010,D1
.LOOP_PISCA:
        MOVE.W  #$FF00,D0
        MOVE.W  D0,$2400
        JSR     .NEW_DELAY

        MOVE.W  #$0000,D0
        MOVE.W  D0,$2400
        JSR     .NEW_DELAY
        SUB.B   #$01,D1
        BNE     .LOOP_PISCA
        RTS

.NEW_DELAY:
        MOVE.L  #500000,D3
.DELAY1:
        SUBQ.L  #1,D3
        BNE     .DELAY1
        RTS
