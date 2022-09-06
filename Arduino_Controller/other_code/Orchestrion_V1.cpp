#include <Arduino.h>
// #include <Serial.h>

class solenoid
{
private:
  uint32_t pulseDelay = 30000; // Delay between steps, in microseconds
  uint8_t drivePin;
  uint32_t currWait = 0;
  uint8_t solenoidStatus = 0;

public:
  solenoid(uint8_t _drivePin){
    drivePin = _drivePin;
    pinMode(drivePin, OUTPUT);
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(drivePin, LOW);
    digitalWrite(LED_BUILTIN, LOW);
  }

  void pulse(){
    solenoidStatus = 1;
    digitalWrite(LED_BUILTIN, HIGH);
    digitalWrite(drivePin, HIGH);
  };

  void updatePulseDelay(uint32_t _pulseDelay){
    pulseDelay = _pulseDelay;
  }

  void update(uint16_t loopTime);
};

void solenoid::update(uint16_t loopTime){
  if(solenoidStatus == 0) return;

  currWait += loopTime;  
  if(currWait < pulseDelay) return; // Do not step if too soon
  
  digitalWrite(LED_BUILTIN, LOW);
  digitalWrite(drivePin, LOW);
  solenoidStatus = 0;
  currWait = 0;
}





class dynStepper
{
private:
  uint16_t stepDelay = 2000; // Delay between steps, in microseconds
  // uint16_t rampTime = 0;  // Time to ramp up to full speed
  uint8_t pinSet[4];; //Defined output pins

  int32_t currentPos = 0;
  int32_t targetPos = 0;

  uint16_t currWait = 0;

public:
  dynStepper(uint8_t _pinA, uint8_t _pinB, uint8_t _pinC, uint8_t _pinD);
  void update(uint16_t loopTime);
  void setTarget(long int _target){targetPos = _target;}
};

dynStepper::dynStepper(uint8_t _pin0, uint8_t _pin1, uint8_t _pin2, uint8_t _pin3){
  pinSet[0] =  _pin0;
  pinSet[1] =  _pin1;
  pinSet[2] =  _pin2;
  pinSet[3] =  _pin3;

  for(size_t ii=0; ii<4; ii++){
    pinMode(pinSet[ii], OUTPUT);
  }
  digitalWrite(pinSet[0], HIGH); // Set initial step
}

void dynStepper::update(uint16_t loopTime){
  currWait += loopTime;
  
  if(currWait < stepDelay) return; // Do not step if too soon

  currWait -= stepDelay;
  if(currWait > stepDelay/4) currWait = 0; // if delay has been long for some reason don't go too fast and miss steps

  if(currentPos < targetPos){
    digitalWrite(pinSet[(unsigned int)currentPos % 4], LOW);
    currentPos += 1;
    digitalWrite(pinSet[(unsigned int)currentPos % 4], HIGH);
  }
  else if(currentPos > targetPos){
    digitalWrite(pinSet[(unsigned int)currentPos % 4], LOW);
    currentPos -= 1;
    digitalWrite(pinSet[(unsigned int)currentPos % 4], HIGH);
  }
  else{
    digitalWrite(pinSet[(unsigned int)currentPos % 4], LOW);
  }
}



dynStepper mainStep(30, 32, 34, 36); // Declare primary stepper class

solenoid driveSolenoid(53);

uint8_t commandSel;
int32_t readInt;
uint32_t readUint;

double currTime;
double lastTime;

void setup() {
  Serial.begin(19200);
  currTime = micros();
  lastTime = micros();
  delay(500);
  driveSolenoid.pulse();

}

void loop() {
  currTime = micros();
  uint16_t timeGap = currTime - lastTime;
  lastTime = currTime;
  
  if(Serial.available()){
    commandSel = Serial.read();

    Serial.write(commandSel);

    switch (commandSel)
    {
    case 1: // Pulse Solenoid
      driveSolenoid.pulse();
      break;
      
    case 2: // Set Stepper Position
      Serial.readBytes((byte*)(&readInt), 4);
      mainStep.setTarget(readInt);
      break;

    case 3: // Set Solenoid Delay
      Serial.readBytes((byte*)(&readUint), 4);
      driveSolenoid.updatePulseDelay(readUint);
      break;

    default:
      break;
    }
  }

  mainStep.update(timeGap);
  driveSolenoid.update(timeGap);
}