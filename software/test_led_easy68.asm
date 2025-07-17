; Programa de teste para placa MC68000
; Sintaxe com $ para valores hexadecimais


START   ORG $1000
        bra     MAIN            ; Pula para o código principal

; Vetores de inicialização
VECTOR_INIT:
        move.l    #$00880000,   a7          ; SP inicial
        jmp        MAIN                           ; PC inicial
        bra         ERROR_HANDLER       ; Vetor de bus error
        bra         ERROR_HANDLER       ; Vetor de address error

MAIN:
        move.l  #$00880000,a7  ; Inicializa stack pointer
      
      ;Clear leds
        move.l        d1,     0
        move.w      d1,     $00E00010  ; Endereço dos LEDs ($00E00010  )

        ; Teste simples de RAM
        move.l      #$A5A5A5A5,   d0
        move.l      d0,     $00080000   ; Endereço da RAM ($80000)
        move.l      $00080000,       d1   ; Lê de volta
        cmp.l        d0,                   d1
        bne           ERROR_HANDLER   ; Se diferente, vai para erro

        ; Loop principal - animação nos LEDs
LED_LOOP:
        move.w      #$0100,     d1      ; Padrão inicial
        move.w      #8,            d2          ; Número de LEDs

LED_ANIMATE:
        move.w      d1,     $00E00010  ; Endereço dos LEDs ($00E00010  )
        rol.w           #1,     d1           ; Rotaciona o padrão

        ; Delay loop (ajuste conforme clock)
        move.l        #1000,     d3
DELAY:
        subq.l         #1,     d3
        bne            DELAY

        dbra           d2,      LED_ANIMATE
        bra             LED_LOOP


; Manipulador de erros (pisca LEDs)
ERROR_HANDLER:
        move.w  #$AAAA,d4
ERROR_LOOP:
        move.w  d4,$00E00010     ; Endereço dos LEDs ($00E00010  )
        eori.w  #$FFFF,d4
        move.l  #3200000,d5
ERROR_DELAY:
        subq.l  #1,d5
        bne     ERROR_DELAY
        bra     ERROR_LOOP


         END     START
