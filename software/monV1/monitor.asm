            SECTION .vectors
            ORG     $00000000

            ; --- Vetores de Exceção do 68000 ---
            DC.L    $000A0000       ; SP inicial
            DC.L    _start          ; PC inicial
            DC.L    SERVICE_BUS_ERR   ; Bus Error
            DC.L    SERVICE_ADDR_ERR  ; Address Error
            DC.L    SERVICE_ILLEGAL   ; Illegal Instruction
            DC.L    SERVICE_DIV0      ; Division by Zero
            DC.L    SERVICE_CHECK     ; CHK Instruction
            DC.L    SERVICE_TRAPV     ; TRAPV Instruction
            DC.L    SERVICE_PRIV      ; Privilege Violation
            DC.L    SERVICE_TRACE     ; Trace
            DC.L    SERVICE_LINE_A    ; Line A Emulator
            DC.L    SERVICE_LINE_F    ; Line F Emulator

            ; --- Preencha o resto com handlers padrão ---
            ;REPT 45
            ;DC.L    DEFAULT_HANDLER
            ;ENDR
            DC.L    DEFAULT_HANDLER    ; $60: Spurious Interrupt
            DC.L    DEFAULT_HANDLER     ; $64: Level 1 Interrupt
            DC.L    DEFAULT_HANDLER     ; $68: Level 2 Interrupt
            DC.L    DEFAULT_HANDLER     ; $6C: Level 3 Interrupt
            DC.L    DEFAULT_HANDLER     ; $70: Level 4 Interrupt
            DC.L    DEFAULT_HANDLER     ; $74: Level 5 Interrupt
            DC.L    DEFAULT_HANDLER        ; $78: Level 6 Interrupt  ✅
            DC.L    DEFAULT_HANDLER     ; $7C: Level 7 Interrupt
            DC.L    DEFAULT_HANDLER    ; $60: Spurious Interrupt
            DC.L    DEFAULT_HANDLER     ; $64: Level 1 Interrupt
            DC.L    DEFAULT_HANDLER     ; $68: Level 2 Interrupt
            DC.L    DEFAULT_HANDLER     ; $6C: Level 3 Interrupt
            DC.L    SPURIOUS_HANDLER    ; $60: Spurious Interrupt
            DC.L    INT1_HANDLER        ; $70: Level 4 Interrupt
            DC.L    INT2_HANDLER        ; $74: Level 5 Interrupt
            DC.L    INT3_HANDLER        ; $78: Level 6 Interrupt  ✅
            DC.L    INT4_HANDLER        ; $7C: Level 7 Interrupt
            DC.L    INT5_HANDLER        ; $64: Level 1 Interrupt
            DC.L    INT6_HANDLER        ; $78: Level 6 Interrupt  ✅
            DC.L    INT7_HANDLER        ; $7C: Level 7 Interrupt
            DC.L    TRAP0_HANDLER       ; Aponta para nosso handler
            DC.L    TRAP1_HANDLER       ; Aponta para nosso handler
            DC.L    TRAP2_HANDLER       ; Aponta para nosso handler
            DC.L    TRAP3_HANDLER       ; Aponta para nosso handler
            DC.L    TRAP4_HANDLER       ; Aponta para nosso handler
            DC.L    TRAP5_HANDLER       ; Aponta para nosso handler
            DC.L    TRAP6_HANDLER       ; Aponta para nosso handler
            DC.L    TRAP7_HANDLER       ; Aponta para nosso handler
            DC.L    TRAP8_HANDLER       ; Aponta para nosso handler
            DC.L    TRAP9_HANDLER       ; Aponta para nosso handler
            DC.L    TRAPA_HANDLER       ; Aponta para nosso handler
            DC.L    TRAPB_HANDLER       ; Aponta para nosso handler
            DC.L    TRAPC_HANDLER       ; Aponta para nosso handler
            DC.L    TRAPD_HANDLER       ; Aponta para nosso handler
            DC.L    TRAPE_HANDLER       ; Aponta para nosso handler
            DC.L    TRAPF_HANDLER       ; Aponta para nosso handler

            ; --- Preencha o resto (até $FF) ---
            ;REPT 128
            ;DC.L    DEFAULT_HANDLER
            ;ENDR

            SECTION .jumptable
            ORG     $0400
ROM_JUMPTABLE:
            BRA     UART_Init          ;
            BRA     UART_WriteChar     ;
            BRA     UART_ReadChar      ;
            BRA     UART_Select        ;
            BRA     UART_Setbaudrate   ;
            BRA     DELAY_MS           ;
            BRA     MEMDUMP            ;
            BRA     UART_ReadCharNonEcho
            BRA     _start
            BRA     warm_start
            BRA     MenuLoop

            SECTION .text
            ORG $00001000

FL_ESC      EQU     0   ;ESC flag de tecla ESC recebida pela serial
USER_SP     EQU     $0009F000
;Clock frequency in Hz
F_CPU       equ 16000000
RAMBASE     equ $80000
;Uart register offsets
RHR         equ     0   ; receive holding register (read)
THR         equ     0   ; transmit holding register (write)
IER         equ     2   ; interrupt enable register
ISR         equ     4   ; interrupt status register (read)
FCR         equ     4   ; FIFO control register (write)
LCR         equ     6   ; line control register
MCR         equ     8   ; modem control register
LSR         equ     10  ; line status register
MSR         equ     12  ; modem status register
SPR         equ     14  ; scratchpad register (reserved for system use)
DLL         equ     0   ; divisor latch LSB
DLM         equ     2   ; divisor latch MSB
; aliases for register names (used by different manufacturers)cd ..
RBR         equ     RHR ; receive buffer register
IIR         equ     ISR ; interrupt identification register
SCR         equ     SPR ; scratch register

LED_ADDRESS equ     $4400
UART_BASE   equ     $4000
TIMER_BASE  equ     $4600
BAUD_RATE   equ     9600
BAUD_DIV    equ     (((F_CPU*10)/(16*BAUD_RATE))+5)/10 ; compute one extra decimal place and round
BAUD_DIV_L  equ     (BAUD_DIV&$FF)
BAUD_DIV_U  equ     ((BAUD_DIV>>8)&$FF)

;=== Uart receiver ================= CONSTANTES =================
SOH         EQU     $01        ; Start Of Header
EOT         EQU     $04        ; End Of Transmission
ACK         EQU     $06        ; Acknowledge
NAK         EQU     $15        ; Negative Acknowledge
CAN         EQU     $18        ; Cancel

; --- Macro para Setar Flag ---
SET_FLAG   MACRO
    BCLR    #\1,minhas_flags  ; \1 = primeiro argumento (bit)
    ENDM
; --- Macro para Setar Flag ---
CLR_FLAG   MACRO
    BSET    #\1,minhas_flags  ; \1 = primeiro argumento (bit)
    ENDM
; --- Macro TEST_FLAG corrigida ---
TEST_FLAG  MACRO
    BTST    #\1,minhas_flags
    ENDM
; --- Macro para testar flag (com salto se setado) ---
TST_FLAG_SET MACRO
    BTST    #\1,minhas_flags  ; Testa o bit \1
    BEQ     \2                ; Se bit = 0 (Z=1), pula para o rótulo \2
    ENDM

        ALIGN 2
_start:
        ;ORI     #$2700,SR           ; Desabilita interrupções (M68K)
        MOVE.W #$2700,SR

;        JSR     CLEARRAM            ;Clear entire ram
CLEARRAM:
        LEA     $080000,A0
        LEA     $180000,A1
        MOVEQ   #0,D0
