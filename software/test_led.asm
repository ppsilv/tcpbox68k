; Programa de teste para placa MC68000
; Sintaxe com 0x para valores hexadecimais

        bra     MAIN            ; Pula para o código principal

; Vetores de inicialização
VECTOR_INIT:
        move.l  #0x00880000,a7  ; SP inicial
        jmp     MAIN            ; PC inicial
        bra     ERROR_HANDLER   ; Vetor de bus error
        bra     ERROR_HANDLER   ; Vetor de address error

MAIN:
        move.l  #0x00880000,a7  ; Inicializa stack pointer

        ; Teste simples de RAM
        move.l  #0xA5A5A5A5,d0
        move.l  d0,0x00080000   ; Endereço da RAM (0x80000)
        move.l  0x00080000,d1   ; Lê de volta
        cmp.l   d0,d1
        bne     ERROR_HANDLER   ; Se diferente, vai para erro

        ; Loop principal - animação nos LEDs
LED_LOOP:
        move.w  #0x0001,d1      ; Padrão inicial
        move.w  #16,d2          ; Número de LEDs

LED_ANIMATE:
        move.w  d1,0x00002000  ; Endereço dos LEDs (0x2000)
        rol.w   #1,d1           ; Rotaciona o padrão

        ; Delay loop (ajuste conforme clock)
        move.l  #160000,d3
DELAY:
        subq.l  #1,d3
        bne     DELAY

        dbra    d2,LED_ANIMATE
        bra     LED_LOOP

; Manipulador de erros (pisca LEDs)
ERROR_HANDLER:
        move.w  #0xAAAA,d4
ERROR_LOOP:
        move.w  d4,0x00002000   ; Endereço dos LEDs (0x2000)
        eori.w  #0xFFFF,d4
        move.l  #3200000,d5
ERROR_DELAY:
        subq.l  #1,d5
        bne     ERROR_DELAY
        bra     ERROR_LOOP

; Preenchimento com NOPs (exemplo)
FILLER:
        nop
        nop
        nop
        ; Continue adicionando NOPs até completar 8KB
