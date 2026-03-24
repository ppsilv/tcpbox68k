#ifndef __VGA16_DRV_H__
#define __VGA16_DRV_H__

/**
 * Hunter Adams (vha3@cornell.edu)
 * modifed for 16 colors by BRL4
 * 
 *
 * HARDWARE CONNECTIONS
 *  - GPIO 16 ---> VGA Hsync
 *  - GPIO 17 ---> VGA Vsync
 *  - GPIO 18 ---> 470 ohm resistor ---> VGA Green 
 *  - GPIO 19 ---> 330 ohm resistor ---> VGA Green
 *  - GPIO 20 ---> 330 ohm resistor ---> VGA Blue
 *  - GPIO 21 ---> 330 ohm resistor ---> VGA Red
 *  - RP2040 GND ---> VGA GND
 *
 * RESOURCES USED
 *  - PIO state machines 0, 1, and 2 on PIO instance 0
 *  - PIO state machine  0 on PIO instance 1
 *  - DMA channels 0, 1, 2, and 3
 *  - 153.6 kBytes of RAM (for pixel color data)
 *
 * NOTE
 *  - This is a translation of the display primitives
 *    for the PIC32 written by Bruce Land and students
 *
 */

#define SCREEN_0                0       //40 col 24 linhas
#define SCREEN_1                1       //80 col 30 linhas
#define SCREEN_2                2       //320x240 gráfico com 256 cores.
#define SCREEN_3                3       //640x480 gráfico com 8 cores.
#define BUFFER_1                1
#define BUFFER_2                2
#define CURSOR_ON               1
#define CURSOR_OFF              0
#define CURSOR_BLINK_ON         1
#define CURSOR_BLINK_OFF        0

//screens


// VGA primitives - usable in main
void initVGA(  char **active_buffer_ptr,unsigned int totalBytes) ;
void initReadBus_Pio();
char* get_vga_buffer_pointer(void);



#endif