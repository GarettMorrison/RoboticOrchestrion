#ifndef COMP_DRIVE
#define COMP_DRIVE

#include <Arduino.h>

class strikeSol{
  private:
    uint32_t pulseDelay = 35000; // Delay between steps, in microseconds
    uint8_t drivePin;
    uint32_t currWait = 0;
    uint8_t solenoidStatus = 0;

  public:
    strikeSol(){};
    strikeSol(uint8_t _drivePin);

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



class holdSol{
  private:
    uint8_t drivePin;

  public:
    holdSol(){};
    holdSol(uint8_t _drivePin){
        drivePin = _drivePin;
        pinMode(drivePin, OUTPUT);
        digitalWrite(drivePin, LOW);
    };

    void set(uint8_t setVal){
      digitalWrite(drivePin, setVal);
    };
};



// Dynamically controlled stepper
class dynStepper{
  private:
    uint32_t stepDelay = 2000; // Delay between steps, in microseconds
    // uint16_t rampTime = 0;  // Time to ramp up to full speed
    uint8_t pinSet[4];; //Defined output pins

    int32_t currentPos = 0;
    int32_t targetPos = 0;

    uint32_t currWait = 0;

  public:
    dynStepper(){};
    dynStepper(uint8_t _pinA, uint8_t _pinB, uint8_t _pinC, uint8_t _pinD);
    void update(uint16_t loopTime);
    void setTarget(long int _target){targetPos = _target;}
    void setStepDelay(uint16_t _stepDelay){stepDelay = _stepDelay;}
    void setZero(){currentPos = 0; targetPos = 0;}
};


#endif