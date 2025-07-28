; ======================================================================
; MC68000 Serial Monitor
; Hardware:
; - CPU: MC68000 @ 16MHz
; - UART: Endereços $2000, $2100, $2200 ou $2300
; - RAM: 512KB a partir de $80000
; Funcionalidades:
; 1. Selecionar UART
; 2. Configurar Baud Rate
; 3. Carregar programa via serial (PC → RAM)
; 4. Gravar programa manualmente
; 5. Executar programa na RAM
; ======================================================================
; ----------------------------------------------------------------------
; Vetor de Reset
; ----------------------------------------------------------------------
    ORG     $0
    DC.L    STACK_INIT           ; Pilha inicial (SP)
    DC.L    Main

; ----------------------------------------------------------------------
; Constantes Hardware
; ----------------------------------------------------------------------
;# Clock frequency in Hz
F_CPU           equ 16000000
;# Serial baud rate
BAUD            equ 9600
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

RAM_START     EQU     $80000      ; Início da RAM disponível
STACK_INIT    EQU     $A0000      ; Topo da pilha (ajuste conforme necessário)

                ; Ponto de entrada (PC)



; ----------------------------------------------------------------------
; Código Principal
; ----------------------------------------------------------------------
Main:
        move.l  #500000,d3
DELAY_INIT:
        subq.l  #1,d3
        bne     DELAY_INIT

        lea.l   UART_BASE,a1
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

COUNTER:
        MOVE.B  #$00,D0

.LOOP:
        lea.l   UART_BASE,A1
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





    ; Inicializa sistema
    MOVE.L  #UART_BASE,CurrentUART
    JSR     UART_Init

    ; Limpa tela e exibe mensagem inicial
    JSR     UART_ClearScreen
    LEA     WelcomeMsg,A0
    JSR     UART_WriteString

; Loop principal do menu
MenuLoop:
    LEA     MenuText,A0
    JSR     UART_WriteString

    ; Lê seleção do usuário
    JSR     UART_ReadChar

    ; Processa opção selecionada
    CMP.B   #'1',D0
    BEQ     SelectUART
    CMP.B   #'2',D0
    BEQ     SetBaudRate
    CMP.B   #'3',D0
    BEQ     LoadProgram
    CMP.B   #'4',D0
    BEQ     WriteProgram
    CMP.B   #'5',D0
    BEQ     RunProgram

    BRA     MenuLoop            ; Opção inválida, repete menu

; ----------------------------------------------------------------------
; Subrotinas do Menu
; ----------------------------------------------------------------------

; 1. Seleciona UART
SelectUART:
    LEA     UARTPrompt,A0
    JSR     UART_WriteString
    JSR     UART_ReadHex        ; Lê endereço da UART
    MOVE.L  D0,CurrentUART      ; Atualiza UART atual
    JSR     UART_Init           ; Reinicializa UART
    RTS

; 2. Configura Baud Rate
SetBaudRate:
    ;LEA     BaudPrompt,A0
    ;JSR     UART_WriteString
    ;JSR     UART_ReadHex        ; Lê valor do baud rate
    ;MOVE.L  CurrentUART,A0
    ;MOVE.B  D0,(UART_BAUD,A0)   ; Configura registrador
    RTS

; 3. Carrega programa via serial
LoadProgram:
    LEA     LoadPrompt,A0
    JSR     UART_WriteString
    JSR     UART_ReadHex        ; Lê endereço de destino
    MOVE.L  D0,A1               ; A1 = ponteiro para RAM

    ; Protocolo: [Tamanho(4B)][Dados...]
    JSR     UART_ReadLong       ; Lê tamanho (32 bits)
    MOVE.L  D0,D1               ; D1 = contador de bytes

.LoadLoop:
    JSR     UART_ReadByte       ; Lê byte
    MOVE.B  D0,(A1)+            ; Armazena na RAM
    SUBQ.L  #1,D1               ; Decrementa contador
    BNE     .LoadLoop           ; Continua até terminar

    LEA     LoadDoneMsg,A0
    JSR     UART_WriteString
    RTS

; 4. Grava programa manualmente (hex)
WriteProgram:
    LEA     WritePrompt,A0
    JSR     UART_WriteString
    JSR     UART_ReadHex        ; Lê endereço
    MOVE.L  D0,A1               ; A1 = ponteiro

    LEA     WriteSizePrompt,A0
    JSR     UART_WriteString
    JSR     UART_ReadHex        ; Lê quantidade de bytes
    MOVE.L  D0,D1               ; D1 = contador

.WriteLoop:
    JSR     UART_ReadByte       ; Lê byte
    MOVE.B  D0,(A1)+            ; Armazena
    SUBQ.L  #1,D1
    BNE     .WriteLoop

    LEA     WriteDoneMsg,A0
    JSR     UART_WriteString
    RTS

; 5. Executa programa na RAM
RunProgram:
    LEA     RunPrompt,A0
    JSR     UART_WriteString
    JSR     UART_ReadHex        ; Lê endereço
    MOVE.L  D0,A0
    JSR     (A0)                ; Chama subrotina
    RTS

; ----------------------------------------------------------------------
; Rotinas de E/S da UART
; ----------------------------------------------------------------------

