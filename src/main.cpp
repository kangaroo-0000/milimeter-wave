#include <Arduino.h>

// Motor, Encoder, and Alarm Pins
const int motor_pin_1 = 5;  // pul+
const int motor_pin_2 = 4;  // pul-
const int motor_pin_3 = 3;  // dir+
const int motor_pin_4 = 2;  // dir-
const int encoder_pin_1 = 6;
const int encoder_pin_2 = 7;
const int alarm_pin_1 = 13;  // alm+
const int alarm_pin_2 = 12;  // alm-

void stepCCW(int steps, float stepAngle);
void stepCW(int steps, float stepAngle);
void stop(void);

void stepCW(int steps, float stepAngle) {
  int i, j = 0;
  int delay_time = 10;
  int innerSteps = (int)(stepAngle / 0.18);
  for (i = 1; i <= steps; i++) {
    for (j = 1; j <= innerSteps; j++) {
      digitalWrite(motor_pin_1, HIGH);
      digitalWrite(motor_pin_2, LOW);
      digitalWrite(motor_pin_3, LOW);
      digitalWrite(motor_pin_4, HIGH);
      delay(delay_time);
      digitalWrite(motor_pin_1, LOW);
      digitalWrite(motor_pin_2, HIGH);
      digitalWrite(motor_pin_3, LOW);
      digitalWrite(motor_pin_4, HIGH);
      delay(delay_time);
      digitalWrite(motor_pin_1, LOW);
      digitalWrite(motor_pin_2, HIGH);
      digitalWrite(motor_pin_3, HIGH);
      digitalWrite(motor_pin_4, LOW);
      delay(delay_time);
      digitalWrite(motor_pin_1, HIGH);
      digitalWrite(motor_pin_2, LOW);
      digitalWrite(motor_pin_3, HIGH);
      digitalWrite(motor_pin_4, LOW);
      delay(delay_time);
    }
    delay(500);
  }
}

void stepCCW(int steps, float stepAngle) {
  int i, j = 0;
  int delay_time = 10;
  int innerSteps = (int)(stepAngle / 0.18);
  for (i = 1; i <= steps; i++) {
    for (j = 1; j <= innerSteps; j++) {
      digitalWrite(motor_pin_1, HIGH);
      digitalWrite(motor_pin_2, LOW);
      digitalWrite(motor_pin_3, HIGH);
      digitalWrite(motor_pin_4, LOW);
      delay(delay_time);  // in ms
      digitalWrite(motor_pin_1, LOW);
      digitalWrite(motor_pin_2, HIGH);
      digitalWrite(motor_pin_3, HIGH);
      digitalWrite(motor_pin_4, LOW);
      delay(delay_time);
      digitalWrite(motor_pin_1, LOW);
      digitalWrite(motor_pin_2, HIGH);
      digitalWrite(motor_pin_3, LOW);
      digitalWrite(motor_pin_4, HIGH);
      delay(delay_time);
      digitalWrite(motor_pin_1, HIGH);
      digitalWrite(motor_pin_2, LOW);
      digitalWrite(motor_pin_3, LOW);
      digitalWrite(motor_pin_4, HIGH);
      delay(delay_time);
    }  // each step takes 40ms to complete
    delay(500);
  }
}

void stop(void) {
  digitalWrite(motor_pin_1, LOW);
  digitalWrite(motor_pin_2, LOW);
  digitalWrite(motor_pin_3, LOW);
  digitalWrite(motor_pin_4, LOW);
}

void setup() {
  pinMode(motor_pin_1, OUTPUT);
  pinMode(motor_pin_2, OUTPUT);
  pinMode(motor_pin_3, OUTPUT);
  pinMode(motor_pin_4, OUTPUT);
  pinMode(alarm_pin_1, INPUT_PULLUP);
  pinMode(alarm_pin_2, INPUT_PULLUP);
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() >= 4) {
    byte command = Serial.read();
    byte highByte = Serial.read();
    byte lowByte = Serial.read();
    int numSteps = (highByte << 8) | lowByte;
    byte stepAngleTenths = Serial.read();

    // Convert tenths of a degree to actual angle if needed
    float stepAngle = stepAngleTenths / 10.0;

    switch (command) {
      case 0b001:  // step counter-clockwise
        stepCCW(numSteps, stepAngle);
        Serial.write(1);
        break;
      case 0b010:  // step clockwise
        stepCW(numSteps, stepAngle);
        Serial.write(2);
        break;
      case 0b011:  // stop motor
        stop();
        Serial.write(3);
        // sendCurrentPosition(motor);
        break;
    }
  }
}
