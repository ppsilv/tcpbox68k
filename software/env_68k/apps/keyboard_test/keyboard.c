#include <stdio.h>
#include <stdlib.h>

#include <mc68000.h>




#define UART_KEYBOARD 0x4300

#define RHR   0   // receive holding register (read)
#define THR   0   // transmit holding register (write)
#define IER   2   // interrupt enable register
#define ISR   4   // interrupt status register (read)
#define FCR   4   // FIFO control register (write)
#define LCR   6   // line control register
#define MCR   8   // modem control register
#define LSR   10  // line status register
#define MSR   12  // modem status register
#define SPR   14  // scratchpad register (reserved for system use)
#define DLL   0   // divisor latch LSB
#define DLM   2   // divisor latch MSB
// aliases for register names (used by different manufacturers)cd ..
#define RBR   RHR // receive buffer register
#define IIR   ISR // interrupt identification register
#define SCR   SPR // scratch register

unsigned char status = 0;

unsigned char get_keypress(); 

void delay(unsigned int time) {
    for (volatile unsigned int i = 0; i < time; i++);
}

#define BAUD_DIV_L  0x08 //(BAUD_DIV&$FF)
#define BAUD_DIV_U  0x00 //((BAUD_DIV>>8)&$FF)

void init_uart(){
    volatile unsigned char *uart_reg = (volatile unsigned char *)UART_KEYBOARD;
    
    // 1. Entra no modo DLAB para configurar Baud Rate
    *(uart_reg + LCR) = 0x83;          
    *(uart_reg + DLL) = 8;    // Divisor para 115200 com 14.7456MHz
    *(uart_reg + DLM) = 0; 
    // 2. Sai do modo DLAB e define 8N1 (MUITO IMPORTANTE: usar 0x03)
    *(uart_reg + LCR) = 0x03;          

    // 3. Configura FIFO (Habilita, limpa buffers e seta trigger de 14 bytes)
    *(uart_reg + FCR) = 0xC7;          
    
    // 4. Limpa registradores de controle
    *(uart_reg + MCR) = 0x00;          
    *(uart_reg + IER) = 0x00; // Garante que interrupções estão desligadas
}       

unsigned char read_kbd()
{
    volatile unsigned char *uart_reg = (volatile unsigned char *)UART_KEYBOARD;

    while( !(*(uart_reg + LSR) & 0x01) ); 
    return *(uart_reg + RHR); 
}
unsigned char uart_read(){
    return read_kbd();
}
void write_kbd(unsigned char data){
    volatile unsigned char *uart_reg = (volatile unsigned char *)UART_KEYBOARD;
    // Tente ler a versão do chip
    while( !(*(uart_reg + LSR) & 0x20) ){}; 
    *(uart_reg + THR) = data;
}

// Tabela simplificada de Tradução HID para ASCII
// Índice é o ScanCode, valor é o caractere
const char hid2ascii[] = {
    0, 0, 0, 0, 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', 
    '3', '4', '5', '6', '7', '8', '9', '0', 0x0D, 0x1B, 0x08, 0x09, ' '
};

void print_char(){
    unsigned char code = get_keypress();
    
    // Traduz para ASCII usando a tabela
    if (code < sizeof(hid2ascii)) {
        char c = hid2ascii[code];
        if (c != 0) {
            printf("%c", c); // Ecoa no terminal do console
        }
    }
}

