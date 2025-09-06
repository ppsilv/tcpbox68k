        ORG     $00000000
        DC.L    $00100000       ;SP inicial
        DC.L    MAIN            ;PC inicial

;# Clock frequency in Hz
F_CPU           equ 12000000
;# Serial baud rate
BAUD            equ 9600
UART            equ $2000
; register offsets
RHR             equ 0   ; receive holding register (read)
THR             equ 0   ; transmit holding register (write)
IER             equ 2   ; interrupt enable register
ISR             equ 4   ; interrupt status register (read)
FCR             equ 4   ; FIFO control register (write)
LCR             equ 6   ; line control register
MCR             equ 8   ; modem control register
LSR             equ 10  ; line status register
MSR             equ 12  ; modem status register
SPR             equ 14  ; scratchpad register (reserved for system use)
DLL             equ 0   ; divisor latch LSB
DLM             equ 2   ; divisor latch MSB
; aliases for register names (used by different manufacturers)
RBR             equ RHR ; receive buffer register
IIR             equ ISR ; interrupt identification register
SCR             equ SPR ; scratch register

BAUD_DIV        equ     (((F_CPU*10)/(16*BAUD))+5)/10 ; compute one extra decimal place and round
BAUD_DIV_L      equ     (BAUD_DIV&$FF)
BAUD_DIV_U      equ     ((BAUD_DIV>>8)&$FF)

MAIN:
        MOVE.L  #$80000,A0      ;Início da RAM
        MOVE.L  #$FFFFF,A1      ;Fim da RAM
        MOVE.W  #$0000,D5       ;D5=0 (sem erro)
        MOVE.L  #$A5A5A5A5,D0
        MOVE.L  $7FFFC,A0
        MOVE.L  D0,(A0)
        MOVE.L  #$80000,A0      ;Início da RAM

        move.l  #500000,d3
DELAY_INIT:
        subq.l  #1,d3
        bne     DELAY_INIT


uartinit:
        lea.l   UART,a1
        move.b  #%00001101,FCR(a1)      ; enable FIFO
        move.b  #%10000011,LCR(a1)      ; 8 data bits, no parity, 1 stop bit, DLAB=1
        move.b  #BAUD_DIV_L,DLL(a1)     ; set divisor latch low byte
        move.b  #BAUD_DIV_U,DLM(a1)     ; set divisor latch high byte
        bclr.b  #7,LCR(a1)              ; disable divisor latch
        clr.b   SCR(a1)                 ; clear the scratch register

sendchars:
        move.b  #$41,D0
.1:     btst.b  #5,LSR(a1)      ; wait until transmit holding register is empty
        beq     .1
        move.b  d0,THR(a1)      ; transmit byte

        move.b  #$42,D0
.2:     btst.b  #5,LSR(a1)      ; wait until transmit holding register is empty
        beq     .2
        move.b  d0,THR(a1)      ; transmit byte

        move.b  #$43,D0
.3:     btst.b  #5,LSR(a1)      ; wait until transmit holding register is empty
        beq     .3
        move.b  d0,THR(a1)      ; transmit byte

        move.b  #$44,D0
.4:     btst.b  #5,LSR(a1)      ; wait until transmit holding register is empty
        beq     .4
        move.b  d0,THR(a1)      ; transmit byte

        JSR     COUNTER
mainprogram:
        JSR     WARN
        BRA     TEST_LED
        BRA     pisca
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
        MOVE.W  D5,$2400        ;Ativa LEDs (byte high)
        BRA     *               ;Trava em caso de erro

SUCCESS:
        MOVE.W  #$5500,D5       ;Padrão de sucesso (LEDs alternados)
        MOVE.W  D5,$2400        ;Exibe nos LEDs
        BRA     *               ;Trava após teste completo

WARN:
        MOVE.W  #$FFFF,D5       ;Sinaliza erro (LEDs acesos)
        MOVE.W  D5,$2400        ;Ativa LEDs (byte high)
        RTS

TEST_LED:
    ; --- Teste do registrador Scratch da UART (0x2007) ---
        lea.l   UART,A1
        ;move.w  #$00A5,D0

        move.b  #$A5,SCR(A1)

;        move.l  #300000,d3
;.DELAY1:
;        subq.l  #1,d3
;        bne     .DELAY1

        lea.l   UART,A1
        MOVE.W  #$0500,D1
        MOVE.b  SCR(A1),D1  ; Lê de volta o registrador Scratch

        ROL.W #8,D1
        MOVE.W  D1,$2400
TERMINO:
        BRA TERMINO


        ;BRA TEST_LED

        ; --- Compara escrita vs leitura ---
        AND   #$00FF,D1


        CMP   #$A5,D1     ; D1 == D0?
        BEQ    pisca ; SUCESSO    ; Se igual, vai para SUCESSO


        BRA     pisca1 ; ATUALIZA_LEDS

SUCESSO:
        ; --- SUCESSO: Padrão 0x47 nos LEDs ---
        MOVE.W  #$4700,D2

ATUALIZA_LEDS:
        ; --- Escreve nos LEDs (endereço 0x2400, byte mais significativo) ---
        MOVE.W  D2,$2400

FIM:
        BRA     FIM        ; Loop infinito (ou reinicia se preferir)

pisca:
        MOVE.W  #$FF00,D0       ; Ativa todos os LEDs (D8-D15 = 0xFF)
        MOVE.W  D0,$2400        ; Escreve no barramento (word access)
        ; Delay loop (ajuste conforme clock)
        move.l  #500000,d3
DELAY:
        subq.l  #1,d3
        bne     DELAY

        MOVE.W  #$0000,D0       ; desAtiva todos os LEDs (D8-D15 = 0xFF)
        MOVE.W  D0,$2400        ; Escreve no barramento (word access)

        ; Delay loop (ajuste conforme clock)
        move.l  #500000,d3
DELAY1:
        subq.l  #1,d3
        bne     DELAY1
        BRA     pisca

pisca1:
        MOVE.W  #$AA00,D0       ; Ativa todos os LEDs (D8-D15 = 0xFF)
        MOVE.W  D0,$2400        ; Escreve no barramento (word access)
        ; Delay loop (ajuste conforme clock)
        move.l  #100000,d3
.DELAY:
        subq.l  #1,d3
        bne     .DELAY

        MOVE.W  #$5500,D0       ; desAtiva todos os LEDs (D8-D15 = 0xFF)
        MOVE.W  D0,$2400        ; Escreve no barramento (word access)

        ; Delay loop (ajuste conforme clock)
        move.l  #150000,d3
.DELAY1:
        subq.l  #1,d3
        bne     .DELAY1
        BRA     pisca1


COUNTER:
        MOVE.B  #$00,D0

.LOOP:
        lea.l   UART,A1
        move.b  D0,SCR(A1)

        move.l  #500000,D3
.DELAY1:
        subq.l  #1,D3
        bne     .DELAY1

        MOVE.b  SCR(A1),D1  ; Lê de volta o registrador Scratch
        ROL.W   #8,D1
        MOVE.W  D1,$2400
        ADD     #1,D0
        BRA     .LOOP
