; ================================================
; ARQUIVO DE INCLUSÃO PARA ROTINAS DA ROM
; Compilado para RAM, mas acessa funções na ROM
; ================================================

    ORG     $00081530

; --- Endereços absolutos das rotinas na ROM ---
; (Substitua pelos endereços reais do seu hardware)

cold_start              EQU $00000000
UART_Init               EQU $00000400
UART_WriteChar          EQU $00000404
UART_ReadChar           EQU $00000408
UART_Select             EQU $0000040C
UART_Setbaudrate        EQU $00000410
DELAY_MS                EQU $00000414
MEMDUMP                 EQU $00000418
UART_ReadCharNonEcho    EQU $0000041C
_start                  EQU $00000420
warm_start              EQU $00000424
new_line                EQU $000013A8
UART_WriteString        EQU $00001308

; --- Macros para chamar as rotinas ---
; (Facilitam o uso sem precisar lembrar dos endereços)

WRITE_CHAR      MACRO
                move.l  \1,-(sp)    ; Empilha argumento
                jsr     UART_WriteChar
                addq.l  #4,sp       ; Limpa stack
                ENDM

READ_CHAR       MACRO
                jsr     UART_ReadChar
                ENDM

DELAY_MS        MACRO
                move.l  \1,-(sp)    ; Argumento: tempo em ms
                jsr     Delay_ms
                addq.l  #4,sp
                ENDM
;USO
; ================================================
; PROGRAMA PRINCIPAL (COMPILADO PARA RAM)
; ================================================
;    INCLUDE "rom_routines.inc"   ; Inclui as definições
;
;    ORG     $00082000            ; Endereço de carga na RAM
;
;Start:
;    MOVE.L  #'A',D0             ; Caractere para enviar
;    WRITE_CHAR D0               ; Usa a macro para UART_WriteChar
;
;    READ_CHAR                   ; Macro para UART_ReadChar (resultado em D0)
;
;    DELAY_MS #500               ; Delay de 500ms
;
;    BRA     Start
;
;    END
;
