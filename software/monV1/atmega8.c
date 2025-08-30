// Configurar Timer1 para interrupção a cada 1ms
void setup_timer() {
  // Timer1 em CTC mode para 1kHz (1ms)
  TCCR1B = (1 << WGM12) | (1 << CS11); // Prescaler 8
  OCR1A = 1999; // 16MHz/8/2000 = 1000Hz (1ms)
  TIMSK = (1 << OCIE1A); // Habilitar interrupção

  // Configurar PB3 como saída para OC1A
  DDRB |= (1 << PB3);

  // Timer1 em CTC mode (WGM13:0 = 4)
  // OC1A toggle on compare match
  TCCR1A = (1 << COM1A0);  // Toggle OC1A on compare match
  TCCR1B = (1 << WGM12) | (1 << CS11);  // CTC mode, prescaler 8

  // Valor para comparação (1ms)
  OCR1A = 1999;  // 16MHz/8/2000 = 1000Hz (1ms)

  // Habilitar interrupção do comparador A
  TIMSK |= (1 << OCIE1A);
}

// Interrupção do timer a cada 1ms
ISR(TIMER1_COMPA_vect) {
  static uint32_t ms_counter = 0;
  ms_counter++;

  // Gerar IRQ nível 6 a cada 1ms
  set_ipl(6); // Nível 6 (110 binário)

}

// Monitoramento do ciclo de barramento
void check_bus_cycle() {
  if ((PINB & 0x38) == 0x38) { // PB3-PB5 (FC0-FC2) = 111
    if ((PINC & 0x07) == 0x06) { // PC0-PC2 (A1-A3) = 110 (nível 6)
      // CPU está reconhecendo nossa interrupção
      _delay_us(0.1); // Delay mínimo
      set_ipl(0); // Remover IRQ imediatamente
    }
  }
}

void set_ipl(uint8_t level) {
  PORTB = (PORTB & 0xF8) | (level & 0x07);
}
