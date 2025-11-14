#include <avr/interrupt.h>
#include <avr/io.h>

uint8_t volatile adcResult = 0;

int main(void) {
  // Initialize Ports
  DDRB = 0xff; // Set PORTB as output

  // Initialize ADC
  ADMUX = (1 << ADLAR) |
          (0 << MUX0 | (1 << REFS0)); // Left adjust result and select ADC0
  ADCSRA = (1 << ADEN) | (1 << ADIE) | (1 << ADPS2) |
           (1 << ADPS1); // Enable ADC, enable ADC interrupt, prescaler 8
  sei();                 // Enable global interrupts

  while (1) {
    ADCSRA |= (1 << ADSC); // Start AD conversion
                           // Delay?
  }
}

// ADC conversion complete ISR
ISR(ADC_vect) {
  adcResult = ADCH;  // Read the result from the ADC
  PORTB = adcResult; // Output the ADC result to PORTB
  ADCSRA |=
      (1
       << ADIF); // Clear the ADC interrupt flag (optional, usually not needed)
}