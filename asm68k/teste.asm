        ORG    $1000           ; Começo do programa

Start:
        MOVE.B #0, D0          ; Inicia em 0

Loop:
        MOVE.B D0, $FFFFFC21   ; Exibe no "display" (endereço fictício do Easy68K)
        ADD.B  #1, D0          ; Incrementa
        CMP.B  #10, D0         ; Chegou em 10?
        BNE    Loop            ; Se não, repete
        MOVE.B #0, D0          ; Reseta para 0
        BRA    Loop            ; Loop infinito

Delay:                         ; Subrotina de delay
        MOVE.L #100000, D1
DelayLoop:
        SUB.L  #1, D1
        BNE    DelayLoop
        RTS

        END    Start

