; CONFIGURAÇÃO DA UART E INTERRUPÇÕES
SERIAL_INIT:
    ; Configura baud rate
    MOVE.B  #$80,ACR(A1)    ; Access Divisor Latch
    MOVE.B  #4,DLL(A1)      ; 230400 baud
    MOVE.B  #0,DLM(A1)
    MOVE.B  #$03,ACR(A1)    ; 8N1

    ; Configura interrupções
    MOVE.B  #$01,IER(A1)    ; Habilita Received Data Available interrupt
    RTS

; VETOR DE INTERRUPÇÃO (exemplo para nível 2)
    ORG     $68             ; Vetor da interrupção nível 2
    DC.L    SERIAL_ISR      ; Endereço da rotina de serviço

SERIAL_ISR:
    MOVEM.L D0-D1/A0-A1,-(SP) ; Salva registradores

    MOVE.L  #UART_BASE,A1   ; Endereço da UART
    BTST    #0,IIR(A1)      ; Verifica se é interrupção de recepção
    BEQ.S   .FIM_ISR        ; Se não for, sai

    MOVE.B  RBR(A1),D0      ; Lê byte recebido
    BSR     PROCESSAR_BYTE  ; Sua rotina de processamento

.FIM_ISR:
    MOVEM.L (SP)+,D0-D1/A0-A1 ; Restaura registradores
    RTE
