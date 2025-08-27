#include <stdio.h>
#include <stdlib.h>

#include <mc68000.h>

#define LEDS_ADDRESS 0x4400
#define LEDS (*(volatile unsigned char *)LEDS_ADDRESS)

void delay(unsigned int time) {
    for (volatile unsigned int i = 0; i < time; i++);
}

// Função para verificar stack
void check_stack(void) {
    unsigned long stack_val;
    asm volatile (
        "move.l %%sp, %0\n\t"
        : "=r" (stack_val)
    );
    printf("Stack pointer: 0x%08X\n", stack_val);
}

void led_effects() {
    // Efeito de "carrinho"
    unsigned char patterns[] = {
        0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80,
        0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01
    };

    for (int i = 0; i < 15; i++) {
        LEDS = patterns[i];
        delay(30000);
    }

    // Efeito de intensidade crescente
    for (int i = 0; i < 8; i++) {
        LEDS |= (1 << i);
        delay(20000);
    }

    for (int i = 0; i < 8; i++) {
        LEDS &= ~(1 << i);
        delay(20000);
    }
}

int main() {
    char str[10]={0};
    int c;
    check_stack();  // ✅ Verificar stack no início

    LEDS = 0x01;

    printf("Hello MC68000!\n");
    LEDS = 0x02;
    printf("Digite 10 chars ");
    LEDS = 0x03;
    gets_s(str,10);
    //gets_s(str,10);

    printf("\nDigitado %s\n",str);
    led_effects();

        LEDS = 0xFF;    // Todos acesos
        delay(50000);
        LEDS = 0x00;    // Todos apagados
        delay(50000);

    return 0;
}


