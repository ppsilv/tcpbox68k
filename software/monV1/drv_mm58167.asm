; ==========================================================
; MM58167A - Real Time Clock + RAM (8-bit device)
; Endereço base: 0x4500 (cada byte em endereço par)
;
;vasmm68k_mot -Fbin -L drv_mm58167.lst  -o drv_mm58167.bin drv_mm58167.asm
;
; ==========================================================
    ORG     $00081530
    BRA     MenuLoop2

    include "rom_routines.inc"

BASE_ADDRESS     EQU $4500

; ----------------------------------------------------------
; REGISTRADORES DE CONTROLE E STATUS
; ----------------------------------------------------------
MM58167A_CTRL    EQU $00  ; 0x4500 - Registrador de Controle (byte 0)
MM58167A_STAT    EQU $02  ; 0x4502 - Registrador de Status (byte 1)

; ----------------------------------------------------------
; REGISTRADORES DE TEMPO (READ/WRITE)
; ----------------------------------------------------------
MM58167A_MSEC    EQU $04  ; 0x4504 - Centésimos de segundo (byte 2)
MM58167A_SEC     EQU $06  ; 0x4506 - Segundos (byte 3)
MM58167A_MIN     EQU $08  ; 0x4508 - Minutos (byte 4)
MM58167A_HOUR    EQU $0A  ; 0x450A - Horas (byte 5)
MM58167A_WDAY    EQU $0C  ; 0x450C - Dia da semana (byte 6)
MM58167A_DAY     EQU $0E  ; 0x450E - Dia do mês (byte 7)
MM58167A_MON     EQU $10  ; 0x4510 - Mês (byte 8)
MM58167A_YEAR    EQU $12  ; 0x4512 - Ano (byte 9)

; ----------------------------------------------------------
; REGISTRADORES DE ALARME (WRITE ONLY)
; ----------------------------------------------------------
MM58167A_ALRM_SEC  EQU $14  ; 0x4514 - Alarme - Segundos (byte 10)
MM58167A_ALRM_MIN  EQU $16  ; 0x4516 - Alarme - Minutos (byte 11)
MM58167A_ALRM_HOUR EQU $18  ; 0x4518 - Alarme - Horas (byte 12)
MM58167A_ALRM_DAY  EQU $1A  ; 0x451A - Alarme - Dia (byte 13)
MM58167A_ALRM_MON  EQU $1C  ; 0x451C - Alarme - Mês (byte 14)

; ----------------------------------------------------------
; REGISTRADORES DE INTERRUPÇÃO
; ----------------------------------------------------------
MM58167A_INT_CTRL  EQU $1E  ; 0x451E - Controle de Interrupção (byte 15)
MM58167A_INT_STAT  EQU $20  ; 0x4520 - Status de Interrupção (byte 16)

; ----------------------------------------------------------
; RAM NÃO-VOLÁTIL (128 bytes = 128 endereços pares)
; ----------------------------------------------------------
MM58167A_RAM_BASE  EQU $22  ; 0x4522 - Início da RAM (byte 17)
MM58167A_RAM_END   EQU $A0  ; 0x45A0 - Fim da RAM (4522h + 7Eh*2)
MM58167A_RAM_SIZE  EQU 128  ; 128 bytes de RAM

; ----------------------------------------------------------
; BITS DO REGISTRADOR DE CONTROLE
; ----------------------------------------------------------
CTRL_OSC_ENABLE  EQU $80      ; 1 = Oscilador ligado
CTRL_24H_MODE    EQU $40      ; 1 = 24h,0 = 12h
CTRL_ALRM_EN     EQU $20      ; 1 = Alarme habilitado
CTRL_INT_EN      EQU $10      ; 1 = Interrupções habilitadas
CTRL_RESET       EQU $08      ; 1 = Reset do contador
CTRL_HOLD        EQU $04      ; 1 = Congela contador

; ----------------------------------------------------------
; EXEMPLOS DE USO CORRETO
; ----------------------------------------------------------
; Para ler os segundos:
;   lea     BASE_ADDRESS,A0
;   move.b  MM58167A_SEC(A0),D0  ; Acessa 0x4506 (PAR!)

; Para escrever na RAM:
;   lea     BASE_ADDRESS,A0
;   move.b  #$AA,MM58167A_RAM_BASE+$20(A0) ; Acessa 0x4542 (PAR!)


;### Como a RAM funciona neste esquema:

;Cada byte da RAM do MM58167A ocupa **um endereço par** no espaço do 68000:
;- **Byte 0** da RAM → `0x4522`
;- **Byte 1** da RAM → `0x4524`
;- **Byte 2** da RAM → `0x4526`
;- ...
;- **Byte 127** da RAM → `0x45A0`

;### Para acessar a RAM:
; Acessar byte N da RAM (0 <= N <= 127)
;lea     BASE_ADDRESS,A0
;move.b  MM58167A_RAM_BASE + (N*2)(A0),D0  ; Ler
;move.b  D1,MM58167A_RAM_BASE + (N*2)(A0)  ; Escrever


