#include "hardware/pio.h"
#include "vga_bus_read.pio.h"
/*
bit 0–7   → D0–D7   (data)
bit 8–12  → A1–A5   (addr = 5 bits)
bit 13    → CS

*/

//Registers
#define WRITE_SCREEN    0x00
#define CHANGE_BUFFER   0x30
#define SELECT_SCREEN   0x29
#define SET_HORIZONTAL  0x28
#define SET_VERTICAL    0x27
#define RUN_CMD         0x26


static uint8_t bus_decode(uint32_t v)
{
    uint8_t data =  v & 0xFF;          // D0–D7
    uint8_t addr = (v >> 8) & 0x1F;    // A1–A5 (5 bits)

    return data;
}

uint8_t bus_wait_event(PIO pio, uint sm)
{
    return bus_decode( pio_sm_get_blocking(pio, sm) );
}

bool bus_try_get_event(uint8_t *value,PIO pio, uint sm)
{
    uint8_t res;
    if (!pio_sm_is_rx_fifo_empty(pio, sm)) {
        res = bus_decode( pio_sm_get(pio, sm) );
        *value = res;
        return true;
    }
    return false;
}

bool bus_try_get_event32(uint32_t *value,PIO pio, uint sm)
{
    uint32_t valor;
    if (!pio_sm_is_rx_fifo_empty(pio, sm)) {
        valor = pio_sm_get(pio, sm) ;
        *value = valor;
        return true;
    }
    return false;
}