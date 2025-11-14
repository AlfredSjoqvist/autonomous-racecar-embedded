/*
 * steering_signal.c
 *
 * Created: 2024-11-12 10:15:11
 * Author : kacum383
 */

#include <avr/interrupt.h>
#include <avr/io.h>

void set_period(uint8_t period);

int main(void) {
  /* Replace with your application code */

  DDRD = (1 << PORTD5);
  // Set timer1 channel A on compare match (set output to high lvl)
  // TCCR1A = (1<<COM1A1)|(1<<COM1A0);
  // CTN, prescale CLK/8
  TCCR1B = (1 << WGM12) | (1 << CS11);
  // force compare on output A
  TCCR1C = (1 << FOC1A);
  // total period of signal
  OCR1AH = 0x9f;
  OCR1AL = 0xef;

  // OCR1BH = (uint8_t)(4096>>8);
  // OCR1BL = (uint8_t)4096;
  // time that signal is high
  set_period(128);

  TIMSK1 = (1 << OCIE1B) | (1 << OCIE1A);
  sei();

  while (1) {
  }
}

ISR(TIMER1_COMPA_vect) { PORTD = 0xff; }

ISR(TIMER1_COMPB_vect) {
  // Set portd5 to zero when timer1 counts to OCR1B
  // PORTD &= (0<<PORTD5)&0xff;
  PORTD = 0x00;
}

/**  */
void set_period(uint8_t period) {
  uint16_t const min_period = (1 << 11) + 4;
  uint16_t const new_period = min_period + (period << 3);

  OCR1BH = (uint8_t)(new_period >> 8);
  OCR1BL = (uint8_t)new_period;
}