.ClearLoop:
        MOVE.L  D0,(A0)+
        CMPA.L  A0,A1
        BHI     .ClearLoop

        JSR     VALIDATE_ROM        ; Verifica a ROM

        ; Configura USP (pilha de usuário)
        LEA     USER_SP,A0
        MOVE.L  A0,USP        ; 🔥 Define User Stack Pointe


        MOVE.L  #$00000000,RomBase
        MOVE.L  #$00004000,RomSize
        MOVE.L  #RAMBASE,RamBase    ;Total ram 1572864 de 0x8000 até 0x180000
        MOVE.L  #$00100000,RamSize
        MOVE.L  #UART_BASE,CurrentUART
        MOVE.W  #BAUD_RATE,CurrentBaudRate
        MOVE.W  #BAUD_DIV_L,BaudDivL
        MOVE.W  #BAUD_DIV_U,BaudDivH
        MOVE.L  #TIMER_BASE,CurrentTimer


        JSR     UART_INIT
        LEA     cls_str,A0
        JSR     UART_WriteString

        JSR     INIT_8253

        JSR     LED_INIT

        LEA     MSGINIT,A0
        JSR     UART_WriteString

        LEA     Msg_Cs,A0
        JSR     UART_WriteString
        LEA     checksum_rom,A0
        MOVE.L  (A0),D0
        JSR     PrintHexAddress

        LEA     Msg_Cscalc,A0
        JSR     UART_WriteString
        LEA     checksum_calc,A0
        MOVE.L  (A0),D0
        JSR     PrintHexAddress

warm_start:
; Loop principal do menu
MenuLoop:
        JSR     new_line
        LEA     MenuText,A0
        JSR     UART_WriteString

        ; Lê seleção do usuário
        JSR     UART_ReadCharNonEcho
        ;JSR     new_line
        ; Processa opção selecionada
        CMP.B   #'3',D0             ;para essa opção não pode ter echo
        BEQ     LOADPROGRAM
        JSR     UART_WriteChar
        CMP.B   #'1',D0
        BEQ     SELECTUART
        CMP.B   #'2',D0
        BEQ     SETBAUDRATE
        CMP.B   #'4',D0
        BEQ     WRITEPROGRAM
        CMP.B   #'5',D0
        BEQ     RUNPROGRAM
        CMP.B   #'6',D0
        BEQ     PISCA_LED
        CMP.B   #'7',D0
        BEQ     MEMDUMP
        CMP.B   #'8',D0
        BEQ     READ_IN_HEXA
        CMP.B   #'9',D0
        BEQ     UART_ReadHex1
        CMP.B   #'0',D0
        BEQ     CALCBAUDDIV
        CMP.B   #'A',D0
        BEQ     LIGA_INT
        CMP.B   #'B',D0
        BEQ     DESLIGA_INT
        CMP.B   #'C',D0
        BEQ     PRINT_SR
        CMP.B   #'D',D0
        BEQ     READ_8253
        CMP.B   #'T',D0
        BEQ     MsgViaTrap1
        CMP.B   #'R',D0
        BEQ     RdViaTrap1
        CMP.B   #'S',D0
        BEQ     StrViaTrap1
        BRA     MenuLoop            ; Opção inválida, repete menu
RdViaTrap1:
        MOVE.W  #1,D0              ; Função CCONOUT
        TRAP    #1
        JSR     UART_WriteChar
        BRA     MenuLoop
StrViaTrap1:
        LEA     Msg_via_trap1,A0
        MOVE.W  #3,D0              ; Função CCONOUT
        TRAP    #1
.imprimir_fim:
        BRA     MenuLoop

MsgViaTrap1:
        LEA     Msg_via_trap1,A0
        MOVE.B  (A0)+,D1           ; Pega próximo caractere
        BEQ     .imprimir_fim      ; Se for zero, termina
        MOVE.W  #2,D0              ; Função CCONOUT
        TRAP    #1
.imprimir_fim:
        BRA     MenuLoop
; =============================================
; Delay em milissegundos para MC68000 @ 16MHz
; Entrada: D0 = tempo em ms (16 bits)
; Destrói: D0
; =============================================
; ==============================================
; INICIALIZAÇÃO DO 8253 - TICK 10ms
; ==============================================
INIT_8253:
    MOVEM.L D0-D1/A0,-(SP)

    MOVE.L   CurrentTimer,A0
    ;LEA      $4603,A1
    ; --- Configura Canal 0 ---
    ; Modo 3 (Square Wave), Divisor 16-bit
    MOVE.B  #%00110110,+3(A0) ; CW: Canal 0, Modo 3, MSB+LSB

    ; --- Calcula divisor 10000 = $2710 ---
    MOVE.W  #$2710,D0        ; 10000 em hexa

    ; --- Envia divisor LSB depois MSB ---
    MOVE.B  D0,(A0)         ; LSB
    LSR.W   #8,D0            ; Pega MSB
    MOVE.B  D0,(A0)         ; MSB

    MOVEM.L (SP)+,D0-D1/A0
    RTS

; ==============================================
; ROTINA QUE LÊ CONTADOR (PARA DEBUG)
; ==============================================
READ_8253:
    MOVEM.L D0-D1/A0,-(SP)

    MOVE.L   CurrentTimer,A0
    ; --- LATCH DO CONTADOR ---
    MOVE.B  #%00000000,+3(A0) ; Latch Count para Canal 0

    ; --- LÊ BYTE A BYTE ---
    MOVE.B  (A0),D0         ; Lê LSB
    ANDI.L  #$FF,D0          ; Isola byte

    MOVE.B  (A0),D1         ; Lê MSB
    ANDI.L  #$FF,D1
    LSL.W   #8,D1            ; MSB para bits 15-8
    OR.W    D1,D0            ; Combina bytes (D0 = valor)

    ; Mostra valor
    JSR     PrintHexAddress

    MOVEM.L (SP)+,D0-D1/A0
    BRA     MenuLoop

LIGA_INT:

        JSR     new_line
        LEA     spu_msg,A0
        JSR     UART_WriteString
        MOVE.L  USP,A0       ; Lê USP atual
        MOVE.L  A0,D0
        JSR     PrintHexAddress  ; Deve mostrar endereço válido
        JSR     new_line

        LEA     sr_msg,A0
        JSR     UART_WriteString
        CLR.L   D0
        MOVE.W  SR,D0
        JSR     PrintHexAddress  ; Deve mostrar endereço válido
        JSR     new_line

        LEA     sp_msg,A0
        JSR     UART_WriteString
        MOVE.L  SP,D0
        JSR     PrintHexAddress  ; Deve mostrar endereço válido
        JSR     new_line

        MOVE    #$2000,SR


        LEA     RunPrompt,A0
        JSR     UART_WriteString

        BRA     MenuLoop       ; Volta para menu

DESLIGA_INT:
        ;ORI    #$2700,SR
        MOVE.W #$2700,SR
        BRA     MenuLoop
PRINT_SR:
        MOVE.L #$00,D0
        MOVE.W SR,D0
        JSR    PrintHexAddress
        BRA    MenuLoop

DELAY_MS:
        MOVE.L  d1,-(sp)          ; Salva D1
        MOVE.W  d0,d1             ; Contador de ms
        BEQ.S   .end              ; Se D0=0, sai
.loop_ms:
        MOVE.L  #16000,d0         ; Ciclos por ms (16MHz)
.inner_loop:
        SUBQ.L  #1,d0             ; 4 ciclos
        BNE.S   .inner_loop       ; 10 ciclos (se taken)
        SUBQ.W  #1,d1             ; 1 ms
        BNE.S   .loop_ms
.end:
        MOVE.L  (sp)+,d1          ; Restaura D1
        rts

__write_leds:
        MOVE.W  D0,LED_ADDRESS
        RTS

PISCA_LED:
        MOVE.W  #$FF00,D0
        MOVE.W  D0,LED_ADDRESS
        MOVE.L  #500000,D3
.DELAY1:
        SUBQ.L  #1,D3
        BNE     .DELAY1
        MOVE.W  #$0000,D0
        MOVE.W  D0,LED_ADDRESS
        BRA     MenuLoop


LED_INIT:
        MOVE.L  D0,-(SP)        ; Preserva D0
        MOVE.W  #$AA00,LED_ADDRESS
        ;MOVE.W  D0,LED_ADDRESS
        move.l  #250000,D3
.DELAY1:
        SUBQ.L  #1,D3
        BNE     .DELAY1
        MOVE.W  #$0000,LED_ADDRESS
        ;MOVE.W  D0,LED_ADDRESS
        MOVE.L  (SP)+,D0        ;Restaura D0
        RTS

; ----------------------------------------------------------------------
; Rotinas de E/S da UART
; ----------------------------------------------------------------------
UART_Init:
UART_INIT:
        move.l   CurrentUART,a1
        move.b  #%00001101,FCR(a1)      ; enable FIFO
        move.b  #%10000011,LCR(a1)      ; 8 data bits, no parity, 1 stop bit, DLAB=1
        move.b  #BAUD_DIV_L,DLL(a1)     ; set divisor latch low byte
        move.b  #BAUD_DIV_U,DLM(a1)     ; set divisor latch high byte
        bclr.b  #7,LCR(a1)              ; disable divisor latch
        clr.b   SCR(a1)                 ; clear the scratch register
        RTS

    ; Escreve caractere (D0.B)
