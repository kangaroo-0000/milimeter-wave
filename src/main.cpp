#include <Arduino.h>
#include <Encoder.h>

// Motor and Encoder Pins
const int motor_pin_1 = 5;  // pul+
const int motor_pin_2 = 4;  // pul-
const int motor_pin_3 = 3;  // dir+
const int motor_pin_4 = 2;  // dir-
const int encoder_pin_1 = 18;
const int encoder_pin_2 = 19;

Encoder myEnc(encoder_pin_1, encoder_pin_2);
long oldPosition = -999;

void setup() {
  pinMode(motor_pin_1, OUTPUT);
  pinMode(motor_pin_2, OUTPUT);
  pinMode(motor_pin_3, OUTPUT);
  pinMode(motor_pin_4, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() >= 3) {
    byte command = Serial.read();
    int angle = Serial.read() << 8;  // High byte
    angle |= Serial.read();          // Low byte

    switch (command) {
      case 0b001:
        stepCCW(200);
        sendAcknowledgement(0b001);
        break;
      case 0b010:
        stepCW(200);
        sendAcknowledgement(0b010);
        break;
      case 0b011:
        stopMotor();
        sendAcknowledgement(0b011);
        break;
      case 0b100:
        returnToOrigin();
        sendAcknowledgement(0b100);
        break;
      case 0b101:
        setStartAngle(angle);
        sendAcknowledgement(0b101);
        break;
      case 0b110:
        setEndAngle(angle);
        sendAcknowledgement(0b110);
        break;
    }
  }
}

void sendAcknowledgement(byte command) {
  Serial.write(command);
  getCurrentPosition();  // Send the current position back
}

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
  }
}

void stopMotor() {
  // Implementation to stop the motor
}

void returnToOrigin() {
  // Implementation to return to the original position
}

void setStartAngle(int angle) {
  // Implementation to set the start angle
}

void setEndAngle(int angle) {
  // Implementation to set the end angle
}
