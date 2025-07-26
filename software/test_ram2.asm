        SECTION code,CODE
        ORG     $00000000
        DC.L    $00100000       ;SP inicial
        DC.L    MAIN            ;PC inicial

;Term vt-102 cursor positioning \033[0;0H

;# Clock frequency in Hz
F_CPU           equ 16000000
;# Serial baud rate
BAUD            equ 9600
UART            equ $2300
UART_BASE       equ $2300
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
; aliases for register names (used by different manufacturers)cd ..
RBR             equ RHR ; receive buffer register
IIR             equ ISR ; interrupt identification register
SCR             equ SPR ; scratch register

BAUD_DIV        equ     (((F_CPU*10)/(16*BAUD))+5)/10 ; compute one extra decimal place and round
BAUD_DIV_L      equ     (BAUD_DIV&$FF)
BAUD_DIV_U      equ     ((BAUD_DIV>>8)&$FF)

RAM_START     EQU     $080000      ; Início da RAM disponível
STACK_INIT    EQU     $100000      ; Topo da pilha (ajuste conforme necessário)
;Variables
UART_CURRENT EQU $81000
BAUD_TABLE   EQU $81004         ; BAUD_DIV_L em $81004  ; BAUD_DIV_U em $81006
RX_BUFFER    EQU $81016
TX_BUFFER    EQU $81124




;isso é provisório tem que por na ram
;CurrentUART equ $2300 JÁ MUDEI
        ;ORG $00001000
MAIN:
        move.l  #500000,d3
DELAY_INIT:
        subq.l  #1,d3
        bne     DELAY_INIT

        ; Inicializa variável
        MOVE.L  #$2300,UART_CURRENT


        JSR     UART_Init

        MOVE.B  #$50,D0
        JSR     UART_WriteChar

        JSR     new_line

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


        JSR     new_line

        MOVE.W  #$BEEF,D0
        JSR     PrintHexFast

        JSR     new_line

        JSR     COUNTER


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

; ----------------------------------------------------------------------
; Rotinas de E/S da UART
; ----------------------------------------------------------------------

; Inicialização da UART
UART_Init0:
    MOVE.W  #9600,D0    ; Para 9600 bauds
    BSR     CalcBaudDiv
    move.l  UART_CURRENT,a1
    move.b  #%00001101,FCR(a1)      ; enable FIFO
    move.b  #%10000011,LCR(a1)      ; 8 data bits, no parity, 1 stop bit, DLAB=1
    LEA     BAUD_TABLE,A0
    MOVE.B  (A0)+,D0
    move.b  D0,DLL(a1)     ; set divisor latch low byte
    MOVE.B  (A0),D0
    move.b  D0,DLM(a1)     ; set divisor latch high byte
    bclr.b  #7,LCR(a1)              ; disable divisor latch
    clr.b   SCR(a1)                 ; clear the scratch register
    RTS


UART_Init:
    move.l   UART_CURRENT,a1
    move.b  #%00001101,FCR(a1)      ; enable FIFO
    move.b  #%10000011,LCR(a1)      ; 8 data bits, no parity, 1 stop bit, DLAB=1
    move.b  #BAUD_DIV_L,DLL(a1)     ; set divisor latch low byte
    move.b  #BAUD_DIV_U,DLM(a1)     ; set divisor latch high byte
    bclr.b  #7,LCR(a1)              ; disable divisor latch
    clr.b   SCR(a1)                 ; clear the scratch register
    RTS

    ; Escreve caractere (D0.B)
UART_WriteChar:
    move.l   UART_CURRENT,A0
.WaitTx:
    BTST.B  #5,LSR(A0)      ; wait until transmit holding register is empty
    BEQ     .WaitTx
    MOVE.B  D0,THR(A0)      ; transmit byte
    RTS


; Lê caractere (retorna em D0)
UART_ReadChar:
    move.l   UART_CURRENT,A0
.WaitRx:
    BTST.B  #0,LSR(A0)        ; RX ready?
    BEQ     .WaitRx
    MOVE.B  RHR(A0),D0
    RTS

; ----------------------------------------------------------------------
; Constantes
; ----------------------------------------------------------------------
;F_CPU       EQU 16000000       ; Clock do CPU (16MHz)
;BAUD_TABLE  EQU $70000         ; Endereço base na RAM para armazenar divisores
                              ; BAUD_DIV_L em $70000
                              ; BAUD_DIV_U em $70001

; ----------------------------------------------------------------------
; Rotina: Calcula e armazena divisor de baud rate
; Entrada:
;   D0.W - BAUD rate desejado (ex: 9600)
; Saída:
;   BAUD_DIV_L e BAUD_DIV_U armazenados na RAM
; ----------------------------------------------------------------------
CalcBaudDiv:
    LINK    A6,#-4            ; Cria frame de stack (4 bytes locais)

    ; 1. Calcula BAUD_DIV = (((F_CPU*10)/(16*BAUD))+5)/10
    MOVE.L  #F_CPU,D1         ; D1 = F_CPU
    MULU.W  #10,D1            ; D1 = F_CPU*10

    MOVE.W  D0,D2             ; D2 = BAUD
    LSL.W   #4,D2             ; D2 = 16*BAUD (shift left 4 bits)

    DIVU.W  D2,D1             ; D1 = (F_CPU*10)/(16*BAUD)
    ADD.W   #5,D1             ; +5 para arredondar
    DIVU.W  #10,D1            ; /10

    ; 2. Separa em parte alta e baixa
    MOVE.W  D1,D0             ; D0 = BAUD_DIV completo
    ANDI.W  #$FF,D0           ; D0 = BAUD_DIV_L (parte baixa)
    MOVE.W  D1,D2
    LSR.W   #8,D2             ; D2 = BAUD_DIV_U (parte alta)

    ; 3. Armazena na RAM
    LEA     BAUD_TABLE,A0
    MOVE.B  D0,(A0)+          ; Armazena BAUD_DIV_L
    MOVE.B  D2,(A0)           ; Armazena BAUD_DIV_U

    UNLK    A6                ; Restaura frame de stack
    RTS

new_line:
        MOVE.B  #10,D0
        JSR     UART_WriteChar
        MOVE.B  #13,D0
        JSR     UART_WriteChar
        RTS

; Versão compacta sem stack frame
PrintHexFast:
    MOVE.L  D2,-(SP)          ; Salva D2
    MOVE.L  D0,-(SP)          ; Salva D0 original
    MOVEQ   #7,D2             ; 8 dígitos (contador)

.Loop:
    MOVE.L  (SP),D0           ; Recupera valor original
    ROL.L   #4,D0             ; Pega próximo nibble
    MOVE.L  D0,(SP)           ; Armazena valor rotacionado
    ANDI.B  #$F,D0            ; Isola nibble

    CMP.B   #9,D0
    BLS     .Digit
    ADD.B   #7,D0             ; Ajuste para A-F
.Digit:
    ADD.B   #'0',D0           ; Converte para ASCII
    JSR     UART_WriteChar    ; Envia caractere

    DBRA    D2,.Loop          ; Repete para todos dígitos

    ADDQ.L  #4,SP             ; Remove valor salvo
    MOVE.L  (SP)+,D2          ; Restaura D2
    RTS

; ----------------------------------------------------------------------
; PrintHex - Imprime valor hexadecimal no terminal
; Entrada:
;   D0.L = Valor a ser impresso (32 bits)
;   D1.W = Número de dígitos (1-8)
; ----------------------------------------------------------------------
PrintHex:
    LINK    A6,#-8            ; Reserva espaço na pilha
    MOVE.L  D2,-(SP)          ; Salva D2
    MOVE.L  D0,-4(A6)         ; Guarda o valor original
    MOVE.W  D1,-6(A6)         ; Guarda contador de dígitos

    ; Ajusta para começar pelo dígito mais significativo
    LSL.W   #2,D1             ; Multiplica por 4 (bits por dígito)
    SUBQ.W  #4,D1             ; Ajuste inicial

.PrintLoop:
    MOVE.L  -4(A6),D0         ; Recupera valor
    MOVE.W  D1,D2             ; Posição do nibble
    ROL.L   D2,D0             ; Rola para colocar nibble nos bits 31-28
    ANDI.L  #$F,D0            ; Isola o nibble (4 bits)

    ; Converte para ASCII
    CMP.B   #9,D0
    BLS     .Decimal
    ADD.B   #7,D0             ; Ajuste para A-F
.Decimal:
    ADD.B   #'0',D0           ; Converte para caractere

    ; Imprime caractere
    JSR     UART_WriteChar    ; Sua rotina de envio UART

    SUBQ.W  #4,D1             ; Próximo nibble
    BPL     .PrintLoop        ; Repete até todos os dígitos

    ; Espaço final para separação
    MOVE.B  #' ',D0
    JSR     UART_WriteChar

    MOVE.L  (SP)+,D2          ; Restaura D2
    UNLK    A6                ; Restaura frame
    RTS
; ----------------------------------------------------------------------
; Exemplo de uso:
; ----------------------------------------------------------------------
SetupDivisor:
    MOVE.W  #9600,D0          ; Configura para 9600 bauds
    BSR     CalcBaudDiv

    ; Agora pode acessar os valores na RAM:
    LEA     BAUD_TABLE,A0
    MOVE.B  (A0)+,D0          ; D0 = BAUD_DIV_L
    MOVE.B  (A0),D1           ; D1 = BAUD_DIV_U

    ; (Aqui você configuraria os registradores da UART)
    RTS
    SECTION data,DATA
     DC.B "Valores",0

    SECTION bss,BSS
    ORG     $81000               ; Área para variáveis
CurrentUART:   DS.L 1
RxBuffer:      DS.B 256
TxBuffer:      DS.B 256