UART_WriteChar:
        MOVE.L  A0,-(SP)        ; Preserva A0
        MOVE.L  D0,-(SP)        ; Preserva D0
        move.l   CurrentUART,A0
.WaitTx:
        BTST.B  #5,LSR(A0)      ; wait until transmit holding register is empty
        BEQ     .WaitTx
        MOVE.B  D0,THR(A0)      ; transmit byte
        MOVE.L  (SP)+,D0        ;Restaura D0
        MOVE.L  (SP)+,A0        ;Restaura A0
        RTS


; Lê caractere (retorna em D0)
UART_ReadChar:
        MOVE.L  A0,-(SP)        ; Preserva A0
        MOVE.L   CurrentUART,A0
.WaitRx:
        BTST    #0,LSR(A0)        ; RX ready?
        BEQ     .WaitRx
        MOVE.B  RHR(A0),D0
        MOVE.L  (SP)+,A0        ;Restaura A0
        CMP.B   #$1b,D0
        BEQ     .fim
        JSR     UART_WriteChar
.fim
        RTS

; Lê caractere (retorna em D0)
UART_ReadCharNonEcho:
        MOVE.L  A0,-(SP)        ; Preserva A0
        MOVE.L  CurrentUART,A0
.WaitRx:
        BTST    #0,LSR(A0)        ; RX ready?
        BEQ     .WaitRx

        MOVE.B  RHR(A0),D0
        MOVE.L  (SP)+,A0        ;Restaura A0

        RTS

; ----------------------------------------------------------------------
; UART_WriteString - Envia string terminada em null para UART
; Entrada:
;   A0 = Ponteiro para a string (endereço da string)
; ----------------------------------------------------------------------
UART_WriteString:
        MOVE.L  A0,-(SP)      ; Preserva D0
        MOVE.L  D0,-(SP)      ; Preserva D0
.WriteLoop:
        MOVE.B  (A0)+,D0      ; Pega caractere
        BEQ     .Done
        JSR     UART_WriteChar ; Use sua rotine existente
        BRA     .WriteLoop
.Done:
        MOVE.L  (SP)+,D0
        MOVE.L  (SP)+,A0
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
;   Nenhuma a rotina pega o baudrate na memoria e faz ocalculo
; Saída:
;   BAUD_DIV_L e BAUD_DIV_U armazenados na RAM
; Formulas:
;
;
; Simplificada: F_CPU/16/10/BAUD_RATE/10
; ----------------------------------------------------------------------

