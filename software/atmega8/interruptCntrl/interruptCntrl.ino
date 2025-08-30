#include <avr/io.h>
#include <util/atomic.h>
#include <util/delay.h>

//When cpu say FC0,FC1 and FC2  = 1,1,1 but no interrupt active.
#define CPU_INT_ACK_WRONG     0x80
//When arrive a irq resquest but we have one active irq in curse
#define IRQ_REQUEST_LOST      0x81
//ACK sem interrupção
#define ACK_WITHOUT_INT       0x82
//Irq <level> must be released
#define IRQ_MUST_BE_RELEASED  0x83

// Definições dos pinos IPL no PORTB
#define IPL0  PC0
#define IPL1  PC1  
#define IPL2  PC2
#define IPL_MASK ((1 << IPL0) | (1 << IPL1) | (1 << IPL2))

// Definições dos pinos de IRQ no PORTD
#define IRQ1_PIN  PD2
#define IRQ2_PIN  PD3
#define IRQ3_PIN  PD4
#define IRQ4_PIN  PD5
#define IRQ5_PIN  PD6
#define IRQ7_PIN  PD7
#define ALL_IRQ_MASK ((1<<IRQ1_PIN)|(1<<IRQ2_PIN)|(1<<IRQ3_PIN)|(1<<IRQ4_PIN)|(1<<IRQ5_PIN)|(1<<IRQ7_PIN))


#define FC0 PB2
#define FC1 PB3
#define FC2 PB4

// Configuração adicional dos pinos
#define VPA_PIN PC5  // Usando PC3 para VPA (ajuste conforme seu hardware)

unsigned char irq_s[8]={0,0,0,0,0,0,0,0};

// Variáveis globais
volatile uint8_t active_irq = 0;
volatile uint8_t irq_being_processed = 0;

// Função de verificação do bus
void check_bus_cycle() {
    if ((PINB & 0x1C) == 0x1C) {  // FC0-FC2 = 111
        if (active_irq != 0) {
            Serial.print("check_bus_cycle: PINB ");
            Serial.print( PINB,16);
            Serial.print("Limpando o vetor de irqs: ");
            Serial.println(active_irq,16);
            irq_s[active_irq]=0;
            
            PORTC |= (1 << VPA_PIN);   // Assert VPA
            _delay_us(0.1);
            set_ipl(0);                // Remove IPL
            _delay_us(0.1);
            PORTC &= ~(1 << VPA_PIN);  // De-assert VPA
            //set_ipl(0) já limpou essa variavel.
            //active_irq = 0;            // Finaliza tratamento
            Serial.println("vou aguardar fc0-fc2 deassert");
            while(((PINB & 0x1C) == 0x1C) ){
               _delay_us(1000);
            }            
        }
        else {
            // ❌ ERRO: ACK sem interrupção
            log_error(ACK_WITHOUT_INT);
        }
    }
}
void log_error(uint8_t error){

}

// Configuração dos ports
void setup_ports() {
    // Configurar PB0-PB2 como saídas (IPL0-IPL2) + VPA_PIN
    DDRC |= (1 << IPL0) | (1 << IPL1) | (1 << IPL2) | (1 << VPA_PIN);
    PORTC &= ~IPL_MASK;  // Inicializa em 0
    
    // Configurar PB1 como saída (OC1A - Debug)
    DDRB |= (1 << PB1)  ;
    
    // Configurar PB3-PB5 como entradas (FC0-FC2) com pull-up
    DDRB &= ~((1 << FC0) | (1 << FC1) | (1 << FC2));
    PORTB |= ((1 << FC0) | (1 << FC1) | (1 << FC2));
    
    // VPA inicialmente inativo    
    PORTC |= (1 << VPA_PIN);  

    // Configura PD0-PD5 como entradas com pull-up
    DDRD &= ~ALL_IRQ_MASK;
    PORTD |= ALL_IRQ_MASK;    
}

void setup_timer1() {
    TCCR1A = (1 << COM1A0);    // Toggle OC1A on compare match
    TCCR1B = (1 << WGM12) | (1 << CS11);  // CTC mode, prescaler 8
    OCR1A = 500;              // 1ms period
    TIMSK |= (1 << OCIE1A);    // Habilitar interrupção
}

//volatile uint32_t ms_counter = 0;

ISR(TIMER1_COMPA_vect) {
//  ms_counter++;
  start_irq(6);  // Gera IRQ nível 6
}

uint8_t check_irq_pins_status() {
    return (~PIND) & ALL_IRQ_MASK;
}

uint8_t get_irq_started() {
    uint8_t status = check_irq_pins_status();
    if (status & (1<<IRQ7_PIN)) return 7;
    if (status & (1<<IRQ5_PIN)) return 5;
    if (status & (1<<IRQ4_PIN)) return 4;
    if (status & (1<<IRQ3_PIN)) return 3;
    if (status & (1<<IRQ2_PIN)) return 2;
    if (status & (1<<IRQ1_PIN)) return 1;
    return 0;
}
// Função principal de verificação de IRQs
void verifica_interrupts() {
    uint8_t started_irq = get_irq_started();
    
    if (started_irq > 0) {
        set_ipl(started_irq);
        
        while (get_irq_started() == active_irq) {
            // Espera IRQ ser liberada
        }        
        set_ipl(0);
    }
}
// ✅ Função set_ipl CORRIGIDA
void set_ipl(uint8_t level) {
    level &= 0x07;
    if( irq_s[level] == 0 ){
      PORTC = (PORTC & 0xF8) | level;  // Limpa E depois seta
      irq_s[level]=level;
      Serial.print("set_ipl: PORTC ");
      Serial.print(PORTC,16);  
      Serial.print(" level: ");
      Serial.println(level,16);  
      active_irq = irq_s[level];
    }
    else{
      //❌ ERRO: Irq <level> must be released
      log_error(IRQ_MUST_BE_RELEASED);
    }   
}

void start_irq(uint8_t new_irq){
  if (new_irq != 0 && active_irq == 0) {
    Serial.print("loop: new_irq=");
    Serial.print(new_irq,16);  
    Serial.print("    active_irq=");
    Serial.println(active_irq,16);  
    active_irq = new_irq;
    set_ipl(active_irq);
    Serial.println("Setting active irq");            
  }else{
    //❌ ERRO: Irq <new_irq> lost
    log_error(IRQ_REQUEST_LOST);
  }
}

#define TIMEOUT  500
long timer1=millis()+TIMEOUT;

void setup(){
  Serial.begin(9600);
  Serial.println("Teste do gerenciador de interrupção"); 
    setup_ports();
    setup_timer1();
    sei();
    pinMode(LED_BUILTIN, OUTPUT);    
    timer1=millis()+TIMEOUT;
}

#define LED_PIN PB5  // Exemplo: LED no PB5 (ajuste conforme seu hardware)
#define LED_PORT PORTB


void loop() {
  uint8_t new_irq;

  while(1) {
    // 1️⃣ Verificação SÍNCRONA das IRQs
    new_irq = get_irq_started();
    if( new_irq > 0)
      start_irq(new_irq);

    // 2️⃣ Verificação SÍNCRONA do ACK
    check_bus_cycle();

    //Activity led
    if ( millis() > timer1 ){
      timer1=millis()+TIMEOUT;
      LED_PORT ^= (1 << LED_PIN);  // toggle LED
    }
  }
}
