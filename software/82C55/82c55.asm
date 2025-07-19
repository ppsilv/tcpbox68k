; Programa para controlar o 82C55 com MC68000
; Compilar com: vasmm68k_mot -Fbin -o output.bin 82c55.asm

        org $1000

; Endereços do 82C55
PPI_PORTA equ $E00000  ; Porta A
PPI_PORTB equ $E00002  ; Porta B
PPI_PORTC equ $E00004  ; Porta C
PPI_CTRL  equ $E00006  ; Registro de controle

Start:
        ; Configurar 82C55:
        ; - Porta A = Saída (Mode 0)
        ; - Porta B = Entrada (Mode 0)
        ; - Porta C (alto) = Saída, Porta C (baixo) = Entrada
        move.b #%10000010,d0       ; Byte de controle: 10000010 (bin) = $82
        move.b d0,PPI_CTRL   ; SEM ESPAÇO EXTRA!

MainLoop:
        ; Escrever $FF na Porta A (todos HIGH)
        move.b #$FF,d0
        move.b d0,PPI_PORTA

        ; Ler Porta B e armazenar em D1
        move.b PPI_PORTB,d1

        ; Escrever valor lido na parte alta da Porta C
        and.b #$F0,d1        ; Máscara para bits 4-7
        move.b d1,PPI_PORTC

        ; Delay simples
        move.l #$FFFF,d2
DelayLoop:
        subq.l #1,d2
        bne DelayLoop

        bra MainLoop

        end Start
