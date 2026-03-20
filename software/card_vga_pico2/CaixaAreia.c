    vga->init = 
    vga->clrscr = 
    vga->pchar = 
    vga->draw_pixel = 
    vga->draw_hline = 
    vga->fill_rect = 
    vga->draw_char_interna = 
    vga->draw_char = 
    vga->print_string = 
    vga->set_text_cursor = 
    vga->set_text_color = 
    vga->set_text_color2 = 
    vga->set_text_wrap = 
    vga->tft_write = 
    vga->set_text_color_big = 
    vga->write_string_bold = 
    vga->read_pixel = 
 vga16_text_init(vga16_text_t* vga, uint8_t mode) ;
 vga16_text_clrscr(vga16_text_t* vga) ;
 vga16_text_pchar(vga16_text_t* vga, uint8_t c) ;
 vga16_text_draw_pixel(vga16_text_t* vga, int16_t x, int16_t y, color_t color) ;
 vga16_text_draw_hline(vga16_text_t* vga, int16_t x, int16_t y, int16_t w, color_t color) ;
 vga16_text_fill_rect(vga16_text_t* vga, int16_t x, int16_t y, int16_t w, int16_t h, color_t color) ;
 vga16_text_draw_char_interna(vga16_text_t* vga, int16_t x, int16_t y, uint8_t c,
 vga16_text_draw_char(vga16_text_t* vga, uint8_t c, color_t color, color_t bg, uint8_t size) ;
 vga16_text_set_text_cursor(vga16_text_t* vga, int16_t x, int16_t y) ;
 vga16_text_set_text_color(vga16_text_t* vga, color_t c) ;
 vga16_text_set_text_color2(vga16_text_t* vga, color_t c, color_t b) ;
 vga16_text_set_text_wrap(vga16_text_t* vga, bool w) ;
 vga16_text_tft_write(vga16_text_t* vga, uint8_t c) ;
 vga16_text_print_string(vga16_text_t* vga, int8_t* str) ;
 vga16_text_set_text_color_big(vga16_text_t* vga, color_t color, color_t background) ;
 vga16_text_write_string_bold(vga16_text_t* vga, int8_t* str) ;
 vga16_text_read_pixel(const vga16_text_t* vga, int16_t x, int16_t y) ;
 
    // Getters
    vga->get_cursor_x = vga16_text_get_cursor_x;
    vga->get_cursor_y = vga16_text_get_cursor_y;
    vga->get_width = vga16_text_get_width;
    vga->get_height = vga16_text_get_height;
    vga->get_textsize = vga16_text_get_text_size;

    // Setters
    vga->set_cursor_x = vga16_text_set_cursor_x;
    vga->set_cursor_y = vga16_text_set_cursor_y;
    vga->set_width = vga16_text_set_width;
    vga->set_height = vga16_text_set_height;
    vga->set_textsize = vga16_text_set_textsize;


 (const vga16_text_t* vga) ;
 (const vga16_text_t* vga) ;
    
