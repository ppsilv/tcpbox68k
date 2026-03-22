#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/dma.h"

#include "vga16_primitives.h"
#include "font_5x7.h"
#include "font_8x16.h"

// 5x7 font
void writeStringBold(char* str);

struct font{
    uint8_t *name;
    uint8_t width ;
    uint8_t height ;
    uint8_t size;
    const uint8_t *data ;
};
typedef struct font font_t ;
/*
struct cursor{
    uint16_t x;
    uint16_t y;
    bool visible;
    bool blink;
    uint16_t blink_interval;
    cursorShape_t shape ;// 0 - block, 1 - underline, 2 - line
};
typedef struct cursor cursor_t;
*/
typedef struct  {
    uint16_t width;  //320, 640
    uint16_t height; //240, 480
    cursor_t *cursor ;
    screenMode_t mode ;
    font_t font ;
    color_t textcolor ;
    color_t textbgcolor ;

    uint32_t txcount;
    uint16_t topmask;
    uint16_t bottommask;
    uint8_t tabspace;    
    uint8_t* vga_data_array;    
}vga16_text_private_t;



static vga16_text_t * vga = NULL ;


static void set_vga_data_array(unsigned char video_data_array[])
{
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  priv->vga_data_array = &video_data_array[0];  
} 

void clrscr(){
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;

  memset(&priv->vga_data_array[0], 0, priv->txcount) ;
  // reset cursor position
  priv->cursor->x = 0 ;
  priv->cursor->y = 0 ;
}

/*
static void pchar(char c){
    tft_write(c);
}*/


void drawPixel(short x, short y, color_t color) {
    vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
    if((x > (priv->width-1)) | (x < 0) | (y > (priv->height-1)) | (y < 0) ) return;

    int pixel = ((priv->width * y) + x) ;
    if (pixel & 1) {
        priv->vga_data_array[pixel>>1] = (priv->vga_data_array[pixel>>1] & priv->topmask) | (color << 4) ;
    }
    else {
        priv->vga_data_array[pixel>>1] = (priv->vga_data_array[pixel>>1] & priv->bottommask) | (color) ;
    }
}

void drawHLine(int x, int y, int w, color_t color) {
    vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  // range checks
  if((x >= priv->width) || (y >= priv->height)) return;
  if((x + w - 1) >= priv->width)  w = priv->width  - x - 1;
  //
  //short xx = x;
  short both_color = color | (color<<4) ;
  // loner pixel at x -- align left with next byte boundary
  if((x & 1)) {
    drawPixel(x,y,color);
    x++ ;
    w-- ;
  }
  // draw loner pixel at end and adjust width
  if((w & 1)){
    drawPixel(x+w-1, y, color);
    w-- ;
  }
  // draw rest of line
  int len = (w>>1)  ;
  if (len>0 && y<480 ) memset(&priv->vga_data_array[320*y+(x>>1)], both_color, len) ;
 }

void fillRect(short x, short y, short w, short h, color_t color) {
   vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
   if((y + h - 1) >= priv->height) h = priv->height - y - 1;

  for(int i=x; i <= w;i++)
      for( int j=y;j <= h;j++)
          drawPixel( i,  j, color ) ;

//  for(int j=y; j<(y+h); j++) {
//    drawHLine(x, j, w, color) ;
//  }
}

static void drawChar_interna(short x, short y, unsigned char c, color_t color, color_t bg, unsigned char size) {
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  char i, j;
  if((x >= priv->width)            || // Clip right
     (y >= priv->height)           || // Clip bottom
     ((x + 6 * size - 1) < 0) || // Clip left
     ((y + 8 * size - 1) < 0))   // Clip top
    return;

    // Calcula a área do caractere
    short charWidth = 8 * size;
    short charHeight = 8 * size;    
    // PRIMEIRO: Limpa a área completa do caractere
    fillRect(x, y, charWidth, charHeight, BLACK);

  uint8_t lastColumn = 5 ;
  uint8_t altura = 8 ;
  uint8_t largura = 6 ;
  for (i=0; i<largura; i++ ) {
    unsigned char line;
    if (i == lastColumn)
      line = 0x0;
    else
      line = pgm_read_byte(font_5x7+(c*lastColumn)+i);
    for ( j = 0; j < altura; j++) {
      if (line & 0x1) {
        if (size == 1) // default size
          drawPixel(x+i, y+j, color);
        else {  // big size
          fillRect(x+(i*size), y+(j*size), size, size, color);
        }
      } else if (bg != color) {
        if (size == 1) // default size
          drawPixel(x+i, y+j, bg);
        else {  // big size
          fillRect(x+i*size, y+j*size, size, size, bg);
        }
      }
      line >>= 1;
    }
  }
}

