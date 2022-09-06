#include <Arduino.h>
// #include <Serial.h>



void setup() {
  Serial.begin(19200);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  analogWrite(2, 0);
  // analogWrite(3, 225);
  // analogWrite(4, 225);
  // analogWrite(5, 225);
  // analogWrite(6, 225);
  // analogWrite(7, 225);
  // analogWrite(8, 225);
}

byte readByte;

bool LED_STAT = LOW;

static int MOTOR_PIN_1 = 8;

void loop() {
  
  // analogWrite(2, 255);
  // analogWrite(3, 255);
  // analogWrite(4, 255);
  // analogWrite(5, 255);
  // analogWrite(6, 255);
  // analogWrite(7, 255);
  // analogWrite(8, 255);

  // delay(2000);

  
  // analogWrite(2, 0);
  // analogWrite(3, 0);
  // analogWrite(4, 0);
  // analogWrite(5, 0);
  // analogWrite(6, 0);
  // analogWrite(7, 0);
  // analogWrite(8, 0);

  // delay(2000);


  if(Serial.available()){
    Serial.readBytes(&readByte, 1);
    // Serial.write(readByte);
    Serial.write(readByte);
    analogWrite(MOTOR_PIN_1, readByte);
    digitalWrite(LED_BUILTIN, readByte);
  }

  delay(20);
}