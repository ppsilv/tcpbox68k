; =====================================================================
; XMODEM RECEIVER PARA 68K (PGORDÃO EDITION)
;
; Características:
; - Suporta XMODEM padrão (128-byte blocks)
; - Checksum de 8-bit (ou CRC opcional)
; - Compatível com Minicom/Linux/macOS
; =====================================================================

                ; --- CONSTANTES ---
SOH            EQU     $01        ; Start Of Header
EOT            EQU     $04        ; End Of Transmission
ACK            EQU     $06        ; Acknowledge
NAK            EQU     $15        ; Negative Acknowledge
CAN            EQU     $18        ; Cancel

                ; --- VARIÁVEIS ---
                SECTION DATA
xmodem_buffer  DS.B    128        ; Buffer de dados
block_number   DS.B    1           ; Número do bloco atual
expected_block DS.B    1           ; Próximo bloco esperado

                ; --- CÓDIGO ---
                SECTION CODE
                XDEF    XMODEM_Receive

XMODEM_Receive:
                MOVEM.L D2-D7/A0-A6,-(SP)
                LEA     xmodem_buffer,A0

                ; ---- 1. INICIALIZAÇÃO ----
                MOVE.B  #NAK,D0
                BSR     UART_WriteChar      ; Solicita início

                ; ---- 2. LOOP PRINCIPAL ----
Receive_Loop:
                BSR     UART_ReadChar
                CMP.B   #EOT,D0
                BEQ     Transfer_Complete   ; Fim da transmissão

                CMP.B   #SOH,D0
                BNE     Receive_Loop        ; Ignora bytes inválidos

                ; ---- 3. RECEBE HEADER ----
                BSR     UART_ReadChar       ; Block number
                MOVE.B  D0,block_number
                BSR     UART_ReadChar       ; ~Block number (complemento)

                ; ---- 4. RECEBE DADOS ----
                MOVE.W  #127,D1             ; 128 bytes (0-based)
                LEA     xmodem_buffer,A1

Receive_Data:
                BSR     UART_ReadChar
                MOVE.B  D0,(A1)+
                DBF     D1,Receive_Data

                ; ---- 5. VERIFICA CHECKSUM ----
                BSR     UART_ReadChar       ; Checksum
                MOVE.B  D0,D2

                ; Calcula checksum local
                LEA     xmodem_buffer,A1
                MOVE.W  #127,D1
                CLR.B   D3

Calc_Checksum:
                ADD.B   (A1)+,D3
                DBF     D1,Calc_Checksum

                CMP.B   D2,D3
                BNE     Send_NAK            ; Erro no checksum

                ; ---- 6. VALIDA NÚMERO DO BLOCO ----
                MOVE.B  block_number,D0
                CMP.B   expected_block,D0
                BNE     Send_NAK            ; Bloco fora de ordem

                ; ---- 7. COPIA DADOS VÁLIDOS ----
                ; (Aqui você processa os 128 bytes recebidos)
                ; Exemplo: copiar para RAM/Flash
                LEA     xmodem_buffer,A1
                MOVE.L  user_buffer_ptr,A2  ; Defina isso antes de chamar
                MOVE.W  #127,D1
Copy_Data:
                MOVE.B  (A1)+,(A2)+
                DBF     D1,Copy_Data

                ; ---- 8. CONFIMA RECEPÇÃO ----
                ADDQ.B  #1,expected_block   ; Próximo bloco
                MOVE.B  #ACK,D0
                BSR     UART_WriteChar
                BRA     Receive_Loop

Send_NAK:
                MOVE.B  #NAK,D0
                BSR     UART_WriteChar
                BRA     Receive_Loop

Transfer_Complete:
                MOVE.B  #ACK,D0             ; Confirma EOT
                BSR     UART_WriteChar
                MOVEM.L (SP)+,D2-D7/A0-A6
                RTS

; --- ROTINAS UART (IMPLEMENTE!) ---
UART_ReadChar:
                ; (Seu código aqui)
                RTS

UART_WriteChar:
                ; (Seu código aqui)
                RTS

                END