void drawChar2( int start_x, int start_y, uint8_t char_code, int color,  int bgcolor, unsigned char size) {
    vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;

    // Calcula a área do caractere
    size=1;
    short charWidth = 8 * size;
    short charHeight = 16 * size;    
    // PRIMEIRO: Limpa a área completa do caractere
    fillRect(start_x, start_y, charWidth, charHeight, bgcolor);

    const uint8_t *char_start = font_8x16 + (char_code * priv->font.height);
    // Percorrer todas as linhas (bytes) do caractere
    for (int row = 0; row < priv->font.height; row++) {
        uint8_t current_byte = char_start[row];

        // Percorrer todos os bits do byte (da esquerda para a direita)
        for (int bit = 7; bit >= 0; bit--) {
            // Calcular coordenadas do pixel
            int pixel_x = start_x + (7 - bit);  // 7-bit para ir da esquerda para direita
            int pixel_y = start_y + row;
            // Verificar se o bit está setado (1)
            if ((current_byte >> bit) & 1) {
                // Desenhar o pixel
                if( size == 1  )
                  drawPixel(pixel_x, pixel_y, color);
                else  
                  fillRect(pixel_x+(row*size), pixel_y+(bit*size), size, size, bgcolor);
            }else{
                // Desenhar o pixel
                if( size == 1  )
                  drawPixel(pixel_x, pixel_y, bgcolor);
                else  
                  fillRect(pixel_x+row*size, pixel_y+bit*size, size, size, bgcolor);
            }
        }
    }
}


void drawChar(unsigned char c, color_t color, color_t bg, unsigned char size) {
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;

  if(size == 2)
    drawChar_interna( priv->cursor->x, priv->cursor->y, c, color, bg, size);
  else  
    drawChar2( priv->cursor->x, priv->cursor->y, c, color, bg, size);
}

void tft_write(unsigned char c){
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;

  if (c == '\n') {
//    priv->cursor->y += priv->font.size*8;
    priv->cursor->y += priv->font.height;
    priv->cursor->x  = 0;
  } else if (c == '\r') {
    // skip em
  } else if (c == '\t'){
      int new_x = priv->cursor->x + priv->tabspace;
      if (new_x < priv->width){
          priv->cursor->x = new_x;
      }
  } else {
  
    drawChar( c, priv->textcolor, priv->textbgcolor, priv->font.size);
    priv->cursor->x += priv->font.size*priv->font.width;

    if ((priv->cursor->x > (priv->width - priv->font.size*6))) {
      priv->cursor->y += priv->font.height;
      priv->cursor->x = 0;
    }
 
  }
}

void put_cursor(unsigned char c){
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;

  uint16_t cursorx=priv->cursor->x;
  uint16_t cursory=priv->cursor->y;

  cursorx += priv->font.size*priv->font.width;
  if ((cursorx > (priv->width - priv->font.size*6))) {
    cursory += priv->font.height;
    cursorx = 0;
  }
  if( priv->cursor->visible == true ){
    if( priv->cursor->blink == true ){
      if( c )
        drawChar( priv->cursor->shape, priv->textcolor, priv->textbgcolor, 1);
      else  
        drawChar( ' ', priv->textcolor, priv->textbgcolor, 1);
    }else{
        drawChar( priv->cursor->shape, priv->textcolor, priv->textbgcolor, 1);
    }
  }else{
        drawChar( ' ', priv->textcolor, priv->textbgcolor, 1);
  }
}


static void setTextCursor(short x, short y) {
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  if((x >= priv->width) || (y >= priv->height)) 
    return;
  if(x*priv->font.width >= priv->width) {
    x = x*priv->font.width / priv->font.width;
    if( y < priv->height )
      y = y *priv->font.height;
    else
      y = 0 ;
  }else{
    x = x*priv->font.width;
    if( y < priv->height )
      y = y *priv->font.height;
    else
      y = 0 ;
  }

  priv->cursor->x = x;
  priv->cursor->y = y;
}

