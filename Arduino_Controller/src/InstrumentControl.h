#ifndef INSTRUMENT_DEF
#define INSTRUMENT_DEF

#include <Arduino.h>
#include "ComponentDrivers.h"

class orchestrion{
    private:
        uint8_t instrumentID = 255;
        strikeSol leftSol;
        strikeSol rightSol;
        dynStepper fretStep;

    public:
        orchestrion(uint8_t _ID, uint8_t _solPinL, uint8_t _solPinR, uint8_t _pinA, uint8_t _pinB, uint8_t _pinC, uint8_t _pinD);
        void execute(uint16_t timeGap, uint8_t comm_data[], uint8_t& comm_len);
};


// Play multiple instruments simultaneously
class discretePolyphone{
    private:
        uint8_t instrumentID = 255;
        uint8_t* notePins;
        uint8_t noteCount;

    public:
        discretePolyphone(uint8_t _ID, uint8_t _notePins[], uint8_t _noteCount);
        void execute(uint16_t timeGap, uint8_t comm_data[], uint8_t& comm_len);
};


#endif