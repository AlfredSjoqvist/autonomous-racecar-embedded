/*
 * Uart_utv.c
 *
 * Created: 2024-11-04 11:33:55
 * Author : gussj945, alfsj019, kacum, rikag
 */

#include <avr/interrupt.h>
#include <avr/io.h>
#include <stdbool.h>

bool listenForDutyCycle = false;
bool listenForServoCycle = false;
bool incomingSignal = false;
uint8_t dutyCycle = 0;
uint8_t servoCycle = 128;
uint8_t directionState = 1; // 1 for forward, 2 for backward, 3 and 4 for brake
enum state { NO_SIGNAL, SERVO, GAS, DIRECTION };

void set_period(uint8_t period);
void USART_Init(uint16_t baud_reg);
void USART_Transmit(uint8_t data);
uint8_t USART_Receive(void);
void USART_Flush(void);

int main(void) {

  /*I/O init*/
  DDRD = (1 << PORTD2);
  DDRC = (1 << PORTC1);
  DDRB = (1 << PORTB3);
  DDRA = (1 << PORTA4);

  /* Gas setting init: */
  OCR0A = dutyCycle;
  TCCR0A = (1 << WGM00) | (1 << WGM01) | (1 << COM0A1);
  TIMSK0 = (1 << TOIE0);
  TCCR0B = (1 << CS01);

  /* Servo setting init: */
  TCCR1B = (1 << WGM12) | (1 << CS11);
  OCR1A = 0x9fef;
  TIMSK1 = (1 << OCIE1B) | (1 << OCIE1A);
  set_period(servoCycle);

  /* Direction setting init: */
  set_direction();

  /* Direction setting init: */
  set_direction();

  /* Set global interrupts:*/
  sei();

  uint16_t UBRRn = 103;
  uint8_t received;
  USART_Init(UBRRn); // Initialize USART with the calculated UBRR value

  enum state st = NO_SIGNAL;

  while (1) {

    received = USART_Receive();

    switch (st) {
    case NO_SIGNAL:
      st = received == '\0' ? GAS : NO_SIGNAL;
      break;
    case GAS:

      if (received != '\0') {
        dutyCycle = received == 1 ? 0 : received;
        st = SERVO;
      } else {
        st = NO_SIGNAL;
      }
      break;
    case SERVO:
      if (received != '\0') {
        servoCycle = received == 1 ? 0 : received;
        st = DIRECTION;
      } else {
        st = NO_SIGNAL;
      }
      break;
    case DIRECTION:
      if (received >= 1 && received <= 4) {
        directionState = received;
        set_direction();
      }
      st = NO_SIGNAL;
      break;
    }
  }
}

/** Initialize uart. Input: Usart baude rate register. */
void USART_Init(uint16_t baud_reg) {

  UBRR0 = baud_reg;
  // Enable receiver and transmitter
  UCSR0B = (1 << RXEN0) | (1 << TXEN0);
  /* Set frame format: 8data, 2stop bit */
  UCSR0C = (1 << USBS0) | (3 << UCSZ00);
}

/** Transmit a byte of data through uart. */
void USART_Transmit(uint8_t data) {
  /* Wait for empty transmit buffer*/
  while (!(
      UCSR0A &
      (1 << UDRE0))) /*UDREn Data register empty flag TXCn - transmit complete*/
    ;
  /* Put data into buffer, sends the data */
  UDR0 = data;
}

/* Waits for the RXCn flag (Receive complete flag) to be high then returns to
 * I/O location UDRn */
uint8_t USART_Receive(void) {
  /* Wait for data to be received */
  while (!(UCSR0A & (1 << RXC0)))
    ;
  /* Get and return received data from buffer*/
  return UDR0;
}

/** Set the correct wave for the servo signal */
void set_period(uint8_t period) {
  uint16_t const min_period = (1 << 11) + 4;
  uint16_t const new_period = min_period + (period << 3);

  OCR1B = new_period;
}

/** Set the brake and direction pins based on the direction byte */
void set_direction() {

  switch (directionState) {
  case 1:
    PORTC &= ~(1 << PORTC1);
    PORTD &= ~(1 << PORTD2);
    break;
  case 2:
    PORTC &= ~(1 << PORTC1);
    PORTD |= (1 << PORTD2);
    break;
  case 3:
  case 4:
    dutyCycle = 0;
    PORTC |= (1 << PORTC1);
    break;
  }
}

/* Interrupts */
ISR(TIMER0_OVF_vect) { OCR0A = dutyCycle; }

ISR(TIMER1_COMPA_vect) {
  PORTA |= (1 << PORTA4);
  set_period(servoCycle);
}

ISR(TIMER1_COMPB_vect) { PORTA &= 0xff & (0 << PORTA4); }
