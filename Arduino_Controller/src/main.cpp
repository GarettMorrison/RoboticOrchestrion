#include <Arduino.h>
// #include <Serial.h>

class solenoid{
  private:
    uint32_t pulseDelay = 35000; // Delay between steps, in microseconds
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
  uint32_t stepDelay = 2000; // Delay between steps, in microseconds
  // uint16_t rampTime = 0;  // Time to ramp up to full speed
  uint8_t pinSet[4];; //Defined output pins

  int32_t currentPos = 0;
  int32_t targetPos = 0;

  uint32_t currWait = 0;

public:
  dynStepper(uint8_t _pinA, uint8_t _pinB, uint8_t _pinC, uint8_t _pinD);
  void update(uint16_t loopTime);
  void setTarget(long int _target){targetPos = _target;}
  void setStepDelay(uint16_t _stepDelay){stepDelay = _stepDelay;}
  void setZero(){currentPos = 0; targetPos = 0;}
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



// Define drive solenoids
solenoid tenor_right(22);
solenoid alto_right(24); 
solenoid tenor_left(26);
solenoid alto_left(28);

// Define note solenoids
dynStepper alto_step(32, 34, 36, 38);  
dynStepper tenor_step(40, 42, 44, 46);

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
}

void loop() {
  currTime = micros();
  uint16_t timeGap = currTime - lastTime;
  lastTime = currTime;
  
  if(Serial.available()){
    commandSel = Serial.read();

    Serial.write(commandSel);

    /*
    alto_right
    tenor_right
    alto_left
    tenor_left
    alto_step
    tenor_step
    */

    switch (commandSel)
    {
    // Pulse Solenoid 
    case 1: // alto_right
      alto_right.pulse();
      break;
    case 2: // tenor_right
      tenor_right.pulse();
      break;
    case 3: // alto_left
      alto_left.pulse();
      break;
    case 4: // tenor_left
      tenor_left.pulse();
      break;
    
    // Set pulse delay
    case 5: // alto_right
      Serial.readBytes((byte*)(&readUint), 4);
      alto_right.updatePulseDelay(readUint);
      break;
    case 6: // tenor_right
      Serial.readBytes((byte*)(&readUint), 4);
      tenor_right.updatePulseDelay(readUint);
      break;
    case 7: // alto_left
      Serial.readBytes((byte*)(&readUint), 4);
      alto_left.updatePulseDelay(readUint);
      break;
    case 8: // tenor_left
      Serial.readBytes((byte*)(&readUint), 4);
      tenor_left.updatePulseDelay(readUint);
      break;
    
    // Set stepper position
    case 9: // alto string
      Serial.readBytes((byte*)(&readInt), 4);
      alto_step.setTarget(readInt);
      break;
    case 10: // tenor string
      Serial.readBytes((byte*)(&readInt), 4);
      tenor_step.setTarget(readInt);
      break;

    // Zero stepper
    case 11: // alto string
      alto_step.setZero();
      break;
    case 12: // tenor string
      tenor_step.setZero();
      break;
      
    // Set stepper position
    case 13: // alto string
      Serial.readBytes((byte*)(&readUint), 4);
      alto_step.setStepDelay(readUint);
      break;
    case 14: // tenor string
      Serial.readBytes((byte*)(&readUint), 4);
      tenor_step.setStepDelay(readUint);
      break;

    default:
      break;
    }
  }
  
  alto_step.update(timeGap);
  tenor_step.update(timeGap);

  alto_right.update(timeGap);
  tenor_right.update(timeGap);
  alto_left.update(timeGap);
  tenor_left.update(timeGap);
}