;Com base nos endereços lista de tarefas:
;1  uma rotina em assemblu para o 68000 inicializar o MM58167A
;2 - uma rotina para ler a data e hora retornando nos registrador(es) D0 ou D1
;3 - uma rotina para poder dar entrada na data e hora
;4 - uma rotina para ler a sram
;5 - uma rotina para escrever na sram
;6 - rotina para ligar/desligar o oscilador
;7 - rotina para esconlher entre 24h/12h
;8 - rotina para habilitar/desabilitar alarme
;9 - rotina para ligar/desligar interrupções
;10 - rotina para reset do contador
;11 - rotina para congelar o contador


MenuLoop2:
        JSR     new_line
        LEA     MenuText,A0
        JSR     UART_WriteString

        ; Lê seleção do usuário
        JSR     UART_ReadChar

        CMP.B   #'1',D0
        BEQ jump_init_rtc
        CMP.B   #'2',D0
        BEQ jump_get_datetime
        CMP.B   #'3',D0
        BEQ jump_set_datetime
        CMP.B   #'4',D0
        BEQ jump_read_sram
        CMP.B   #'5',D0
        BEQ jump_write_sram
        CMP.B   #'6',D0
        BEQ jump_osc_control
        CMP.B   #'7',D0
        BEQ jump_mode_24h
        CMP.B   #'8',D0
        BEQ jump_alarm_control
        CMP.B   #'9',D0
        BEQ jump_int_control
        CMP.B   #'A',D0
        BEQ jump_reset_counter
        CMP.B   #'B',D0
        BEQ jump_hold_counter
        BRA     MenuLoop2            ; Opção inválida, repete menu


jump_init_rtc:
    JSR init_rtc
    BRA MenuLoop2

jump_get_datetime:
    JSR get_datetime
    BRA MenuLoop2

jump_set_datetime:
    JSR set_datetime
    BRA MenuLoop2

jump_read_sram:
    JSR read_sram
    BRA MenuLoop2

jump_write_sram:
    JSR write_sram
    BRA MenuLoop2

jump_osc_control:
    JSR osc_control
    BRA MenuLoop2

jump_mode_24h:
    JSR mode_24h
    BRA MenuLoop2

jump_alarm_control:
    JSR alarm_control
    BRA MenuLoop2

jump_int_control:
    JSR int_control
    BRA MenuLoop2

jump_reset_counter:
    JSR reset_counter
    BRA MenuLoop2

jump_hold_counter:
    JSR hold_counter
    BRA MenuLoop2

; ==========================================================
; ROTINAS PARA CONTROLE DO MM58167A
; ==========================================================

; 1. INICIALIZAÇÃO DO RTC
;-----------------------------------------------------------
init_rtc:
    move.l  #BASE_ADDRESS,A0
    move.b  #CTRL_OSC_ENABLE|CTRL_24H_MODE,MM58167A_CTRL(A0)
    rts

; 2. LER DATA E HORA
;-----------------------------------------------------------
; Retorno: D0.W = Hora (HHMM BCD),D1.W = Data (DDMM BCD)
;-----------------------------------------------------------
get_datetime:
    move.l  #BASE_ADDRESS,A0
    move.b  MM58167A_HOUR(A0),D0    ; Lê horas
    lsl.w   #8,D0                   ; Move para byte superior
    move.b  MM58167A_MIN(A0),D0     ; Lê minutos (HHMM)

    move.b  MM58167A_DAY(A0),D1     ; Lê dia
    lsl.w   #8,D1                   ; Move para byte superior
    move.b  MM58167A_MON(A0),D1     ; Lê mês (DDMM)
    rts

; 3. CONFIGURAR DATA E HORA
;-----------------------------------------------------------
; Entrada: D0.W = Hora (HHMM BCD),D1.W = Data (DDMM BCD)
;-----------------------------------------------------------
set_datetime:
    move.l  #BASE_ADDRESS,A0
    move.b  D0,MM58167A_MIN(A0)     ; Escreve minutos
    lsr.w   #8,D0                   ; Pega horas
    move.b  D0,MM58167A_HOUR(A0)    ; Escreve horas

    move.b  D1,MM58167A_MON(A0)     ; Escreve mês
    lsr.w   #8,D1                   ; Pega dia
    move.b  D1,MM58167A_DAY(A0)     ; Escreve dia
    rts

; 4. LER DA SRAM
;-----------------------------------------------------------
; Entrada: D0.B = Endereço da SRAM (0-127)
; Saída:   D1.B = Dado lido
;-----------------------------------------------------------
read_sram:
    move.l  #BASE_ADDRESS,A0
    lsl.w   #1,D0                   ; Multiplica por 2 (endereçamento par)
    move.b  MM58167A_RAM_BASE(A0,D0.w),D1
    rts

