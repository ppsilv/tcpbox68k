
#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "string.h"
#include "vga16_drv.h"
#include "vga16_primitives.h"
#include "pt_cornell_v1_4.h"    // protothreads header
#include "colors.h"


vga16_text_t *vga = NULL ;

static repeating_timer_t timer;
static int last_toggle_time = 1;

static bool timer_callback(repeating_timer_t *rt)
{
    if(last_toggle_time == 1){
        put_cursor(1);
        last_toggle_time = 0;
    }
    else{
        put_cursor(0);
        last_toggle_time = 1;
    }
  return true;
}
static void create_timer(bool btimer)
{
    if(btimer){
        cancel_repeating_timer(&timer);
        int16_t tempo = vga->get_blink_interval();
        add_repeating_timer_ms(tempo, timer_callback, NULL, &timer);
    }else{
        cancel_repeating_timer(&timer);
    }
}

 volatile   int cursorx=0;
 volatile   int cursory=0;

// ========================================
// === core 0 main
// ========================================
void swap_buffers(char **active_buffer_ptr, unsigned char *new_buffer) {
    *active_buffer_ptr = (char *)new_buffer;
    // Opcional: esperar a DMA terminar antes de trocar
    // dma_channel_wait_for_finish_blocking(rgb_chan_0);
}
#define TXCOUNT 153600 // Total pixels/2 (since we have 2 pixels per byte)
char vga_video_data_array0[TXCOUNT];
char vga_video_data_array1[TXCOUNT];
char *active_buffer = (char *)&vga_video_data_array0[0];
char buffer=0;
static PT_THREAD (protothread_trocatela(struct pt *pt))
{
    PT_BEGIN(pt);
    static bool LED_state = false ;
    //Init something here
    PT_INTERVAL_INIT() ;

    while(1) {
        PT_YIELD_INTERVAL(5000000) ;
        swap_buffers(&active_buffer, vga_video_data_array0);
        vga->set_vga_data_array(vga_video_data_array0);
        buffer=0;
        PT_YIELD_INTERVAL(5000000) ;
        swap_buffers(&active_buffer, vga_video_data_array1);
        vga->set_vga_data_array(vga_video_data_array1);
        buffer=1;
    }
  PT_END(pt);
} 


#include "hardware/pio.h"
extern PIO bus_pio1;
extern uint bus_sm;
//extern uint8_t bus_wait_event(PIO pio, uint sm);
extern bool bus_try_get_event(uint8_t *value,PIO pio, uint sm);
bool bus_try_get_event32(uint32_t *value,PIO pio, uint sm);
static PT_THREAD (protothread_print_bus_read(struct pt *pt))
{
    char buf[256]={0};
    uint8_t value;
    uint32_t valor=0;
    PT_BEGIN(pt);
    PT_INTERVAL_INIT() ;
    uint8_t icor=0;
    while(1) {
        PT_YIELD_INTERVAL(1000000) ;
//        if( bus_try_get_event(&value,bus_pio1, bus_sm) == true ){    
//            sprintf(buf,"%02X",value);
//            vga->printString(buf);        
//        }

        if( bus_try_get_event32(&valor,bus_pio1, bus_sm) == true ){    
            sprintf(buf,"[%08X]",valor);
            vga->printString(buf);        
        }

    } // END WHILE(1)
    PT_END(pt);
}

void drawPixel(short x, short y, color_t color) ;
void drawHLine(int x, int y, int w, color_t color) ;
void fillRect(short x, short y, short w, short h, color_t color);

int main(){

    // set the clock
    set_sys_clock_khz(150000, true);

    // start the serial i/o
    stdio_init_all() ;
    initReadBus_Pio();

    // Initialize the VGA screen
    initVGA(  &active_buffer, TXCOUNT ) ;

    vga = create_screen( MODE_640x480, active_buffer, TXCOUNT );
    vga->set_vga_data_array(vga_video_data_array0);
    vga->setTextColor(CYAN, BLACK);
    vga->setTextSize(1);
    vga->set_blink_interval(125);
    vga->setTextCursorVisible(CURSOR_ON);

    drawHLine(0,0,640,YELLOW);
    drawHLine(0,1,640,YELLOW);
    drawHLine(0,2,640,YELLOW);
    drawHLine(0,3,640,YELLOW);

    //fillRect(0,2,400,640,RED);

    vga->setTextCursor(0,1);
    vga->printString("         0         1         2         3         4         5         6         7");      
    vga->printString("12345678901234567890123456789012345678901234567890123456789012345678901234567890");
    vga->printString("         0         1         2         3         4         5         6         7");      
    vga->printString("12345678901234567890123456789012345678901234567890123456789012345678901234567890");
    
    vga->setTextCursor(0,6);
    vga->printString("Tela numero 1 cor: ");

    char buf[12];
    for( int i=0;i<8;i++){
        if(i==0){
            vga->setTextColor(i, WHITE);
        }else
            vga->setTextColor(i, BLACK);
        sprintf(buf,"[%d - %d",i,vga->getTextColor());
        vga->printString(buf);
        vga->printString("]");
    }
    vga->setTextCursor(0,7);
    sprintf(buf,"blink interval: %d", vga->get_blink_interval());
    vga->printString(buf);

    //for(int i=0;i<640;i++)
    //    for( int j=100;j<110;j++)
    //        drawPixel( i,  j, GREEN ) ;
//
    vga->setTextColor(GREEN, BLACK);
    //vga->clrscr();
    /*
        swap_buffers existe porque a idéia de duplo buffer é justamente
        essa, enquanto o sistema está mostrando uma tela podemos atualizar
        a outra sem interferir com a tela sendo mostrada.
        Temos 2 situações aqui
        1 - Estamos mostrando na tela o buffer1 vga_video_data_array1
            usamos: vga->set_vga_data_array(vga_video_data_array0);
            para escrever no buffer0 quando termina de atualizar o buffer0
            fazemos swap.
        2 - Estamos mostrando na tela o buffer0 vga_video_data_array0
            usamos: vga->set_vga_data_array(vga_video_data_array1); para fazer
            scroll vertical, após fazer o scroll fazemos o swap e mostramos o
            buffer1.
                        
    */
    swap_buffers(&active_buffer, vga_video_data_array1);
    vga->set_vga_data_array(vga_video_data_array1);
    vga->setTextCursor(0,4);
    vga->printString("Paulo da silva (c) 2025-2026 marco-16 compilation 101...\n");
    vga->setTextCursor(0,5);
    vga->printString("Paulo da silva (c) 2025-2026 marco-17 compilation 101...\n");
    vga->setTextCursor(0,6);
    vga->printString("Paulo da silva (c) 2025-2026 marco-19 compilation 101...\n");
    vga->setTextCursor(0,7);
    vga->printString("Paulo da silva (c) 2025-2026 marco-20 compilation 101...\n");



  // === config threads ========================
  // for core 0
  create_timer(CURSOR_BLINK_ON); //Com o timer para o cursor ele não engasga como quando controlado pela protothread
  pt_add_thread(protothread_trocatela);
  pt_add_thread(protothread_print_bus_read);


  // === initalize the scheduler ===============
  pt_schedule_start ;
  // NEVER exits
  // ===========================================
} // end main
