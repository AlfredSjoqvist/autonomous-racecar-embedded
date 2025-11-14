/** Working hall sensor implementation. Counts the pulses from both wheels
 * and transmits their average through UART.
 */
#include <avr/interrupt.h>
#include <avr/io.h>
#define F_CPU 16000000UL
#include <stdbool.h>
#include <util/delay.h>

static uint8_t volatile pulse_cnt_l, pulse_cnt_r;
uint8_t volatile adc_result = 0;

bool listen_for_duty_cycle = false;
uint16_t const UBRRn = 103;

void USART_Init(uint16_t UBRRn);
void USART_Transmit(uint8_t data);

int main(void) {
  DDRD = (0 << PORTD3) | (PORTD2); // Set pin 16 to input from hall sensor
  PORTD = (1 << PORTD3) | (1 << PORTD2);

  // Set interrupt 1 & 0 to falling-edge.
  EICRA = (1 << ISC11) | (1 << ISC01);
  // Enable interrupt 1 & 0.
  EIMSK = (1 << INT1) | (1 << INT0);

  // set timer1 in CTC mode, interrupt every 125 clk/32 cycle
  TCCR1B = (1 << CS12) | (0 << CS11) | (0 << CS10) | (1 << WGM12);
  TCCR1C = (1 << FOC1A);
  // when timer1 reaches the OCR2A value an interrupt is triggered.
  TIMSK1 = (1 << OCIE1A);
  // when timer1 counts up to this value an interrupt is triggered.
  OCR1A = 0x186A;

  // Initialize ADC
  ADMUX = (1 << ADLAR) |
          (0 << MUX0 | (1 << REFS0)); // Left adjust, reference voltage
  ADCSRA = (1 << ADEN) | (1 << ADIE) | (1 << ADPS1) |
           (1 << ADPS2); // Enable ADC, enable ADC interrupt

  // Initialize USART0.
  USART_Init(UBRRn);

  sei();

  while (1) {
    if (!(ADCSRA & (1 << ADSC))) {
      ADCSRA |= (1 << ADSC);
    }
  }
}

ISR(INT1_vect) {
  _delay_us(500);

  if (!(PIND & (1 << PORTD2))) {
    pulse_cnt_r++;
  }
}

ISR(INT0_vect) {
  _delay_us(500);
  if (!(PIND & (1 << INT0))) {
    pulse_cnt_l++;
  }
}

ISR(TIMER1_COMPA_vect) {
  USART_Transmit(255);

  if (adc_result == 255) {
    adc_result--;
  }

  if (pulse_cnt_l == 255) {
    pulse_cnt_l--;
  }

  if (pulse_cnt_r == 255) {
    pulse_cnt_r--;
  }

  USART_Transmit(pulse_cnt_l);
  USART_Transmit(pulse_cnt_r);
  USART_Transmit(adc_result);

  pulse_cnt_l = 0;
  pulse_cnt_r = 0;
}

ISR(ADC_vect) {
  adc_result = ADCH; // Read the result from the ADC
}

/** input: USART baud rate register, initializes UART */
void USART_Init(uint16_t baud_reg) {

  UBRR0 = baud_reg;
  // Enable receiver and transmitter
  UCSR0B = (1 << RXEN0) | (1 << TXEN0);
  // Set frame format: 8data, 2stop bit
  UCSR0C = (1 << USBS0) | (3 << UCSZ00);
}

/** Transmit a byte of data. */
void USART_Transmit(uint8_t data) {
  // Wait for empty transmit buffer
  while (!(UCSR0A & (1 << UDRE0))) {
  }
  // Put data into buffer, sends the data.
  UDR0 = data;
}
