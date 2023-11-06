#include <Arduino.h>
#include <Encoder.h>

const int motor_pin_1 = 5;  // pul+
const int motor_pin_2 = 4;  // pul-
const int motor_pin_3 = 3;  // dir+
const int motor_pin_4 = 2;  // dir-
const int encoder_pin_1 = 18;
const int encoder_pin_2 = 19;

Encoder myEnc(encoder_pin_1, encoder_pin_2);
long oldPosition = -999;

// put function declarations here:
void stepCW(int steps);
void stepCCW(int steps);
void getCurrentPosition();

void setup() {
  // put your setup code here, to run once:
  pinMode(motor_pin_1, OUTPUT);
  pinMode(motor_pin_2, OUTPUT);
  pinMode(motor_pin_3, OUTPUT);
  pinMode(motor_pin_4, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    char input = Serial.read();
    if (input == 'a') {
      stepCW(200);
    } else if (input == 'b') {
      stepCCW(200);
    }
  }
}

// put function definitions here:
void getCurrentPosition() {
  long newPosition = myEnc.read();
  if (newPosition != oldPosition) {
    oldPosition = newPosition;
    Serial.println(newPosition);
  }
}

void stepCW(int steps) {
  int i = 0;
  int delay_time = 10;  // experimentally derived delay
  for (i = 1; i <= steps; i++) {
    digitalWrite(motor_pin_1, HIGH);
    digitalWrite(motor_pin_2, LOW);
    digitalWrite(motor_pin_3, HIGH);
    digitalWrite(motor_pin_4, LOW);
    getCurrentPosition();
    delay(delay_time);  // in ms
    digitalWrite(motor_pin_1, LOW);
    digitalWrite(motor_pin_2, HIGH);
    digitalWrite(motor_pin_3, HIGH);
    digitalWrite(motor_pin_4, LOW);
    getCurrentPosition();
    delay(delay_time);
    digitalWrite(motor_pin_1, LOW);
    digitalWrite(motor_pin_2, HIGH);
    digitalWrite(motor_pin_3, LOW);
    digitalWrite(motor_pin_4, HIGH);
    getCurrentPosition();
    delay(delay_time);
    digitalWrite(motor_pin_1, HIGH);
    digitalWrite(motor_pin_2, LOW);
    digitalWrite(motor_pin_3, LOW);
    digitalWrite(motor_pin_4, HIGH);
    getCurrentPosition();
    delay(delay_time);
  }  // each step takes 40ms to complete
}

void stepCCW(int steps) {
  int i = 0;
  int delay_time = 10;
  for (i = 1; i <= steps; i++) {
    digitalWrite(motor_pin_1, HIGH);
    digitalWrite(motor_pin_2, LOW);
    digitalWrite(motor_pin_3, LOW);
    digitalWrite(motor_pin_4, HIGH);
    getCurrentPosition();
    delay(delay_time);
    digitalWrite(motor_pin_1, LOW);
    digitalWrite(motor_pin_2, HIGH);
    digitalWrite(motor_pin_3, LOW);
    digitalWrite(motor_pin_4, HIGH);
    getCurrentPosition();
    delay(delay_time);
    digitalWrite(motor_pin_1, LOW);
    digitalWrite(motor_pin_2, HIGH);
    digitalWrite(motor_pin_3, HIGH);
    digitalWrite(motor_pin_4, LOW);
    getCurrentPosition();
    delay(delay_time);
    digitalWrite(motor_pin_1, HIGH);
    digitalWrite(motor_pin_2, LOW);
    digitalWrite(motor_pin_3, HIGH);
    digitalWrite(motor_pin_4, LOW);
    getCurrentPosition();
    delay(delay_time);
  }  // each step takes 40ms to complete
}
