#include <mc68000.h>

int putchar(int c) {
    while (!(UART->status & 0x02)); // Wait for TX ready
    UART->data = c;
    return c;
}

int getchar(void) {
    while (!(UART->status & 0x01)); // Wait for RX ready
    return UART->data;
}