unsigned char get_keypress1() {
    volatile unsigned char *uart_reg = (volatile unsigned char *)UART_KEYBOARD;
    //unsigned char header1;
    //unsigned char header2;
    unsigned char scancode;
    int i;

    while(1) {
        // 1. Procura o primeiro byte do cabeçalho (0x57)
        while(!(*(uart_reg + LSR) & 0x01)); 
        if (*(uart_reg + RHR) != 0x57) {
            while((*(uart_reg + LSR) & 0x01)){
                *(uart_reg + RHR);
            }
            continue;
        }

        // 2. Procura o segundo byte (0xAB)
        while(!(*(uart_reg + LSR) & 0x01)); 
        if (*(uart_reg + RHR) != 0xAB) {
            while((*(uart_reg + LSR) & 0x01)){
                *(uart_reg + RHR);
            }
            continue;
        }
        // 2. Procura o segundo byte (0x88)
        while(!(*(uart_reg + LSR) & 0x01)); 
        if (*(uart_reg + RHR) != 0x88){
            while((*(uart_reg + LSR) & 0x01)){
                *(uart_reg + RHR);
            }
            continue;
        }

        // 3. Se chegou aqui, o pacote é legítimo. 
        // Vamos pular os bytes: Tipo (1), Modificador (1) e Reservado (1)
        for(i = 0; i <= 3; i++) {
            while(!(*(uart_reg + LSR) & 0x01));
            *(uart_reg + RHR); // Lê e descarta
        }

        // 4. O sexto byte é o que nos interessa: ScanCode!
        while(!(*(uart_reg + LSR) & 0x01));
        scancode = *(uart_reg + RHR);

        // 5. Filtro de "Key Up": O CH9350 manda 0x00 quando soltamos a tecla.
        // Se você quiser apenas a tecla pressionada, ignore o 0x00.
        if (scancode != 0) {
            return scancode;
        }
    }
}
unsigned char get_keypress() {
    volatile unsigned char *uart_reg = (volatile unsigned char *)UART_KEYBOARD;
    unsigned char cmd, length, type;
    unsigned char key_buffer[8];
    int i;

    while(1) {
        // 1. Sincroniza no primeiro byte do cabeçalho (0x57)
        while(!(*(uart_reg + LSR) & 0x01)); 
        if (*(uart_reg + RHR) != 0x57) continue;

        // 2. Confirma o segundo byte (0xAB)
        while(!(*(uart_reg + LSR) & 0x01)); 
        if (*(uart_reg + RHR) != 0xAB) continue;

        // 3. Lê o Comando (Pelo seu dump, pode vir 0x87 ou 0x81)
        while(!(*(uart_reg + LSR) & 0x01)); 
        cmd = *(uart_reg + RHR);

        //printf("[%02x]",cmd);

        
        if (cmd == 0x82) 
            status = 0;
        //else
        //    printf("[%02x]",cmd);    
        if (cmd == 0x87) {
            // É o aviso de descritor recebido. Ele manda 1 byte de tamanho depois.
            while(!(*(uart_reg + LSR) & 0x01));
            length = *(uart_reg + RHR);
            
            // Esvazia os bytes desse aviso rapidamente
            for(i = 0; i < length; i++) {
                while(!(*(uart_reg + LSR) & 0x01));
                *(uart_reg + RHR);
            }
            continue; // Volta a procurar o próximo cabeçalho
        } 
        if (cmd == 0x88) {
            unsigned char key_buffer[8] = {0};
            //for(i = 0; i < 8; i++) {
            //    while(!(*(uart_reg + LSR) & 0x01));
            //    key_buffer[i] = *(uart_reg + RHR);
            //    printf("[%02x]",key_buffer[i]);
            //}

            // printf("[%02x]\n", cmd);          
            // No comando 0x88, os 8 bytes de dados HID vêm IMEDIATAMENTE após o comando.
            
            for(i = 0; i < 8; i++) {
                while(!(*(uart_reg + LSR) & 0x01));
                key_buffer[i] = *(uart_reg + RHR);
              //  printf("[%02x]",key_buffer[i]);
                if (key_buffer[2] != 0) {
                    printf("[%02x ",key_buffer[2]);
                    printf("%02x] ",hid2ascii[key_buffer[2]]);
                    key_buffer[2] = 0;
                }
                else
                if (key_buffer[4] != 0) {
                    printf("[%02x ",key_buffer[4]);
                    printf("%02x] ",hid2ascii[key_buffer[4]]);
                    key_buffer[4] = 0;
                }
            }
            //printf("\n");
            continue;
        }        
        status = 0;
        if (cmd == 0x81) {
            // É o pacote de dados! 
            // O próximo byte é o Tipo/Endereço (no seu dump veio 0x01)
            while(!(*(uart_reg + LSR) & 0x01));
            type = *(uart_reg + RHR);

            // O próximo byte é o Length (Tamanho do pacote que vem atrás)
            while(!(*(uart_reg + LSR) & 0x01));
            length = *(uart_reg + RHR);

            // Se o tamanho for 0x6A (106 bytes), é aquele Descriptor gigante!
            // Temos que engolir ele na velocidade da luz para a FIFO não transbordar
            if (length > 8) {
                for(i = 0; i < length; i++) {
                    while(!(*(uart_reg + LSR) & 0x01));
                    *(uart_reg + RHR); // descarta
                }
                continue; 
            }

            // SE CHEGOU AQUI: O tamanho é pequeno (provavelmente 8 bytes padrão de teclado HID)
            if (length == 8) {
                for(i = 0; i < 8; i++) {
                    while(!(*(uart_reg + LSR) & 0x01));
                    key_buffer[i] = *(uart_reg + RHR);
                    printf("[%02x ",key_buffer[i]);
                }

                // O formato padrão USB HID de 8 bytes é:
                // key_buffer[0] = Modificadores (Shift, Ctrl, Alt...)
                // key_buffer[1] = Reservado (0x00)
                // key_buffer[2] = Primeira tecla pressionada (ScanCode!)
                
                // Filtro para ignorar quando solta a tecla (tudo zero)
                if (key_buffer[2] != 0) {
                    return key_buffer[2]; // Retorna o ScanCode real!
                }
            } else {
                // Caso venha um tamanho inesperado, limpa para não desalinhar
                for(i = 0; i < length; i++) {
                    while(!(*(uart_reg + LSR) & 0x01));
                    *(uart_reg + RHR);
                }
            }
        }
    }
} 
void get_version(){
    volatile unsigned char *uart_reg = (volatile unsigned char *)UART_KEYBOARD;
    // Tente ler a versão do chip
    while( !(*(uart_reg + LSR) & 0x20) ){}; *(uart_reg + THR) = 0xAB;
    while( !(*(uart_reg + LSR) & 0x20) ){}; *(uart_reg + THR) = 0x01;
    while( !(*(uart_reg + LSR) & 0x20) ){}; *(uart_reg + THR) = 0x57;
    while( !(*(uart_reg + LSR) & 0x20) ){}; *(uart_reg + THR) = 0x03; // Checksum (57+AB+01)
}
void set_keyboard_leds(unsigned char led_status) {
    volatile unsigned char *uart_reg = (volatile unsigned char *)UART_KEYBOARD;
    
    unsigned char buf[11];
    
    buf[0] = 0x57;
    buf[1] = 0xAB;
    buf[2] = 0x12; // Comando de escrita de dados HID
    buf[3] = 0x00;
    buf[4] = 0x00;
    buf[5] = 0x00;
    buf[6] = 0x00;
    buf[7] = 0x02; // Report Type (Output)
    buf[8] = led_status; // O bitmask dos LEDs (0x01, 0x02, 0x04)
    buf[9] = 0x0F; // Constante de preenchimento (comum nesse protocolo)
    
    // Checksum: soma de buf[0] até buf[9]
    unsigned char ck = 0;
    for(int i = 2; i < 10; i++) {
        ck += buf[i];
    }
    buf[10] = ck;

    // Envio para a UART
    for(int i = 0; i < 11; i++) {
        while( !(*(uart_reg + LSR) & 0x20) ); 
        *(uart_reg + THR) = buf[i];
    }
}
void clear_buffer(){
    // Estrutura conceitual para o seu loop no tcpbox68k
    while(1) {
        // 1. Aguarda cabeçalho 0x57 0xAB
        if (uart_read() == 0x57 && uart_read() == 0xAB) {
            unsigned char cmd = uart_read();
            
            if (cmd == 0x81) { // Pacote de dados
                unsigned char addr = uart_read(); // lê endereço/tipo
                unsigned char len = uart_read();  // lê o tamanho real (se for 0x6A é o descritor, se for 0x08 é tecla!)
                
                if (len == 0x08) {
                    // SUCESSO! Isto aqui é um pacote de tecla pressionada!
                    unsigned char key_buffer[8];
                    for(int i=0; i<8; i++) {
                        key_buffer[i] = uart_read(); // Lê os 8 bytes de scan codes rapidamente
                    }
                    // Agora sim, imprima com segurança fora do gárgulo de tempo:
                    printf("Tecla detectada! Mod: %02X, Scan: %02X\n", key_buffer[0], key_buffer[2]);
                } else {
                    // É o descritor longo de 106 bytes (0x6A) ou outro tamanho.
                    // Esvazie a UART rapidamente para não estourar a FIFO
                    for(int i=0; i<len; i++) {
                        uart_read(); 
                    }
                }
            }
            else if (cmd == 0x87) {
                // Se receber o aviso de descriptor 0x87, limpe os bytes seguintes
                // para manter a UART alinhada
                unsigned char len = uart_read();
                for(int i=0; i<len; i++) {
                    uart_read();
                }
            }
        }    
    }
}
unsigned char keyboard_led_state=0;
void toggle_caps_lock() {
    // Inverte apenas o bit 1 (Caps Lock)
    keyboard_led_state ^= 0x02; 
    set_keyboard_leds(keyboard_led_state);
}
/*
void set_transparent_mode() {
    volatile unsigned char *uart_reg = (volatile unsigned char *)UART_KEYBOARD;

    // Array com o comando completo: Header(57 AB), Cmd(01), Param(00), Checksum(01)
    unsigned char cmd[] = {0x57, 0xAB, 0x01, 0x00, 0x01};

    for(int i = 0; i < 5; i++) {
        // Aguarda o Line Status Register (LSR) indicar que o 
        // Transmitter Holding Register (THR) está vazio (bit 5 - 0x20)
        while (!(uart_reg[LSR] & 0x20)); 
        
        // Escreve o byte no Transmit Holding Register
        uart_reg[THR] = cmd[i];
    }
}*/
void main() {
    init_uart();
    //set_transparent_mode();
    printf("Desligando led...");
    delay(0x8FF);
    printf("\nOrion68K Online. Digite algo:\n");
    set_keyboard_leds(0x02);

    get_keypress();

    while(1) {
        toggle_caps_lock();
        delay(0x8FF);
        //printf("key [%02X] ",read_kbd());
    }
}