static void setTextSize(unsigned char s) {
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  if(s >0 ){
    priv->font.size = s;
  }else{
    priv->font.size = 1;
  }
}
static unsigned char getTextSize(void) {
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  
  return priv->font.size;
}
void set_blink_interval(uint16_t interval)
{
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  priv->cursor->blink_interval = interval;
}
static uint16_t get_blink_interval(void){
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  return priv->cursor->blink_interval;
}
static void setTextCursorVisible(bool v) {
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  priv->cursor->visible = v;
}
static void setTextCursorBlink(bool b) {
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  priv->cursor->blink = b;
}
//static void setTextColor(char c) {
//  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
//  priv->textcolor = priv->textbgcolor = c;
//}

static void setTextColor(char c, char b) {
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  priv->textcolor = c;
  priv->textbgcolor = b;
}

static char getTextColor(void) {
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  return priv->textcolor;
}


static void printString(char* str){
    while (*str){
        tft_write(*str++);
    }
}

static void setTextColorBig(color_t color, char background) {
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  priv->textcolor = color;
  priv->textbgcolor = background;
}
/* 
static void writeStringBold(char* str){
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;

    char temp_bg ;
    temp_bg = priv->textbgcolor;
    while (*str){
        char c = *str++;
        drawChar_interna(priv->cursor->x, priv->cursor->y, c, priv->textcolor, priv->textbgcolor, priv->font.size);
        drawChar_interna(priv->cursor->x+1, priv->cursor->y, c, priv->textcolor, priv->textcolor, priv->font.size);
        priv->cursor->x += 7 * priv->font.size ;
    }
    priv->textbgcolor = temp_bg ;
}
*/
short readPixel(short x, short y) {
  vga16_text_private_t* priv = (vga16_text_private_t*)vga->_private;
  int pixel = ((640 * y) + x) ;
  short color ;
  if (pixel & 1) {
      color = priv->vga_data_array[pixel>>1] >> 4 ;
  }
  else {
      color = priv->vga_data_array[pixel>>1] & 0xf  ;
  }
  return color ;
}


vga16_text_t* create_screen(screenMode_t mode,unsigned char vga_data_array[],unsigned int txcount){
  vga = (vga16_text_t*)malloc(sizeof(vga16_text_t));
  vga16_text_private_t* priv = (vga16_text_private_t*)malloc(sizeof(vga16_text_private_t));
  
  if (!vga || !priv) {
      free(vga);
      free(priv);
      return NULL;
  }
  
  vga->_private = priv;
  priv->cursor = create_default_cursor() ;
  priv->textcolor = WHITE ;
  priv->textbgcolor = BLACK ;
  priv->font.name = font_name;
  priv->font.width = font_width ;
  priv->font.height= font_height ;
  priv->font.size = font_size ;   //textsize
  priv->font.data = font_8x16 ;
  priv->tabspace = 4;
  priv->txcount = txcount ;
  priv->topmask = 0b00001111 ;
  priv->bottommask = 0b11110000 ;
  priv->vga_data_array = vga_data_array ;

  if( mode == MODE_320x240 ){    
    priv->width = 320;
    priv->height= 240;
  }
  else if( mode == MODE_640x480 ){    
    priv->width = 640;
    priv->height= 480;
  }else{ //default
    priv->width = 640;
    priv->height= 480;
  }

  vga->printString = printString;
  vga->setTextColor = setTextColor;
  vga->getTextColor = getTextColor;
  vga->setTextSize = setTextSize;
  vga->getTextSize = getTextSize;
  vga->setTextCursorPos = setTextCursor;
  vga->clrscr = clrscr;
  vga->setTextCursorVisible = setTextCursorVisible;
  vga->setTextCursorBlink = setTextCursorBlink;
  vga->get_blink_interval = get_blink_interval;
  vga->set_blink_interval = set_blink_interval;
  vga->pchar = tft_write;
  vga->set_vga_data_array = set_vga_data_array;

  return vga;
}

 