; Inicialização da UART
UART_Init:
    lea.l   CurrentUART,a1
    move.b  #%00001101,FCR(a1)      ; enable FIFO
    move.b  #%10000011,LCR(a1)      ; 8 data bits, no parity, 1 stop bit, DLAB=1
    move.b  #BAUD_DIV_L,DLL(a1)     ; set divisor latch low byte
    move.b  #BAUD_DIV_U,DLM(a1)     ; set divisor latch high byte
    bclr.b  #7,LCR(a1)              ; disable divisor latch
    clr.b   SCR(a1)                 ; clear the scratch register
    RTS

; Escreve caractere (D0.B)
UART_WriteChar:
    MOVE.L  CurrentUART,A0
.WaitTx:
    BTST    #5,LCR(A0)        ; TX ready?
    BEQ     .WaitTx
    MOVE.B  D0,THR(A0)
    RTS

; Lê caractere (retorna em D0)
UART_ReadChar:
    MOVE.L  CurrentUART,A0
.WaitRx:
    BTST    #0,LSR(A0)        ; RX ready?
    BEQ     .WaitRx
    MOVE.B  RHR(A0),D0
    RTS

; Escreve string (A0 = endereço da string)
UART_WriteString:
    MOVE.L  A0,-(SP)
    MOVE.B  (A0)+,D0
.WriteLoop:
    CMP.B   #0,D0
    BEQ     .Done
    JSR     UART_WriteChar
    MOVE.B  (A0)+,D0
    BRA     .WriteLoop
.Done:
    MOVE.L  (SP)+,A0
    RTS

; Limpa a tela (sequência VT100)
UART_ClearScreen:
    MOVE.B  #$1B,D0
    JSR     UART_WriteChar
    MOVE.B  #'[',D0
    JSR     UART_WriteChar
    MOVE.B  #'2',D0
    JSR     UART_WriteChar
    MOVE.B  #'J',D0
    JSR     UART_WriteChar
    RTS

; ----------------------------------------------------------------------
; Rotinas Auxiliares
; ----------------------------------------------------------------------

; Lê número hexadecimal (retorna em D0)
UART_ReadHex:
    MOVEQ   #0,D0
    MOVEQ   #7,D1            ; Máximo 8 dígitos
.Loop:
    JSR     UART_ReadChar
    CMP.B   #'0',D0
    BLT     .Done
    CMP.B   #'9',D0
    BLE     .IsDigit
    CMP.B   #'A',D0
    BLT     .Done
    CMP.B   #'F',D0
    BGT     .Done
    SUB.B   #7,D0            ; Ajuste para A-F
.IsDigit:
    SUB.B   #'0',D0
    LSL.L   #4,D0            ; Desloca 4 bits
    DBF     D1,.Loop
.Done:
    RTS

; Lê 4 bytes (32 bits) via UART
UART_ReadLong:
    MOVEQ   #0,D0
    MOVEQ   #3,D1            ; 4 bytes a ler
.Loop:
    LSL.L   #8,D0            ; Desloca resultado atual
    JSR     UART_ReadByte
    OR.B    D0,D0            ; Combina com novo byte
    DBF     D1,.Loop
    RTS

; Lê byte hexadecimal (2 caracteres ASCII)
UART_ReadByte:
    JSR     UART_ReadHexNibble
    LSL.B   #4,D0
    MOVE.B  D0,D1
    JSR     UART_ReadHexNibble
    OR.B    D1,D0
    RTS

; Lê meio-byte hexadecimal
UART_ReadHexNibble:
    JSR     UART_ReadChar
    CMP.B   #'A',D0
    BLT     .Digit
    SUB.B   #7,D0            ; Ajuste para A-F
.Digit:
    SUB.B   #'0',D0
    AND.B   #$0F,D0
    RTS

; ----------------------------------------------------------------------
; Strings do Sistema
; ----------------------------------------------------------------------
WelcomeMsg:
    DC.B    "MC68000 System Monitor",13,10
    DC.B    "---------------------",13,10,13,10,0

MenuText:
    DC.B    "1. Select UART",13,10
    DC.B    "2. Set Baud Rate",13,10
    DC.B    "3. Load Program (PC)",13,10
    DC.B    "4. Write Program (Hex)",13,10
    DC.B    "5. Run Program",13,10
    DC.B    "> ",0

UARTPrompt:
    DC.B    "UART Address (2000/2100/2200/2300): ",0

BaudPrompt:
    DC.B    "Baud Rate Value: ",0

LoadPrompt:
    DC.B    "Load Address: ",0

LoadDoneMsg:
    DC.B    "Program loaded successfully!",13,10,0

WritePrompt:
    DC.B    "Write Address: ",0

WriteSizePrompt:
    DC.B    "Number of bytes: ",0

WriteDoneMsg:
    DC.B    "Data written to memory!",13,10,0

RunPrompt:
    DC.B    "Run Address: ",0

; ----------------------------------------------------------------------
; Variáveis em RAM
; ----------------------------------------------------------------------
    ORG     $70000               ; Área para variáveis
CurrentUART   DS.L    1          ; Endereço da UART atual
RxBuffer      DS.B    256        ; Buffer de recepção
TxBuffer      DS.B    256        ; Buffer de transmissão

; ----------------------------------------------------------------------
; Fim do Código
; ----------------------------------------------------------------------
    END