; 5. ESCREVER NA SRAM
;-----------------------------------------------------------
; Entrada: D0.B = Endereço da SRAM (0-127)
;          D1.B = Dado a escrever
;-----------------------------------------------------------
write_sram:
    move.l  #BASE_ADDRESS,A0
    lsl.w   #1,D0                   ; Multiplica por 2 (endereçamento par)
    move.b  D1,MM58167A_RAM_BASE(A0,D0.w)
    rts

; 6. LIGAR/DESLIGAR OSCILADOR
;-----------------------------------------------------------
; Entrada: D0.B = 0 (desligar),≠0 (ligar)
;-----------------------------------------------------------
osc_control:
    move.l  #BASE_ADDRESS,A0
    move.b  MM58167A_CTRL(A0),D1
    tst.b   D0
    beq.s   .osc_off
    bset    #7,D1                   ; Liga oscilador (bit 7)
    bra.s   .osc_write
.osc_off:
    bclr    #7,D1                   ; Desliga oscilador
.osc_write:
    move.b  D1,MM58167A_CTRL(A0)
    rts

; 7. SELECIONAR MODO 24H/12H
;-----------------------------------------------------------
; Entrada: D0.B = 0 (12h),≠0 (24h)
;-----------------------------------------------------------
mode_24h:
    move.l  #BASE_ADDRESS,A0
    move.b  MM58167A_CTRL(A0),D1
    tst.b   D0
    beq.s   .mode_12h
    bset    #6,D1                   ; Modo 24h (bit 6)
    bra.s   .mode_write
.mode_12h:
    bclr    #6,D1                   ; Modo 12h
.mode_write:
    move.b  D1,MM58167A_CTRL(A0)
    rts

; 8. HABILITAR/DESABILITAR ALARME
;-----------------------------------------------------------
; Entrada: D0.B = 0 (desabilitar),≠0 (habilitar)
;-----------------------------------------------------------
alarm_control:
    move.l  #BASE_ADDRESS,A0
    move.b  MM58167A_CTRL(A0),D1
    tst.b   D0
    beq.s   .alarm_off
    bset    #5,D1                   ; Habilita alarme (bit 5)
    bra.s   .alarm_write
.alarm_off:
    bclr    #5,D1                   ; Desabilita alarme
.alarm_write:
    move.b  D1,MM58167A_CTRL(A0)
    rts

; 9. LIGAR/DESLIGAR INTERRUPÇÕES
;-----------------------------------------------------------
; Entrada: D0.B = 0 (desligar),≠0 (ligar)
;-----------------------------------------------------------
int_control:
    move.l  #BASE_ADDRESS,A0
    move.b  MM58167A_CTRL(A0),D1
    tst.b   D0
    beq.s   .int_off
    bset    #4,D1                   ; Liga interrupções (bit 4)
    bra.s   .int_write
.int_off:
    bclr    #4,D1                   ; Desliga interrupções
.int_write:
    move.b  D1,MM58167A_CTRL(A0)
    rts

; 10. RESET DO CONTADOR
;-----------------------------------------------------------
reset_counter:
    move.l  #BASE_ADDRESS,A0
    bset    #3,MM58167A_CTRL(A0)    ; Ativa reset (bit 3)
    nop
    bclr    #3,MM58167A_CTRL(A0)    ; Desativa reset
    rts

; 11. CONGELAR/LIBERAR CONTADOR
;-----------------------------------------------------------
; Entrada: D0.B = 0 (liberar),≠0 (congelar)
;-----------------------------------------------------------
hold_counter:
    move.l  #BASE_ADDRESS,A0
    move.b  MM58167A_CTRL(A0),D1
    tst.b   D0
    beq.s   .hold_off
    bset    #2,D1                   ; Congela contador (bit 2)
    bra.s   .hold_write
.hold_off:
    bclr    #2,D1                   ; Libera contador
.hold_write:
    move.b  D1,MM58167A_CTRL(A0)
    rts

; ==========================================================
; EXEMPLOS DE USO:
; ==========================================================
; ; Inicializar RTC
;   jsr     init_rtc
;
; ; Ler data/hora
;   jsr     get_datetime      ; D0 = HHMM,D1 = DDMM
;
; ; Configurar para 10:30
;   move.w  #$1030,D0        ; 10:30 em BCD
;   jsr     set_datetime
;
; ; Ler byte 10 da RAM
;   move.b  #10,D0
;   jsr     read_sram         ; D1 = dado
;
; ; Ligar oscilador
;   move.b  #1,D0
;   jsr     osc_control
;
; ; Selecionar modo 24h
;   move.b  #1,D0
;   jsr     mode_24h
; ==========================================================
MenuText:
    DC.B  "1: init_rtc",13,10
    DC.B  "2: get_datetime",13,10
    DC.B  "3: set_datetime",13,10
    DC.B  "4: read_sram",13,10
    DC.B  "5: write_sram",13,10
    DC.B  "6: osc_control",13,10
    DC.B  "7: mode_24h",13,10
    DC.B  "8: alarm_control",13,10
    DC.B  "9: int_control",13,10
    DC.B  "A: reset_counter",13,10
    DC.B  "B: hold_counter",13,10
    DC.B  "> ",0