CALCBAUDDIV:
;[ Registrador D0 (32 bits) ]
;[   DIVU.W #16,D0          ]  → "Divida esse LONG por 16, mas... só pode retornar WORD!"
;[   Se o resultado > 65535 ]  → "F*DEU, vou ignorar e deixar o original mesmo ¯\_(ツ)_/¯"
        ;==(((F_CPU/16)/10)/(BAUD/10))+5/10
        ;((F_CPU/16)/10)
        ;F_CPU = 16000000 ou 0xF42400
        MOVE.L  #F_CPU,D0
        MOVE.W  #16,D1         ; Divisor
        BSR     Div32x16       ; D0 = 0xF4240 (1.000.000)
;1
        move.l  d0,-(SP)
        jsr     PrintHexAddress
        jsr     new_line
        move.l  (SP)+,d0

        MOVE.W  #10,D1         ; Divisor
        BSR     Div32x16       ; D0 = 0x186A0
;2
        move.l  d0,-(SP)
        jsr     PrintHexAddress
        jsr     new_line
        move.l  (SP)+,d0

        ;(BAUD/10)
        move.l  d0,-(SP)
;3
        CLR.L   D0
        MOVE.W  CurrentBaudRate,D0
        move.l  d0,-(SP)
        jsr     PrintHexAddress
        jsr     new_line
        move.l  (SP)+,d0

        MOVE.B  #10,D1
        BSR     Div32x16

;4
        move.l  d0,-(SP)
        jsr     PrintHexAddress
        jsr     new_line
        move.l  (SP)+,D1
        move.l  (SP)+,D0


        ;(F_CPU/BAUD)
        BSR     Div32x16
;5
        move.l  d0,-(SP)
        jsr     PrintHexAddress
        jsr     new_line
        move.l  (SP)+,d0

        ; 4. Separa parte alta/baixa corretamente
        MOVE.W  D0,D1
        ANDI.W  #$FF,D0        ; D0 = BAUD_DIV_L (8 bits baixos)
        LSR.W   #8,D1          ; D1 = BAUD_DIV_H (8 bits altos)
        ANDI.W  #$FF,D1        ; Limpa bits extras

        ; 5. Armazena (AGORA COM 16 BITS, NÃO 32!)
        LEA     Baud1DivL,A0
        MOVE.W  D0,(A0)        ; 16 bits suficientes
        LEA     Baud1DivH,A0
        MOVE.W  D1,(A0)

        BRA     MenuLoop
        RTS
.BaudError:
        BRA     _start

new_line:
        MOVE.L  D0,-(SP)          ; Salva D0
        MOVE.B  #10,D0
        JSR     UART_WriteChar
        MOVE.B  #13,D0
        JSR     UART_WriteChar
        MOVE.L  (SP)+,D0          ; Restaura D0
        RTS
; D0 = Dividendo (32 bits), D1 = Divisor (16 bits)
; Retorna D0 = Quociente, D1 = Resto
Div32x16:
        MOVEQ   #0,D2       ; D2 = Quociente
        MOVEQ   #31,D3      ; 32 iterações
DivLoop:
        LSL.L   #1,D0       ; Desloca D0 (MSB → Carry)
        ROXL.L  #1,D2       ; Desloca D2 com Carry
        CMP.W   D1,D2       ; D2 >= D1?
        BLT     .skip
        SUB.W   D1,D2       ; Sim, subtrai
        ADDQ.L  #1,D0       ; E adiciona 1 ao quociente
.skip:
        DBRA    D3,DivLoop  ; Repete
        MOVE.L  D2,D1       ; Resto em D1
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
PrintHexPRECISA_DE_REVISAO:
        LINK    A6,#-8            ; Reserva espaço na pilha
        MOVE.L  D2,-(SP)          ; Salva D2
        MOVE.L  D0,-4(A6)         ; Guarda o valor original
        MOVE.W  D1,-6(A6)         ; Guarda contador de dígitos

        MOVE.W  #$0008,D1

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
; MemDump - Imprime dump de memória formatado
; Entrada:
;   A0 = Endereço inicial (ex: $80000)
;   D0 = Quantidade de bytes (ex: 256)
; ----------------------------------------------------------------------
MEMDUMP:
        LEA     DumpHeader,A0
        JSR     UART_WriteString
        MOVE.L  (addressInHex),A0
        MOVE.L  A0,D0
        JSR     PrintHexAddress
        JSR     new_line

        LEA     DumpHeader1,A0
        JSR     UART_WriteString

        MOVE.L  (addressInHex),A0
        ; Calcula endereço final

DUMPLOOPMASTER:
        CLR.L   D1
        MOVE.L  A0,D1
        ADDI.L  #$000000FF,D1             ; D1 = endereço final
        ;MOVE.L  D1,D0
        ;JSR     PrintHexAddress
        ;JSR     new_line

        ;aguarda um caractere ser digitado mas nao usa é somente para parar a execução aqui
        ;JSR     UART_ReadChar


DumpLoop:
        ; Nova linha a cada 16 bytes
        MOVE.L  A0,D0
        ANDI.L  #$0000000F,D0     ; Verifica se é início de linha
        BNE     NoNewLine

        ; Imprime endereço
        MOVE.L  A0,D0
        JSR     PrintHexAddress    ; Imprime 8 dígitos hex

        MOVE.B  #':',D0
        JSR     UART_WriteChar
        MOVE.B  #' ',D0
        JSR     UART_WriteChar

NoNewLine:
        ; Imprime byte em hex
        MOVE.B  (A0)+,D0
        JSR     PrintByteHex

        MOVE.B  #' ',D0
        JSR     UART_WriteChar

        ; Verifica fim da linha (16 bytes)
        MOVE.L  A0,D0
        ANDI.L  #$0000000F,D0
        BNE     NoEndLine

        ; Imprime caracteres ASCII
        MOVE.B  #' ',D0
        JSR     UART_WriteChar
        MOVE.B  #'|',D0
        JSR     UART_WriteChar

        LEA     -16(A0),A1        ; Volta ao início da linha
        MOVEQ   #15,D2            ; 16 caracteres

AsciiLoop:
        MOVE.B  (A1)+,D0
        CMP.B   #32,D0            ; Verifica se é imprimível
        BLT     NonPrintable
        CMP.B   #126,D0
        BGT     NonPrintable

        JSR     UART_WriteChar
        BRA     NextAscii

NonPrintable:
        MOVE.B  #'.',D0           ; Substitui não imprimíveis
        JSR     UART_WriteChar

NextAscii:
        DBRA    D2,AsciiLoop

        MOVE.B  #'|',D0
        JSR     UART_WriteChar
        MOVE.B  #13,D0            ; CR
        JSR     UART_WriteChar
        MOVE.B  #10,D0            ; LF
        JSR     UART_WriteChar

NoEndLine:
        ; Verifica fim do dump
        CMP.L   D1,A0
        BLS     DumpLoop

        MOVE.L  A0,-(SP)          ; Salva endereço atual
        LEA     HitAnyKey,A0
        JSR     UART_WriteString
        JSR     UART_ReadChar
        CMP.B   #$1B,D0
        BEQ     .fim

        MOVE.L  (SP)+,A0          ; Recupera endereço atual
        BRA     DUMPLOOPMASTER
.fim
        BRA     MenuLoop

; ----------------------------------------------------------------------
; PrintHexAddress - Imprime endereço de 32 bits
; Entrada: D0 = endereço
; ----------------------------------------------------------------------
PrintHexAddress:
        SWAP    D0                ; Imprime parte alta primeiro
        JSR     PrintWordHex
        SWAP    D0                ; Parte baixa
        ; Continua para PrintWordHex

; ----------------------------------------------------------------------
; PrintWordHex - Imprime word em hex (16 bits)
; Entrada: D0.w = valor
; ----------------------------------------------------------------------
PrintWordHex:
        ROL.W   #8,D0             ; Byte mais significativo primeiro
        JSR     PrintByteHex
        ROR.W   #8,D0             ; Byte menos significativo
        ; Continua para PrintByteHex

; ----------------------------------------------------------------------
; PrintByteHex - Imprime byte em hex (8 bits)
; Entrada: D0.b = valor
; ----------------------------------------------------------------------
PrintByteHex:
        MOVE.B  D0,-(SP)          ; Salva byte original
        LSR.B   #4,D0             ; Nibble alto
        BSR     PrintNibble
        MOVE.B  (SP)+,D0          ; Recupera byte
        ANDI.B  #$0F,D0           ; Nibble baixo
        ; Continua para PrintNibble
; ----------------------------------------------------------------------
; PrintNibble - Imprime um nibble em hex
; Entrada: D0.b bits 3-0 = nibble (0-15)
; ----------------------------------------------------------------------
PrintNibble:
        CMP.B   #9,D0
        BLS     .Decimal
        ADD.B   #7,D0             ; Ajuste para A-F
.Decimal:
        ADD.B   #'0',D0
        JMP     UART_WriteChar    ; Usa JMP para tail call optimization

;CLEARRAM:
;        LEA     $80000,A0
;        LEA     $9FFFF,A1
;        ;LEA     $BFFFF,A1
;        MOVEQ   #0,D0
;.ClearLoop:
;        MOVE.L  D0,(A0)+
;        CMPA.L  A0,A1
;        BHI     .ClearLoop
;        RTS


CLEARRAM3:
        MOVE.L  (addressInHex),A0
        MOVE.L  (addressInHex),D0
        ADD.L   #$1000,D0
        MOVE.L  D0,A1
        MOVEQ   #0,D0
.ClearLoop:
        MOVE.L  D0,(A0)+
        CMPA.L  A0,A1
        BHI     .ClearLoop
        BRA     MenuLoop


; ----------------------------------------------------------------------
; Subrotinas do Menu
; ----------------------------------------------------------------------

; 1. Seleciona UART
UART_Select:
SELECTUART:
        LEA     PromptNotImplemented,A0
        JSR     UART_WriteString
        ;LEA     UARTPrompt,A0
        ;JSR     UART_WriteString
        ;JSR     UART_ReadHex        ; Lê endereço da UART
        ;MOVE.L  D0,CurrentUART      ; Atualiza UART atual
        ;JSR     UART_Init           ; Reinicializa UART
        BRA     MenuLoop

; 2. Configura Baud Rate
UART_Setbaudrate:
SETBAUDRATE:
        LEA     PromptNotImplemented,A0
        JSR     UART_WriteString
        ;LEA     BaudPrompt,A0
        ;JSR     UART_WriteString
        ;JSR     UART_ReadHex        ; Lê valor do baud rate
        ;MOVE.L  CurrentUART,A0
        ;MOVE.B  D0,(UART_BAUD,A0)   ; Configura registrador
        BRA     MenuLoop

; 3. Carrega programa via serial
LOADPROGRAM:
        LEA     pgm_buffer,A0   ; Onde os dados serão salvos
        MOVE.L  A0,usr_buffer_addr
        JSR     XMODEM_Receive
        BRA     MenuLoop

; 4. Grava programa manualmente (hex)
WRITEPROGRAM:
        LEA     WritePrompt,A0
        JSR     UART_WriteString
        JSR     UART_ReadHex        ; Lê endereço
        MOVE.L  (addressInHex),A1               ; A1 = ponteiro

        LEA     WriteSizePrompt,A0
        JSR     UART_WriteString
        MOVE.L  #$00000000,D0
.WriteLoop:
        JSR     UART_ReadByte       ; Lê byte
        TST_FLAG_SET FL_ESC,.fim    ; Testa o bit 0 (ESC=0 se setado)
        MOVE.B  D0,(A1)+            ; Armazena
        BRA     .WriteLoop

.fim:
        LEA     WriteDoneMsg,A0
        JSR     UART_WriteString
        BRA     MenuLoop

; 5. Executa programa na RAM
RUNPROGRAM:
        LEA     flag_pgm_loaded,A0   ; Get flag program loaded
        MOVE.B  (A0),D0              ; Program  loaded
        CMP.B   #1,D0
        BEQ     .run_program
        LEA     NO_PROGRAM_TO_RUN,A0
        JSR     UART_WriteString
        BRA     MenuLoop

.run_program
        LEA     RunPrompt,A0
        JSR     UART_WriteString
        LEA     pgm_buffer,A0   ; A0 aponta para o endereço buffer onde esta o progama
        JSR     (A0)        ; Chama o código como uma sub-rotina (salva o endereço de retorno)
        BRA     MenuLoop

; ----------------------------------------------------------------------
; Rotinas Auxiliares
; ----------------------------------------------------------------------

; Lê número hexadecimal (retorna em D0)
UART_ReadHex1:
        MOVE.L  D1,-(SP)
        MOVE.L  D2,-(SP)

        LEA     WritePrompt,A0
        JSR     UART_WriteString

        JSR     new_line

        MOVEQ   #0,D0
        MOVEQ   #0,D1            ; Máximo 8 dígitos
        MOVEQ   #0,D2            ; Resultado em D2

.Loop:
        JSR     UART_ReadChar
        CMP.B   #13,D0
        BEQ     .Done
        CMP.B   #10,D0
        BEQ     .Done
        JSR     BufferPut
        BRA     .Loop
.Done:
;         BSR     UART_BufferGet
;         CMP.B   #-1,D0          ; Buffer vazio?
;         BEQ     NadaParaLer      ; Se sim, ignora
;         Senão, D0 contém o byte lido!
.loop1:
        JSR     BufferGet
        CMP.B   #-1,D0          ; Buffer vazio?
        BEQ     .fim      ; Se sim, ignora
        JSR     UART_WriteChar
        BRA     .loop1
.fim:
        MOVE.L  (SP)+,D2
        MOVE.L  (SP)+,D1
        JSR     new_line
        bra     MenuLoop ;provisoriamente
        RTS

; Lê número hexadecimal (retorna em D0)
UART_ReadHex:
        MOVE.L  D1,-(SP)
        MOVE.L  D2,-(SP)

        MOVEQ   #0,D0
        MOVEQ   #28,D1            ; Máximo 8 dígitos
        MOVEQ   #0,D2            ; Resultado em D2
.Loop:
        CLR.L   D0
        JSR     UART_ReadChar
        CMP.B   #13,D0
        BEQ     .Done
        CMP.B   #10,D0
        BEQ     .Done
        ;Tratando os numeros
        CMP.B   #'0',D0
        BGE     .maiorQueZero
        BRA     .Loop
.maiorQueZero:
        CMP.B   #'9',D0
        BLE     .isdigit
        ;Tratando as letras
        CMP.B   #'A',D0
        BGE     .maiorQueA
        BRA     .Loop
.maiorQueA:
        CMP.B   #'F',D0
        BLE     .isletter
        BRA     .Loop
.isdigit:
        SUB.B   #'0',D0
        LSL.L   D1,D0
        SUB.B   #4,D1
        OR.L    D0,D2
        LEA     addressInHex,A0
        MOVE.L  D2,(A0)
        BRA     .Loop
.isletter:
        SUB.B   #$37,D0
        LSL.L   D1,D0
        SUB.B   #4,D1
        OR.L    D0,D2
        LEA     addressInHex,A0
        MOVE.L  D2,(A0)
        BRA     .Loop
.Done:
        JSR     new_line
        LEA     addressInHex,A0
        MOVE.L  (A0),D0
        JSR     PrintHexAddress
        JSR     new_line
        MOVE.L  (SP)+,D2
        MOVE.L  (SP)+,D1
        RTS

READ_IN_HEXA:
        LEA     TestHexInput,A0
        JSR     UART_WriteString
        JSR     UART_ReadHex
        bra     MenuLoop


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
        CLR_FLAG    FL_ESC
        MOVE #0,CCR
        ;MOVE.L  D0,-(SP)            ; Preserva D0
        JSR     UART_ReadHexNibble
        TST_FLAG_SET FL_ESC,.Fim            ; Testa o bit 0 (Z=0 se setado)
        LSL.B   #4,D0
        MOVE.B  D0,D1
        JSR     UART_ReadHexNibble
        TST_FLAG_SET FL_ESC,.Fim            ; Testa o bit 0 (Z=0 se setado)
        OR.B    D1,D0
.Fim:
        ;MOVE.L  (SP)+,D0        ; Recupera D0
        RTS

; Lê meio-byte hexadecimal
UART_ReadHexNibble:
        JSR     UART_ReadChar
        CMP.B   #$1B,D0
        BEQ     .Fim
        CMP.B   #'A',D0
        BLT     .Digit
        SUB.B   #7,D0            ; Ajuste para A-F
.Digit:
        SUB.B   #'0',D0
        AND.B   #$0F,D0
        RTS
.Fim:
        SET_FLAG FL_ESC
        RTS

;--------------------------------------------------
; BufferPut - Insere um byte no buffer (D0.B = byte)
;--------------------------------------------------
; Exemplo: insere 'A' no buffer
;          MOVE.B  #'A',D0
;          JSR     UART_BufferPut

BufferPut:
        MOVE.L  D1,-(SP)
        MOVE.L  A0,-(SP)

        ;ANDI.W    #$FF00,D0
        LEA     BUFFER,A0
        MOVE.W  BUFFER_COUNT,D1

        CMP.W   #256,D1
        BGE     .BufferFull

        ; Modificado para usar deslocamento de 16 bits
        MOVE.W  BUFFER_HEAD,D1
        ADD     D1,A0
        MOVE.B  D0,(A0)              ;PUTTING BYTE

        ADD     #2,D1              ; Incrementa como word
        ANDI.W  #255,D1            ; Mantém no range 0-255
        MOVE.W  D1,BUFFER_HEAD

        ADDQ.W  #1,BUFFER_COUNT

.BufferFull:
        MOVE.L  (SP)+,A0
        MOVE.L  (SP)+,D1

        RTS

;--------------------------------------------------
; BufferGet - Pega um byte do buffer (retorna em D0.B, ou -1 se vazio)
;--------------------------------------------------
;Exemplo: Lendo byte do buffer
;         BSR     UART_BufferGet
;         CMP.B   #-1,D0          ; Buffer vazio?
;         BEQ     NadaParaLer      ; Se sim, ignora
;         Senão, D0 contém o byte lido!
BufferGet:
        MOVE.L  D1,-(SP)
        MOVE.L  A0,-(SP)

        MOVE.W  BUFFER_COUNT,D1
        BEQ     .BufferEmpty

        LEA     BUFFER,A0

        ; Modificado para usar deslocamento de 16 bits
        MOVE.W  BUFFER_TAIL,D1
        MOVE.B  (A0,D1.W),D0       ; Usando D1.W em vez de D1.L

        ADDQ.B  #2,D1              ; Incrementa como word
        ANDI.W  #255,D1            ; Mantém no range 0-255
        MOVE.W  D1,BUFFER_TAIL

        SUBQ.W  #1,BUFFER_COUNT
        BRA     .Exit

.BufferEmpty:
        JSR     FBufferEmpty
        MOVEQ   #-1,D0
.Exit:
        MOVE.L  (SP)+,A0
        MOVE.L  (SP)+,D1
        RTS

FBufferEmpty:
        JSR     new_line
        LEA     BufferEmpty,A0
        JSR     UART_WriteString
        JSR     new_line
        RTS
;---------------------------------------------------------------------
; Zera os ponteiros do buffer circular (HEAD e TAIL) - VASM Edition
;---------------------------------------------------------------------
ClearBufferPointers:
        MOVE.L  #0,BUFFER_HEAD    ; Zera BUFFER_HEAD (32 bits)
        MOVE.L  #0,BUFFER_TAIL    ; Zera BUFFER_TAIL (32 bits)
        MOVE.W  #0,BUFFER_COUNT   ; Opcional: zera contador (16 bits)
        RTS
;---------------------------------------------------------------------
; MontaAddress - Lê 8 bytes (4 bits cada) e forma um uint32
; Entrada: Buffer contém 8 bytes (MSB first, 4 bits úteis cada)
; Saída:   D0.L = valor de 32 bits (formado pelos nibbles)
;          D1.B = 0 (sucesso) ou -1 (erro, buffer vazio)
;---------------------------------------------------------------------
MontaAddress:
        MOVEM.L D2-D5/A0,-(SP)   ; Salva registradores

        ; Verifica se há pelo menos 8 bytes no buffer
        MOVE.W  BUFFER_COUNT,D1
        CMP.W   #8,D1
        BLT     .BufferUnderrun   ; Erro se menos que 8 bytes

        LEA     BUFFER,A0      ; A0 = base do buffer
        MOVE.L  BUFFER_TAIL,D2    ; D2 = tail (ponteiro de leitura)
        CLR.L   D0                ; Zera D0 (resultado final)
        MOVEQ   #7,D3             ; Contador (8 nibbles, MSB first)

.ReadLoop:
        MOVE.B  (A0,D2.L),D4      ; Lê byte do buffer
        ANDI.B  #$0F,D4          ; Pega apenas os 4 bits inferiores

        ; Desloca e insere os 4 bits em D0
        LSL.L   #4,D0             ; Abre espaço para o novo nibble
        OR.B    D4,D0             ; Adiciona os 4 bits no LSB

        ; Atualiza tail (circular)
        ADDQ.L  #1,D2
        ANDI.L  #255,D2           ; Mantém entre 0-255

        DBRA    D3,.ReadLoop      ; Repete para todos os 8 nibbles

        ; Atualiza ponteiros globais
        MOVE.L  D2,BUFFER_TAIL
        SUB.W   #8,BUFFER_COUNT

        MOVEQ   #0,D1             ; Sucesso (D1 = 0)
        BRA     .Exit

.BufferUnderrun:
        MOVEQ   #-1,D1            ; Erro (D1 = -1)
        MOVEQ   #0,D0             ; Retorna 0 em D0

.Exit:
        MOVEM.L (SP)+,D2-D5/A0    ; Restaura registradores
        RTS

        DC.B "pdsilva AKA pgordao"
        ALIGN 2
; =====================================================================
; XMODEM RECEIVER ROUTINE
;bloco.append(0x01);        // SOH
;bloco.append(blockNumber); // Número do bloco (começa com 1)
;bloco.append(255 - blockNumber); // Complemento
;bloco.append(dados);       // Seus 128 bytes de dados
;bloco.append(checksum);    // Checksum calculado
; =====================================================================
XMODEM_Receive:
       MOVEM.L D2-D7/A0-A6,-(SP)
       ; Inicializa variáveis
       LEA     expected_block,A0
       MOVE.B  #1,D0
       MOVE.B  D0,(A0)             ; Bloco esperado (0)
       LEA     xmodem_buffer,A0

       LEA     flag_pgm_loaded,A0   ; Get flag program loaded
       MOVE.B  #0,D0
       MOVE.B  D0,(A0)              ; Program not loaded

       ; ---- 1. INICIALIZAÇÃO ----
       MOVE.B  #NAK,D0
       JSR     UART_WriteChar      ; Solicita início

       ;SINALIZA NACK SENT
       MOVE.W  #$0800,D0
       JSR     __write_leds

       ;LEA   pgm_buffer,A2   ; Destino (garanta alinhamento em 4 bytes)
       LEA   $00082000,A2   ; Destino (garanta alinhamento em 4 bytes)

       ; ---- 2. LOOP PRINCIPAL ----
Receive_Loop:
       JSR     UART_ReadCharNonEcho

       CMP.B   #EOT,D0
       BEQ     Transfer_Complete   ; Fim da transmissão

       CMP.B   #SOH,D0
       BNE     Receive_Loop        ; Ignora bytes inválidos

       ;SINALIZA leds
       MOVE.W  #$0C00,D0
       JSR     __write_leds

       ; ---- 3. RECEBE HEADER ----
       JSR     UART_ReadCharNonEcho       ; Block number
       MOVE.B  D0,block_number

       JSR     UART_ReadCharNonEcho       ; ~Block number (complemento)

       ;SINALIZA leds
       MOVE.W  #$0800,D0
       JSR     __write_leds

       ; ---- 4. RECEBE DADOS ----
       MOVE.L  #128/4,D1        ; 32 longs (128 bytes)
       LEA     xmodem_buffer,A1
Read_Loop:
       ; Lê 4 bytes da UART e armazena em D0 (usando shifts/ORs)
       JSR     UART_ReadCharNonEcho    ; Byte 1 (bits 24-31)
       LSL.L   #8,D0
       JSR     UART_ReadCharNonEcho    ; Byte 2 (bits 16-23)
       LSL.L   #8,D0
       JSR     UART_ReadCharNonEcho    ; Byte 3 (bits 8-15)
       LSL.L   #8,D0
       JSR     UART_ReadCharNonEcho    ; Byte 4 (bits 0-7)
       MOVE.L  D0,(A1)+         ; Grava os 4 bytes
       SUBQ.L  #1,D1
       BNE     Read_Loop

       MOVE.W  #$0600,D0
       JSR     __write_leds

       ; ---- 5. VERIFICA CHECKSUM ----
       JSR     UART_ReadCharNonEcho       ; Checksum
       MOVE.B  D0,D2


;******************************************************************************************
                ;SEM CHECKSUM NESSE MOMENTO SEM COPIAR DADOS SO TESTANDO ENVIO
           ;     BRA     Send_ACK
;******************************************************************************************

        ; Calcula checksum local
        LEA     xmodem_buffer,A1
        MOVE.W  #127,D1
        CLR.L   D3

Calc_Checksum:
        ADD.B   (A1)+,D3
        DBF     D1,Calc_Checksum;

        CMP.B   D2,D3
        BNE     Send_NAK            ; Erro no checksum

        ;---- 6. VALIDA NÚMERO DO BLOCO ----
        ;MOVE.B  block_number,D0
        ;CMP.B   expected_block,D0
        ;BNE     Send_NAK            ; Bloco fora de ordem

        ; ---- 7. COPIA DADOS VÁLIDOS ----
        ; (Aqui você processa os 128 bytes recebidos)
        ; Exemplo: copiar do buffer para a RAM
        ; 1. Copia os 128 bytes do XMODEM para o buffer destino
        LEA     xmodem_buffer,A1     ; Origem (128 bytes)
        MOVE.L  #32,D1              ; 32 longs = 128 bytes (contador exato)
Copy_Data:
        MOVE.L  (A1)+,(A2)+         ; Copia 4 bytes por vez
        SUBQ.L  #1,D1               ; Decrementa contador
        BNE     Copy_Data            ; Repete até D1 = 0

        ; ---- 8. CONFIMA RECEPÇÃO ----
        ADDQ.B  #1,expected_block   ; Próximo bloco
        MOVE.B  #ACK,D0
        JSR     UART_WriteChar
        BRA     Receive_Loop

Send_ACK:
        ;SINALIZA NACK SENT
        MOVE.W  #$0400,D0
        JSR     __write_leds
        MOVE.B  #ACK,D0
        JSR     UART_WriteChar
        BRA     Receive_Loop

Send_NAK:
        MOVE.B  #NAK,D0
        JSR     UART_WriteChar
        BRA     Receive_Loop

Transfer_Complete:
        MOVE.B  #ACK,D0             ; Confirma EOT
        JSR     UART_WriteChar

        LEA     flag_pgm_loaded,A0   ; Get flag program loaded
        MOVE.B  #1,D0
        MOVE.B  D0,(A0)              ; Program  loaded

        MOVEM.L (SP)+,D2-D7/A0-A6
        RTS
; ========================================================
; Validador de Checksum para ROM (MC68000)
; Assume:
;   - Checksum está nos últimos 4 bytes da ROM (LONG)
;   - Big-endian (padrão 68000)
;   - ROM termina em 0x0000FFFF (16KB)
; ========================================================

VALIDATE_ROM:
        LEA     ROM_START,A0        ; Endereço inicial da ROM (0x00000000)
        MOVE.L  #ROM_SIZE-4,D0      ; Tamanho da ROM (16KB - 4 bytes)
        MOVE.L  #0,D1               ; Acumulador do checksum

    ; --- Calcula checksum (soma de todos os LONGs, exceto os últimos 4 bytes) ---
.CHECKSUM_LOOP:
        MOVE.L  (A0)+,D2            ; Lê 4 bytes da ROM
        ADD.L   D2,D1               ; Soma ao acumulador
        SUB.L   #4,D0               ; Decrementa contador
        BGT     .CHECKSUM_LOOP      ; Repete até D0 <= 0

        LEA     checksum_calc,A0
        MOVE.L  D1,(A0)+
        ;RTS     ;NESSE MOMENTO NÃO FAZ NADA COM O RESULTADO

        ; --- Compara com o checksum armazenado (últimos 4 bytes da ROM) ---
        MOVE.L  ROM_END-4+1,D2        ; Lê o checksum gravado (0x0000FFFC)
        CMP.L   D1,D2               ; Combina com o calculado?
        BEQ     .CHECKSUM_OK        ; Se sim, ROM válida

        ; --- Checksum inválido: travar o sistema ou notificar ---
        MOVE.W  #$DEAD,D3           ; Código de erro (opcional)
        BRA     SYSTEM_HALT         ; Trava o sistema (ou reinicia)
.CHECKSUM_OK:
        RTS                         ; Retorna (ROM válida)


SYSTEM_HALT:
        MOVE.W  #$2700,SR        ; Desabilita interrupções
.INFINITE_LOOP:
        BRA     .INFINITE_LOOP   ; Trava o sistema



; --- Constantes ---
ROM_START   EQU     $00000000   ; Início da ROM
ROM_END     EQU     $00003FFF   ; Fim da ROM (8KB)
ROM_SIZE    EQU     ROM_END-ROM_START+1  ; Tamanho total (16384 bytes)

SPURIOUS_HANDLER:
    MOVE.W  #$CB00,LED_ADDRESS  ; Indica spurious
    RTE

DEFAULT_HANDLER:
    MOVEM.L D0-D7/A0-A6,-(SP)

    ; --- IDENTIFICA O TIPO DE EXCEÇÃO ---
    ; --- AGORA lê corretamente da pilha ---
    MOVE.L  (14,SP),D0      ; ⭐⭐ PC (14 bytes abaixo por causa dos registradores salvos)
    MOVE.W  (18,SP),D1      ; ⭐⭐ SR (18 bytes abaixo)
    MOVE.W  (20,SP),D2      ; ⭐⭐ Vector Offset (20 bytes abaixo)

    ; Mostra informações detalhadas
    LEA     debug_msg,A0
    JSR     UART_WriteString

    MOVE.L  D0,D0           ; PC
    JSR     PrintHexAddress
    JSR     new_line

    LEA     sr_msg,A0
    JSR     UART_WriteString
    MOVE.W  D1,D0           ; SR
    JSR     PrintHexAddress
    JSR     new_line

    LEA     vector_msg,A0
    JSR     UART_WriteString
    MOVE.W  D2,D0           ; Vector offset
    JSR     PrintHexAddress
    JSR     new_line

    ; --- ANALISA O VETOR ---
    LSR.W   #2,D2           ; Divide por 4 para get vector number
    ANDI.W  #$FF,D2         ; Vector number em D2

    LEA     vector_num_msg,A0
    JSR     UART_WriteString
    MOVE.W  D2,D0
    JSR     PrintHexAddress
    JSR     new_line

    ; --- MOSTRA QUAL EXCEÇÃO É ---
    CMP.W   #8,D2
    BNE     .not_bus_error
    LEA     bus_error_msg,A0
    BRA     .show_msg
.not_bus_error:
    CMP.W   #9,D2
    BNE     .not_address_error
    LEA     address_error_msg,A0
    BRA     .show_msg
.not_address_error:
    CMP.W   #10,D2
    BNE     .not_illegal
    LEA     illegal_msg,A0
    BRA     .show_msg
.not_illegal:
    CMP.W   #32,D2
    BLO     .other_exception
    LEA     trap_msg,A0
    BRA     .show_msg
.other_exception:
    LEA     unknown_msg,A0

.show_msg:
    JSR     UART_WriteString
    JSR     new_line

    ; Pequeno delay para visualização
    MOVE.L  #500000,D3
.DELAY:
    SUBQ.L  #1,D3
    BNE     .DELAY

    MOVEM.L (SP)+,D0-D7/A0-A6
    RTE
    JMP MenuLoop

; --- MENSAGENS DE DEBUG ---
debug_msg:      DC.B "Exception - PC: ",0
sr_msg:         DC.B "Status Reg: ",0
sp_msg:         DC.B "Stack Reg: ",0
spu_msg:         DC.B "StackU Reg: ",0
vector_msg:     DC.B "Vector offset: ",0
vector_num_msg: DC.B "Vector number: ",0
bus_error_msg:  DC.B "Bus Error!",0
address_error_msg: DC.B "Address Error!",0
illegal_msg:    DC.B "Illegal Instruction!",0
trap_msg:       DC.B "TRAP Instruction!",0
unknown_msg:    DC.B "Unknown Exception!",0




INT1_HANDLER:
        MOVEM.L D0-D7/A0-A6,-(A7)
        ; Seu código de tratamento aqui
        MOVE.W  #$D100,D0
        MOVE.W  D0,LED_ADDRESS

        MOVEM.L (A7)+,D0-D7/A0-A6
        RTE
INT2_HANDLER:
        MOVEM.L D0-D7/A0-A6,-(A7)
        ; Seu código de tratamento aqui
        MOVE.W  #$D200,D0
        MOVE.W  D0,LED_ADDRESS

        MOVEM.L (A7)+,D0-D7/A0-A6
        RTE
INT3_HANDLER:
        MOVEM.L D0-D7/A0-A6,-(A7)
        ; Seu código de tratamento aqui
        MOVE.W  #$D300,D0
        MOVE.W  D0,LED_ADDRESS

        MOVEM.L (A7)+,D0-D7/A0-A6
        RTE
INT4_HANDLER:
        MOVEM.L D0-D7/A0-A6,-(A7)
        ; Seu código de tratamento aqui
        MOVE.W  #$D400,D0
        MOVE.W  D0,LED_ADDRESS

        MOVEM.L (A7)+,D0-D7/A0-A6
        RTE
INT5_HANDLER:
        MOVEM.L D0-D7/A0-A6,-(A7)
        ; Seu código de tratamento aqui
        MOVE.W  #$D500,D0
        MOVE.W  D0,LED_ADDRESS

        MOVEM.L (A7)+,D0-D7/A0-A6
        RTE
INT6_HANDLER:
        MOVEM.L D0-D7/A0-A6,-(A7)
        ; Seu código de tratamento aqui
        MOVE.W  #$D600,D0
        MOVE.W  D0,LED_ADDRESS

        MOVEM.L (A7)+,D0-D7/A0-A6
        RTE
INT7_HANDLER:
        MOVEM.L D0-D7/A0-A6,-(A7)
        ; Seu código de tratamento aqui
        MOVE.W  #$D700,D0
        MOVE.W  D0,LED_ADDRESS

        MOVEM.L (A7)+,D0-D7/A0-A6
        RTE

SERVICE_BUS_ERR:
        MOVE.W  #$C100,LED_ADDRESS
        RTE
SERVICE_ADDR_ERR:
        MOVE.L  2(SP),D0        ; PC onde ocorreu a exceção
        MOVE.W  6(SP),D1        ; SR na época
        MOVE.W  8(SP),D2        ; Vector offset (FORMATO 68000!)

        MOVE.L  D0,-(SP)
        LEA     debug_msg,A0
        JSR     UART_WriteString

        MOVE.L  (SP)+,D0
        JSR     PrintHexAddress  ; Deve mostrar endereço válido
        JSR     new_line

        LEA     sr_msg,A0
        JSR     UART_WriteString
        CLR.L   D0
        MOVE.W  D1,D0
        JSR     PrintHexAddress  ; Deve mostrar endereço válido
        JSR     new_line

        LEA     sp_msg,A0
        JSR     UART_WriteString
        CLR.L   D0
        MOVE.W  D2,D0
        JSR     PrintHexAddress  ; Deve mostrar endereço válido
        JSR     new_line
        MOVE.W  #$C200,LED_ADDRESS
        RTE
SERVICE_ILLEGAL:
        MOVE.L  2(SP),D0        ; PC onde ocorreu a exceção
        MOVE.W  6(SP),D1        ; SR na época
        MOVE.W  8(SP),D2        ; Vector offset (FORMATO 68000!)

        MOVE.L  D0,-(SP)
        LEA     debug_msg,A0
        JSR     UART_WriteString

        MOVE.L  (SP)+,D0
        JSR     PrintHexAddress  ; Deve mostrar endereço válido
        JSR     new_line

        LEA     sr_msg,A0
        JSR     UART_WriteString
        CLR.L   D0
        MOVE.W  D1,D0
        JSR     PrintHexAddress  ; Deve mostrar endereço válido
        JSR     new_line

        LEA     sp_msg,A0
        JSR     UART_WriteString
        CLR.L   D0
        MOVE.W  D2,D0
        JSR     PrintHexAddress  ; Deve mostrar endereço válido
        JSR     new_line

        LEA     sr_msg,A0
        JSR     UART_WriteString
        CLR.L   D0
        MOVE.W  SR,D0
        JSR     PrintHexAddress  ; Deve mostrar endereço válido
        JSR     new_line

        LEA     sp_msg,A0
        JSR     UART_WriteString
        MOVE.L  SP,D0
        JSR     PrintHexAddress  ; Deve mostrar endereço válido
        JSR     new_line
        MOVE.W  #$C300,LED_ADDRESS

        JMP MenuLoop
        RTE

SERVICE_DIV0:
        MOVE.W  #$C400,LED_ADDRESS
        RTE
SERVICE_CHECK:
        MOVE.W  #$C500,LED_ADDRESS
        RTE
SERVICE_TRAPV:
        MOVE.W  #$C600,LED_ADDRESS
        RTE
SERVICE_PRIV:
        MOVE.W  #$C700,LED_ADDRESS
        RTE
SERVICE_TRACE:
        MOVE.W  #$C800,LED_ADDRESS
        RTE
SERVICE_LINE_A:
        MOVE.W  #$C900,LED_ADDRESS
        RTE
SERVICE_LINE_F:
        MOVE.W  #$CA00,LED_ADDRESS
        RTE
TRAP0_HANDLER:
TRAP2_HANDLER:
TRAP3_HANDLER:
TRAP4_HANDLER:
TRAP5_HANDLER:
TRAP6_HANDLER:
TRAP7_HANDLER:
TRAP8_HANDLER:
TRAP9_HANDLER:
TRAPA_HANDLER:
TRAPB_HANDLER:
TRAPC_HANDLER:
TRAPD_HANDLER:
TRAPE_HANDLER:
TRAPF_HANDLER:
        RTE

; --------------------------------
; Handler do TRAP #1
; Entrada:
;   D0.W - Número da função
;   D1.L - Parâmetro (para escrita)
; Saída:
;   D0.L - Resultado (para leitura)
; --------------------------------
TRAP1_HANDLER:
    cmp.w   #1,d0         ; Compara com CCONIN (ler caractere)
    BEQ     trap_cconin    ; Se for 1, vai para leitura
    cmp.w   #2,d0         ; Compara com CCONOUT (escrever caractere)
    BEQ     trap_cconout   ; Se for 2, vai para escrita
    cmp.w   #3,d0         ; Compara com CCONOUT (escrever string)
    BEQ     trap_strout   ; Se for 2, vai para escrita
    cmp.w   #0,d0         ; Compara com PTERM0 (terminar)
    BEQ     trap_pterm0    ; Se for 0, vai para terminar
    move.l  #-1,d0        ; Retorna erro se função não reconhecida
    RTE                   ; Retorna da exceção



; --------------------------------
; TRAP_CCONIN - Ler caractere do console
; Saída: D0.L - Caractere lido
; --------------------------------
trap_cconin:
    JSR         UART_ReadCharNonEcho
    ANDI.L      #$FF,D0       ; Mantém apenas o byte inferior
    RTE                   ; Retorna da exceção

; --------------------------------
; TRAP_CCONOUT - Escrever caractere no console
; Entrada: D1.L - Caractere a escrever
; --------------------------------
trap_cconout:
    ANDI.L      #$FF,D1         ; Mantém apenas o byte inferior
    MOVE.B      D1,D0
    JSR         UART_WriteChar
    RTE                   ; Retorna da exceção

trap_strout:
    MOVE.B      (A0)+,D0
    CMP.B       #0,D0
    BEQ         .fim
    JSR         UART_WriteChar
    BRA         trap_strout
.fim:
    RTE

; --------------------------------
; TRAP_PTERM0 - Terminar programa
; --------------------------------
trap_pterm0:
    move.w  #0,d0         ; Código de saída 0
    bsr     hardware_exit ; Chama rotina de término
    RTE                   ; Retorna da exceção (nunca executado)

; --------------------------------
; hardware_exit - Terminar execução
; Entrada: D0.W - Código de saída
; --------------------------------
hardware_exit:
    ; >>> ADAPTE PARA SUA PLACA <<<
    ; Exemplo: parar o processador
    ; stop    #$2700

    ; Exemplo simples: loop infinito
    BRA     hardware_exit
    RTS


    ALIGN 2
; =====================================================================
; END XMODEM RECEIVER ROUTINE
; =====================================================================

; ----------------------------------------------------------------------
; SECTION data
;-----------------------------------------------------------------------
    SECTION .rodata
    SECTION .data
    DC.B "Valores",0
cls_str:   dc.b    27,'[2J',0   ; \x1b = 27 (ASCII para ESC)
; ----------------------------------------------------------------------
; Strings do Sistema
; ----------------------------------------------------------------------
DumpHeader:
    DC.B    "Memory Dump from :",0
DumpHeader1:
    DC.B    "Address   00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  ASCII",13,10
    DC.B    "--------  -----------------------------------------------  ----------------",13,10,0
MSGINIT:
    DC.B    13,10,"Tcpbox68k - copyright (C) pdsilva(pgordao).V1.0",13,10
    DC.B    "MC68000 System Monitor",13,10
    INCLUDE "build_date.inc"
    INCLUDE "build_counter.inc"
    DC.B    "-------------------------------------------",13,10,13,10,0
MenuText:
    DC.B    "1. Select UART",13,10
    DC.B    "2. Set Baud Rate",13,10
    DC.B    "3. Load Program (PC)",13,10
    DC.B    "4. Write Program (Hex)",13,10
    DC.B    "5. Run Program",13,10
    DC.B    "6. Acendendo os LEDs",13,10
    DC.B    "7. Memory dump from address buffer",13,10
    DC.B    "8. Read hexa value and put in address buffer",13,10
    DC.B    "9. From screen to buffer E from buffer to screen",13,10
    DC.B    "0. Do baud divisor calculation",13,10
    DC.B    "> ",0
UARTPrompt:
    DC.B    "UART Address (2000/2100/2200/2300): ",0
BaudPrompt:
    DC.B    "Baud Rate Value: ",0
LoadPrompt:
    DC.B    "Aguardando 68ksender to initiate: ",0
LoadPromptReady:
    DC.B    "Ready to receive from PC!",0
LoadDoneMsg:
    DC.B    "Program loaded successfully!",13,10,0
WritePrompt:
    DC.B    "Write Address: ",0
WriteSizePrompt:
    DC.B    "Write your program or . to finish ",13,10,0
WriteDoneMsg:
    DC.B    13,10,"Data written to memory!",13,10,0
RunPrompt:
    DC.B    13,10,"Running program...",13,10,0
NO_PROGRAM_TO_RUN:
    DC.B    "No program loaded to run",13,10,0
PromptNotImplemented:
    DC.B    "Not Implemented!",13,10,0
BufferEmpty:
    DC.B    "Ooops Buffer Empty!",13,10,0
TestHexInput:
    DC.B    13,10,"Digite um endereco de no maximo 4bytes 8 caracteres!",13,10
    DC.B    "mais que isso sera descatado os excedentes...",13,10,0
HitAnyKey:
    DC.B    13,10,"Hit any <ENTER> to continue <ESC> to terminate: ",0
XmodemInit:
    DC.B    "XMODEM Receiver Initialized",13,10,0
XmodemWaitingSoh:
    DC.B    "Waiting for SOH (Start of Header)...",13,10,0
Msg_Cs:
    DC.B    "Checksum ROM.: ",0
Msg_Cscalc:
    DC.B    " - Checksum CAL.: ",0
Msg_default_handler:
    DC.B    " Default handler wrote UART ",13,10,0
Msg_via_trap1:
    DC.B    "Mensagem via trap #1",13,10,0

    ALIGN   2
    ;Isso preenche 762 com 00
    ;DS.B    $00000762 - *, $00
    DC.B    "ROMv4.0",0   ; String de identificação
    ;DS.B    $00002968 - *, $00
    ORG     $3FFC
checksum_rom:
    DC.L    0     ; Valor calculado

; ----------------------------------------------------------------------
; SECTION bss
;-----------------------------------------------------------------------
    SECTION .bss
    ORG     RAMBASE               ; Área para variáveis
RomBase:            DS.L 1
RomSize:            DS.L 1
RamBase:            DS.L 1
RamSize:            DS.L 1
CurrentUART:        DS.L 1
CurrentBaudRate:    DS.W 1
BaudDivL:           DS.W 1
BaudDivH:           DS.W 1
Baud1DivL:          DS.W 1
Baud1DivH:          DS.W 1
CurrentTimer:       DS.L 1
; === Buffer circular for uart (256 bytes) ===
addressInHex:       DS.L 1     ; ENDEREÇO LIDO
BUFFER_HEAD:        DS.L 1     ; Ponteiro de escrita (próxima posição livre)
BUFFER_TAIL:        DS.L 1     ; Ponteiro de leitura (próximo dado a ler)
BUFFER_COUNT:       DS.W 1     ; Contador de bytes no buffer
BUFFER:             DS.B 256   ; Buffer de recepção
;=== System variables
xmodem_buffer       DS.B   512        ; Buffer de dados
block_number        DS.B   1           ; Número do bloco atual
expected_block      DS.B   1           ; Próximo bloco esperado
usr_buffer_addr     DS.B   512
checksum_calc       DS.L   1
flag_pgm_loaded     DS.B   1
minhas_flags        DS.L   1

        ORG $00082000
        ALIGN 2
pgm_buffer          DS.B   8192
        END

