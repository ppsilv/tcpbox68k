#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/dma.h"
#include "vga_hsync.pio.h"
#include "vga_vsync.pio.h"
#include "vga_rgb.pio.h"
#include "vga_bus_read.pio.h"
#include "vga_drv.h"

// Give the I/O pins that we're using some names that make sense - usable in main()
//enum vga_pins {BUS=0,HSYNC=19, VSYNC=20, RED_PIN=21, LO_GRN=22, BLUE_PIN=26} ;
enum vga_pins {BUS=0,HSYNC=16, VSYNC=17, RED_PIN=20, LO_GRN=19, BLUE_PIN=18} ;

// VGA timing constants
#define H_ACTIVE   655    // (active + frontporch - 1) - one cycle delay for mov
#define V_ACTIVE   479    // (active - 1)
#define RGB_ACTIVE 319    // (horizontal active)/2 - 1
//#define RGB_ACTIVE 639 // change to this if 1 pixel/byte

PIO bus_pio0;
PIO bus_pio1;
uint bus_sm;
// Manually select a few state machines from pio instance pio0.
uint hsync_sm = 0;
uint vsync_sm = 1;
uint rgb_sm = 2;

static void initDMA(char **active_buffer_ptr,unsigned int totalBytes,PIO pio);
static void initPio0(void);

void initReadBus_Pio()
{
    PIO pio = pio1;
    bus_pio1 = pio;

    uint bus_read_offset = pio_add_program(pio, &bus_read_program);

    uint bus_read_sm = 0;
    bus_sm = bus_read_sm;

    pio_sm_claim (pio, bus_read_sm);

    bus_read_program_init(pio, bus_read_sm, bus_read_offset, BUS);

}

void initVGA(  char **active_buffer_ptr,unsigned int totalBytes) {

    initPio0();
    initDMA(active_buffer_ptr,totalBytes,bus_pio0);

}

static void initPio0(void)
{
        // Choose which PIO instance to use (there are two instances, each with 4 state machines)
    PIO pio = pio0;
    bus_pio0 = pio;
    // The program name comes from the .program part of the pio file
    // and is of the form <program name_program>
    uint hsync_offset = pio_add_program(pio, &hsync_program);
    uint vsync_offset = pio_add_program(pio, &vsync_program);
    uint rgb_offset = pio_add_program(pio, &rgb_program);
/*
    // Manually select a few state machines from pio instance pio0.
    uint hsync_sm = 0;
    uint vsync_sm = 1;
    uint rgb_sm = 2;
*/
    pio_sm_claim (pio, hsync_sm);
    pio_sm_claim (pio, vsync_sm);
    pio_sm_claim (pio, rgb_sm);

    // Call the initialization functions that are defined within each PIO file.
    // Why not create these programs here? By putting the initialization function in
    // the pio file, then all information about how to use/setup that state machine
    // is consolidated in one place. Here in the C, we then just import and use it.
    hsync_program_init(pio, hsync_sm, hsync_offset, HSYNC);
    vsync_program_init(pio, vsync_sm, vsync_offset, VSYNC);
    rgb_program_init(pio, rgb_sm, rgb_offset, BLUE_PIN);

    /////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////

    // Initialize PIO state machine counters. This passes the information to the state machines
    // that they retrieve in the first 'pull' instructions, before the .wrap_target directive
    // in the assembly. Each uses these values to initialize some counting registers.
    pio_sm_put_blocking(pio, hsync_sm, H_ACTIVE);
    pio_sm_put_blocking(pio, vsync_sm, V_ACTIVE);
    pio_sm_put_blocking(pio, rgb_sm, RGB_ACTIVE);
   

    // Start the two pio machine IN SYNC
    // Note that the RGB state machine is running at full speed,
    // so synchronization doesn't matter for that one. But, we'll
    // start them all simultaneously anyway.
    pio_enable_sm_mask_in_sync(pio, ((1u << hsync_sm) | (1u << vsync_sm) | (1u << rgb_sm)));

}

static void initDMA(char **active_buffer_ptr,unsigned int totalBytes,PIO pio){

    /////////////////////////////////////////////////////////////////////////////////////////////////////
    // ============================== PIO DMA Channels =================================================
    /////////////////////////////////////////////////////////////////////////////////////////////////////

    // DMA channels - 0 sends color data, 1 reconfigures and restarts 0
    int rgb_chan_0 = dma_claim_unused_channel(true);
    int rgb_chan_1 = dma_claim_unused_channel(true);

    // change this to true of other DMA channels interfer with video
    #define rgb_high_priority false

    // Channel Zero (sends color data to PIO VGA machine)
    dma_channel_config c0 = dma_channel_get_default_config(rgb_chan_0);  // default configs
    channel_config_set_transfer_data_size(&c0, DMA_SIZE_8);              // 8-bit txfers
    channel_config_set_read_increment(&c0, true);                        // yes read incrementing
    channel_config_set_write_increment(&c0, false);                      // no write incrementing
    channel_config_set_dreq(&c0, DREQ_PIO0_TX2) ;                        // DREQ_PIO0_TX2 pacing (FIFO)
    channel_config_set_chain_to(&c0, rgb_chan_1);                        // chain to other channel
    channel_config_set_high_priority (&c0, rgb_high_priority) ;

    dma_channel_configure(
        rgb_chan_0,                 // Channel to be configured
        &c0,                        // The configuration we just created
        &pio->txf[rgb_sm],          // write address (RGB PIO TX FIFO)
        *active_buffer_ptr,             // The initial read address (pixel color array)
        totalBytes,                 // Number of transfers; in this case each is 1 byte.
        false                       // Don't start immediately.
    );

    // Channel One (reconfigures the first channel)
    dma_channel_config c1 = dma_channel_get_default_config(rgb_chan_1);   // default configs
    channel_config_set_transfer_data_size(&c1, DMA_SIZE_32);              // 32-bit txfers
    channel_config_set_read_increment(&c1, false);                        // no read incrementing
    channel_config_set_write_increment(&c1, false);                       // no write incrementing
    channel_config_set_chain_to(&c1, rgb_chan_0);                         // chain to other channel

    dma_channel_configure(
        rgb_chan_1,                         // Channel to be configured
        &c1,                                // The configuration we just created
        &dma_hw->ch[rgb_chan_0].read_addr,  // Write address (channel 0 read address)
        active_buffer_ptr,                    // Read address (POINTER TO AN ADDRESS)
        1,                                  // Number of transfers, in this case each is 4 byte
        false                               // Don't start immediately.
    );

    // Start DMA channel 0. Once started, the contents of the pixel color array
    // will be continously DMA's to the PIO machines that are driving the screen.
    // To change the contents of the screen, we need only change the contents
    // of that array.
    dma_start_channel_mask((1u << rgb_chan_0)) ;
}    
