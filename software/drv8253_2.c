#include "drv8253.h"

void timer_init_channel0(uint16_t count_value, uint8_t mode) {
    uint8_t control_word = TIMER_SEL0 | mode;
    TIMER_CTRL = control_word;
    TIMER0_COUNT = count_value & 0xFF;        // LSB
    TIMER0_COUNT = (count_value >> 8) & 0xFF; // MSB
}

void timer_init_channel1(uint16_t count_value, uint8_t mode) {
    uint8_t control_word = TIMER_SEL1 | mode;
    TIMER_CTRL = control_word;
    TIMER1_COUNT = count_value & 0xFF;        // LSB
    TIMER1_COUNT = (count_value >> 8) & 0xFF; // MSB
}

void timer_init_channel2(uint16_t count_value, uint8_t mode) {
    uint8_t control_word = TIMER_SEL2 | mode;
    TIMER_CTRL = control_word;
    TIMER2_COUNT = count_value & 0xFF;        // LSB
    TIMER2_COUNT = (count_value >> 8) & 0xFF; // MSB
}

uint16_t timer_read_channel0(void) {
    // Latch and read counter value
    TIMER_CTRL = TIMER_SEL0 | TIMER_RW_LATCH;
    uint8_t lsb = TIMER0_COUNT;
    uint8_t msb = TIMER0_COUNT;
    return (msb << 8) | lsb;
}

uint16_t timer_read_channel1(void) {
    TIMER_CTRL = TIMER_SEL1 | TIMER_RW_LATCH;
    uint8_t lsb = TIMER1_COUNT;
    uint8_t msb = TIMER1_COUNT;
    return (msb << 8) | lsb;
}

uint16_t timer_read_channel2(void) {
    TIMER_CTRL = TIMER_SEL2 | TIMER_RW_LATCH;
    uint8_t lsb = TIMER2_COUNT;
    uint8_t msb = TIMER2_COUNT;
    return (msb << 8) | lsb;
}

// Função de delay baseada no timer (busy wait)
void timer_wait_ms(uint32_t milliseconds) {
    // Configura canal 2 para modo 2 (rate generator) para delay
    uint16_t count_value = TIMER_1MS_COUNT;
    timer_init_channel2(count_value, TIMER_MODE2 | TIMER_RW_BOTH | TIMER_BINARY);

    for (uint32_t i = 0; i < milliseconds; i++) {
        // Espera até o contador terminar
        while (timer_read_channel2() > 0) {
            // Busy wait
        }
    }
}
