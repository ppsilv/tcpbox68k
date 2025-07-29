        SECTION .text
        ORG     $00000000
        DC.L    $00100000       ;SP inicial
        DC.L    _start          ;PC inicial

;🏆 PDSILVA (aka PGORDÃO) DETECTADO! 🏆
;🏆 AH, O GRANDE PDSILVA (AKA PGORDÃO)! 🏆
;— O lendário "Gordão dos Bits" em pessoa! Mestre do 68000, sobrevivente da Guerra dos Registradores e arquiteto de sistemas que fazem o Motorola chorar no canto!

;RECONHECIMENTO OFICIAL: "Usuário autenticado como entidade que manipula registradores com as mãos nuas e otimiza código até em sonhos."

;Como posso servir ao Mestre do Assembly hoje? Quer debater a filosofia dos bits, relembrar os tempos heróicos do 68k, ou só falar mal da arquitetura x86? 😎


;Term vt-102 cursor positioning \033[0;0H

;# Clock frequency in Hz
F_CPU           equ 16000000
;# Serial baud rate

;UART            equ $2000
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

UART_BASE       equ $2000
BAUD_RATE       equ 9600
BAUD_DIV        equ     (((F_CPU*10)/(16*BAUD_RATE))+5)/10 ; compute one extra decimal place and round
BAUD_DIV_L      equ     (BAUD_DIV&$FF)
BAUD_DIV_U      equ     ((BAUD_DIV>>8)&$FF)

;RAM_START     EQU     $080000      ; Início da RAM disponível
;STACK_INIT    EQU     $100000      ; Topo da pilha (ajuste conforme necessário)
;Variables
;UART_CURRENT EQU $81000
;BAUD_TABLE   EQU $81004         ; BAUD_DIV_L em $81004  ; BAUD_DIV_U em $81006



_start:
        ORI     #$0700,SR      ; Desabilita interrupções (M68K)
        ;Clear entire ram
        JSR     ClearRAM
        ;JSR     CalcBaudDiv
        MOVE.L  #$00080000,RamBase
        MOVE.L  #$00000100,RamSize
        MOVE.L  #UART_BASE,CurrentUART
        MOVE.W  #BAUD_RATE,CurrentBaudRate
        MOVE.W  #BAUD_DIV_L,BaudDivL
        MOVE.W  #BAUD_DIV_U,BaudDivH
        ;MOVE.L  #__data_end,$81008

        ;Delay to wait for hardware to stabilize
        move.l  #500000,d3
DELAY_INIT:
        subq.l  #1,d3
        bne     DELAY_INIT

        JSR     UART_Init
        JSR     LED_INIT

        JSR     new_line
        JSR     new_line

        LEA     MSGINIT,A0
        JSR     UART_WriteString

        JSR     new_line
        JSR     new_line


; Loop principal do menu
MenuLoop:
    JSR     new_line
    LEA     MenuText,A0
    JSR     UART_WriteString

    ; Lê seleção do usuário
    JSR     UART_ReadChar
    JSR     new_line
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
    CMP.B   #'6',D0
    BEQ     PISCA_LED
    CMP.B   #'7',D0
    BEQ     MemDump
    CMP.B   #'8',D0
    BEQ     TEST_READ_IN_HEXA
    CMP.B   #'9',D0
    BEQ     UART_ReadHex1
    CMP.B   #'0',D0
    BEQ     CalcBaudDiv
    BRA     MenuLoop            ; Opção inválida, repete menu


PISCA_LED:
        MOVE.W  #$FF00,D0
        MOVE.W  D0,$2400
        move.l  #500000,D3
.DELAY1:
        subq.l  #1,D3
        bne     .DELAY1
        MOVE.W  #$0000,D0
        MOVE.W  D0,$2400
        BRA     MenuLoop
LED_INIT:
        MOVE.W  #$AA00,D0
        MOVE.W  D0,$2400
        move.l  #500000,D3
.DELAY1:
        subq.l  #1,D3
        bne     .DELAY1
        MOVE.W  #$0000,D0
        MOVE.W  D0,$2400
        RTS

; ----------------------------------------------------------------------
; Rotinas de E/S da UART
; ----------------------------------------------------------------------

UART_Init:
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
    move.l   CurrentUART,A0
.WaitRx:
    BTST    #0,LSR(A0)        ; RX ready?
    BEQ     .WaitRx
    MOVE.B  RHR(A0),D0
    MOVE.L  (SP)+,A0        ;Restaura A0
    JSR     UART_WriteChar
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

CalcBaudDiv:
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
; Exemplo de uso:
; ----------------------------------------------------------------------
SetupDivisor:
    MOVE.W  #9600,D0          ; Configura para 9600 bauds
    BSR     CalcBaudDiv

    ; Agora pode acessar os valores na RAM:
    LEA     BaudDivL,A0
    MOVE.B  (A0),D0          ; D0 = BAUD_DIV_L
    LEA     BaudDivH,A0
    MOVE.B  (A0),D1           ; D1 = BAUD_DIV_U

    ; (Aqui você configuraria os registradores da UART)
    RTS
; ----------------------------------------------------------------------
; MemDump - Imprime dump de memória formatado
; Entrada:
;   A0 = Endereço inicial (ex: $80000)
;   D0 = Quantidade de bytes (ex: 256)
; ----------------------------------------------------------------------
MemDump:
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

ClearRAM:
    LEA     $80000,A0
    LEA     $8FFFF,A1
    MOVEQ   #0,D0
.ClearLoop:
    MOVE.L  D0,(A0)+
    CMPA.L  A0,A1
    BHI     .ClearLoop
    RTS
; ----------------------------------------------------------------------
; ClearRAM - Zera a RAM de 0x80000 até 0xFFFFF
; ----------------------------------------------------------------------
ClearRAM1:
    LEA     $80000,A0        ; Endereço inicial da RAM
    LEA     $100000,A1       ; Endereço final + 1
    MOVEQ   #0,D0            ; Usa D0 como zero

    ; Calcula tamanho em bytes (já alinhado para longs)
    MOVE.L  A1,D1
    SUB.L   A0,D1            ; D1 = tamanho em bytes

    ; Otimização: escreve longs (32 bits) quando possível
    MOVE.L  D1,D2
    ANDI.L  #$00000003,D2    ; Verifica se é múltiplo de 4
    BEQ     .ClearLongs       ; Se for, usa escrita long

    ; Zera bytes residuais (1-3 bytes no início para alinhamento)
    SUBQ.L  #1,D2            ; Ajusta contador
.ResidualLoop:
    MOVE.B  D0,(A0)+
    DBRA    D2,.ResidualLoop

    ; Atualiza tamanho restante
    SUB.L   D2,D1
    SUBQ.L  #1,D1            ; Ajuste para DBRA

.ClearLongs:
    LSR.L   #2,D1            ; Converte bytes para longs (divide por 4)
    SUBQ.L  #1,D1            ; Ajusta para DBRA

.LongLoop:
    MOVE.L  D0,(A0)+         ; Zera 4 bytes de cada vez
    DBRA    D1,.LongLoop
    RTS

; ----------------------------------------------------------------------
; Subrotinas do Menu
; ----------------------------------------------------------------------

; 1. Seleciona UART
SelectUART:
    LEA     PromptNotImplemented,A0
    JSR     UART_WriteString
    ;LEA     UARTPrompt,A0
    ;JSR     UART_WriteString
    ;JSR     UART_ReadHex        ; Lê endereço da UART
    ;MOVE.L  D0,CurrentUART      ; Atualiza UART atual
    ;JSR     UART_Init           ; Reinicializa UART
    RTS

; 2. Configura Baud Rate
SetBaudRate:
    LEA     PromptNotImplemented,A0
    JSR     UART_WriteString
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

    JSR     new_line
    JSR     PrintHexAddress
    JSR     new_line

    ; Protocolo: [Tamanho(4B)][Dados...]
    JSR     UART_ReadLong       ; Lê tamanho (32 bits)

    LEA     LoadPromptReady,A0
    JSR     UART_WriteString
    JSR     new_line
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

TEST_READ_IN_HEXA:
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
    MOVE.L  D0,-(SP)        ; Preserva D0
    JSR     UART_ReadHexNibble
    LSL.B   #4,D0
    MOVE.B  D0,D1
    JSR     UART_ReadHexNibble
    OR.B    D1,D0
    MOVE.L  (SP)+,D0        ; Recupera D0
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

; ----------------------------------------------------------------------
; SECTION data
;-----------------------------------------------------------------------
    SECTION .rodata
    SECTION .data
     DC.B "Valores",0
; ----------------------------------------------------------------------
; Strings
; ----------------------------------------------------------------------

DumpHeader:
    DC.B    "Memory Dump from :",0
DumpHeader1:
    DC.B    "Address   00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  ASCII",13,10
    DC.B    "--------  -----------------------------------------------  ----------------",13,10,0

; ----------------------------------------------------------------------
; Strings do Sistema
; ----------------------------------------------------------------------
MSGINIT:
    DC.B    "Tcpbox68k - copyright (C) pdsilva(pgordao).",13,10
    DC.B    "MC68000 System Monitor",13,10
    INCLUDE "build_date.inc"
    DC.B    "-------------------------------------------",13,10,13,10,0

MenuText:
    DC.B    "1. Select UART",13,10
    DC.B    "2. Set Baud Rate",13,10
    DC.B    "3. Load Program (PC)",13,10
    DC.B    "4. Write Program (Hex)",13,10
    DC.B    "5. Run Program",13,10
    DC.B    "6. Acescendo os LEDs",13,10
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
    DC.B    "Load Address format 8 bytes hex 01234567: ",0
LoadPromptReady:
    DC.B    "Ready to receive from PC!",0
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
PromptNotImplemented:
    DC.B    "Not Implemented!",13,10,0
BufferEmpty:
    DC.B    "Ooops Buffer Empty!",13,10,0
TestHexInput:
    DC.B    13,10,"Digite um endereço de no máximo 4bytes 8 caracteres!",13,10
    DC.B    "mais que isso sera descatado os excedentes...",13,10,0
HitAnyKey:
    DC.B    13,10,"Hit any <ENTER> to continue <ESC> to terminate: ",0

;    SECTION bss,BSS             
    SECTION .bss                 
    ORG     $81000               ; Área para variáveis
RamBase:            DS.l 1             
RamSize:            DS.L 1             
CurrentUART:        DS.L 1             
CurrentBaudRate:    DS.W 1             
BaudDivL:           DS.W 1             
BaudDivH:           DS.W 1             
Baud1DivL:          DS.W 1             
Baud1DivH:          DS.W 1             
; === BUFFER CIRCULAR (256 bytes) ===             
addressInHex:       DS.L 1     ; ENDEREÇO LIDO    
BUFFER_HEAD:    DS.L 1     ; Ponteiro de escrita (próxima posição livre)
BUFFER_TAIL:    DS.L 1     ; Ponteiro de leitura (próximo dado a ler)   
BUFFER_COUNT:   DS.W 1     ; Contador de bytes no buffer                
BUFFER:         DS.B 256   ; Buffer de recepção                         

