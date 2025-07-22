; ========================================================
; **drv_uart.asm**
; Driver para comunicação serial com 16C554 (16 MHz)
; Rotinas:
;   - ser_init()      → Inicializa UART
;   - cin()           → Leitura não-bloqueante (retorna Z=1 se não há dado)
;   - cin_wait()      → Leitura bloquante
;   - cout()          → Envia um caractere
;   - couts()         → Envia string (terminada em 0)
;   - printf()        → Envia string formatada (simples)
;   - scanf()         → Lê string até Enter (simples)
; ========================================================

; --- Definições dos registradores da 16C554 ---
UART_BASE    EQU   $00002000       ; Endereço base da UART (ajuste conforme seu hardware)
UART_RHR     EQU   UART_BASE+0               ; Receive Holding Register (leitura)
UART_THR     EQU   UART_BASE+0               ; Transmit Holding Register (escrita)
UART_IER     EQU   UART_BASE+1               ; Interrupt Enable Register
UART_IIR     EQU   UART_BASE+2               ; Interrupt Identification Register
UART_FCR     EQU   UART_BASE+2               ; FIFO Control Register
UART_LCR     EQU   UART_BASE+3               ; Line Control Register
UART_MCR     EQU   UART_BASE+4               ; Modem Control Register
UART_LSR     EQU   UART_BASE+5               ; Line Status Register
UART_MSR     EQU   UART_BASE+6               ; Modem Status Register
UART_SCR     EQU   UART_BASE+7               ; Scratch Register
UART_DLL     EQU   UART_BASE+0               ; Divisor Latch Low (quando LCR bit 7 = 1)
UART_DLM     EQU   UART_BASE+1               ; Divisor Latch High (quando LCR bit 7 = 1)

; --- Constantes ---
UART_BAUD_115200 EQU 8             ; Divisor para 115200 bps (16 MHz / (16 * 115200) ≈ 8.68 → 8)

; ========================================================
; **ser_init()**
; Inicializa a UART (115200 bps, 8N1, FIFO habilitado)
; ========================================================
ser_init:

    ; Configura baud rate (115200)
    MOVE.B   #0x80, UART_LCR(A0)   ; Habilita acesso a DLL/DLM (LCR bit 7 = 1)
    MOVE.B   #UART_BAUD_115200, UART_DLL(A0)  ; Configura divisor (low)
    MOVE.B   #0x00, UART_DLM(A0)   ; High byte do divisor = 0

    ; Configura formato 8N1
    MOVE.B   #0x03, UART_LCR(A0)   ; 8 bits, sem paridade, 1 stop bit (8N1)

    ; Habilita FIFO (opcional)
    MOVE.B   #0x01, UART_FCR(A0)   ; Habilita FIFO
    RTS

; ========================================================
; **cin()**
; Leitura **não-bloqueante** de um caractere
; Saída:
;   - D0.B = caractere lido (se Z=0)
;   - Z=1 se não há dado disponível
; ========================================================
cin:
    BTST     #0, UART_LSR(A0)      ; Testa bit DR (dado disponível?)
    BEQ.S    .no_data              ; Se não, retorna Z=1
    MOVE.B   UART_RHR(A0), D0      ; Lê o caractere
    ANDI.B   #$FF, D0              ; Garante que Z=0 se há dado
    RTS
.no_data:
    MOVEQ    #0, D0                ; Z=1 (nenhum dado)
    RTS

; ========================================================
; **cin_wait()**
; Leitura **bloqueante** de um caractere
; Saída:
;   - D0.B = caractere lido
; ========================================================
cin_wait:
    JSR      cin
    BEQ.S    cin_wait              ; Espera até ter dado
    RTS

; ========================================================
; **cout()**
; Envia um caractere pela serial
; Entrada:
;   - D0.B = caractere a enviar
; ========================================================
cout:

.wait_tx:
    BTST     #5, UART_LSR(A0)      ; Testa bit THRE (buffer vazio?)
    BEQ.S    .wait_tx              ; Espera até estar pronto
    MOVE.B   D0, UART_THR(A0)      ; Envia o caractere
    RTS

; ========================================================
; **couts()**
; Envia uma string terminada em 0
; Entrada:
;   - A0 = ponteiro para a string
; ========================================================
couts:
    MOVEM.L  D0/A0, -(A7)          ; Salva registradores
.loop:
    MOVE.B   (A0)+, D0             ; Pega próximo caractere
    BEQ.S    .end                  ; Se for 0, termina
    JSR      cout                  ; Envia caractere
    BRA.S    .loop                 ; Repete
.end:
    MOVEM.L  (A7)+, D0/A0          ; Restaura registradores
    RTS

; ========================================================
; **printf()**
; Envia uma string formatada (simples, sem suporte a %d, %x)
; Entrada:
;   - A0 = ponteiro para a string
; ========================================================
printf:
    JSR      couts                 ; Por enquanto, igual a couts()
    RTS                            ; (Pode ser expandido depois)

; ========================================================
; **scanf()**
; Lê uma string até Enter (simples)
; Entrada:
;   - A0 = ponteiro para o buffer
;   - D0.W = tamanho máximo do buffer
; Saída:
;   - Buffer preenchido com a string (terminada em 0)
; ========================================================
scanf:
    MOVEM.L  D0-D1/A0, -(A7)       ; Salva registradores
    MOVE.W   D0, D1                ; D1 = contador de caracteres
.loop:
    JSR      cin_wait              ; Lê um caractere
    CMPI.B   #$0D, D0              ; É Enter?
    BEQ.S    .end                  ; Se sim, termina
    CMPI.B   #$08, D0              ; É Backspace?
    BEQ.S    .backspace            ; Trata backspace
    MOVE.B   D0, (A0)+             ; Armazena no buffer
    SUBQ.W   #1, D1                ; Decrementa contador
    BEQ.S    .buffer_full          ; Se buffer cheio, termina
    JSR      cout                  ; Ecoa o caractere (terminal local)
    BRA.S    .loop
.backspace:
    CMPA.L   (A7), A0              ; Verifica se há caracteres para apagar
    BEQ.S    .loop                 ; Se não, ignora
    SUBQ.L   #1, A0                ; Volta uma posição
    ADDQ.W   #1, D1                ; Incrementa contador
    MOVE.B   #$08, D0              ; Backspace
    JSR      cout
    MOVE.B   #' ', D0              ; Espaço (apaga caractere)
    JSR      cout
    MOVE.B   #$08, D0              ; Backspace novamente
    JSR      cout
    BRA.S    .loop
.buffer_full:
    MOVE.B   #$07, D0              ; Beep (avisa buffer cheio)
    JSR      cout
.end:
    CLR.B    (A0)                  ; Termina string com 0
    MOVEM.L  (A7)+, D0-D1/A0       ; Restaura registradores
    RTS

; --- Fim do arquivo ---
