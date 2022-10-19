#include <Arduino.h>
#include "InstrumentControl.h"

uint32_t load_uint32_t(uint8_t arr[]){
    uint32_t i32 = 0;
    for(uint8_t ii=0; ii<4; ii++){
        i32 |= arr[ii];
        i32 <<= 8;
    }
    // uint32_t i32 = arr[0] | (arr[1] << 8) | (arr[2] << 16) | (arr[3] << 24);
    return(i32);
}
uint32_t uint32_A;// predefine variable to load value into



int32_t load_int32_t(uint8_t arr[]){
    int32_t i32 = 0;
    for(uint8_t ii=0; ii<4; ii++){
        i32 |= arr[ii];
        i32 <<= 8;
    }
    // int32_t i32 = arr[0] | (arr[1] << 8) | (arr[2] << 16) | (arr[3] << 24);
    return(i32);
}
int32_t int32_A; // predefine variable to load value into



void reduceQueue(uint8_t comm_data[], uint8_t& comm_len, uint8_t reduceCount){
    for(uint8_t ii=0; ii<comm_len-reduceCount; ii++){
        comm_data[ii] = comm_data[ii+reduceCount];
    }
    comm_len -= reduceCount;
}



bool checkSum(uint8_t comm_data[], uint8_t& comm_len, uint8_t commandLen){
    uint8_t checkSum = 0;
    for(uint16_t ii=0; ii<commandLen-1UL; ii++){
        checkSum += comm_data[ii];
    }
    

    if(checkSum == comm_data[commandLen-1UL]){
        return(1);
    }
    else{
        comm_len = 0; // Clear command queue as there was an error and further commands cannot be trusted
        return(0);
    }
}





orchestrion::orchestrion(uint8_t _ID, uint8_t _solPinL, uint8_t _solPinR, uint8_t _pinA, uint8_t _pinB, uint8_t _pinC, uint8_t _pinD){
    instrumentID = _ID;
    leftSol = strikeSol(_solPinL);
    rightSol = strikeSol(_solPinR);
    fretStep = dynStepper(_pinA, _pinB, _pinC, _pinD);
}

/*
Index [Len required] Command
0 [7] Set Stepper Position
1 [7] Set Stepper Delay
2 [3] Zero Stepper at location
3 [3] Strike LeftSol
4 [3] Strike RightSol
5 [7] Set pulse LeftSol
6 [7] Set pulse RightSol
*/
uint8_t commandCount_orch = 7;
uint8_t commandLens_orch[] = {7, 7, 3, 3, 3, 7, 7};

void orchestrion::execute(uint16_t timeGap, uint8_t comm_data[], uint8_t& comm_len){
    if(comm_len < 3) return; // not enough data for command
    if(comm_data[0] != instrumentID) return; // Return 0 if not correct ID
    
    // Check that command index is in range, clear queue if not
    if(comm_data[1] < commandCount_orch){
        comm_len = 0;
        return;
    }
    if(comm_len < commandLens_orch[comm_data[1]]) return; // if command len is too short return

    // do check sum, if matches execute command
    uint8_t commandLen = commandLens_orch[comm_data[1]];
    if( checkSum(comm_data, comm_len, commandLen) ){
        // All checks passed, execute command
        switch (comm_data[1]){
            // 0 [7] Set Stepper Position
            case 0:
                int32_A = load_int32_t(comm_data+2); // offset of 2 to skid ID and command bytes
                fretStep.setTarget(int32_A);
                break;

            // 1 [7] Set Stepper Delay
            case 1:
                uint32_A = load_uint32_t(comm_data+2); // offset of 2 to skid ID and command bytes
                fretStep.setStepDelay(static_cast<uint16_t>(uint32_A));
                break;

            // 2 [3] Zero Stepper at location
            case 2:
                fretStep.setZero();
                break;

            // 3 [3] Strike LeftSol
            case 3:
                leftSol.pulse();
                break;

            // 4 [3] Strike RightSol
            case 4:
                rightSol.pulse();
                break;

            // 5 [7] Set pulse LeftSol
            case 5:
                uint32_A = load_uint32_t(comm_data+2); // offset of 2 to skid ID and command bytes
                leftSol.updatePulseDelay(uint32_A);
                break;

            // 6 [7] Set pulse RightSol
            case 6:
                uint32_A = load_uint32_t(comm_data+2); // offset of 2 to skid ID and command bytes
                rightSol.updatePulseDelay(uint32_A);
                break;
        }
        
        reduceQueue(comm_data, comm_len, commandLen); // Command complete, remove from queue
    }
}





discretePolyphone::discretePolyphone(uint8_t _ID, uint8_t _notePins[], uint8_t _noteCount){
    instrumentID = _ID;
    notePins = _notePins;
    noteCount = _noteCount;
    
    for(uint8_t ii=0; ii<noteCount; ii++){
        pinMode(notePins[ii], OUTPUT);
    }
}

/*
Index [Len required] Command
0 [4] Enable note
1 [4] Disable note
2 [3] Disable all notes
*/
uint8_t commandCount_poly = 3;
uint8_t commandLens_poly[] = {4, 4, 3};

void discretePolyphone::execute(uint16_t timeGap, uint8_t comm_data[], uint8_t& comm_len){
    if(comm_len < 3) return; // not enough data for command
    if(comm_data[0] != instrumentID) return; // Return 0 if not correct ID
    
    // Check that command index is in range, clear queue if not
    if(comm_data[1] > commandCount_poly){
        comm_len = 0;
        return;
    }



    if(comm_len < commandLens_poly[comm_data[1]]) return; // if command len is too short return


    // do check sum, if matches execute command
    uint8_t commandLen = commandLens_poly[comm_data[1]];
    if( checkSum(comm_data, comm_len, commandLen) ){
        // All checks passed, execute command

        switch (comm_data[1]){
            //0 [4] Enable note
            case 0:
                // Serial.write(0x69);
                // Serial.write(comm_data[2]);
                // Serial.write(notePins[comm_data[2]]);
                // Serial.write(0x69);
                digitalWrite(notePins[comm_data[2]], HIGH);
                break;

            //1 [4] Disable note
            case 1:
                // Serial.write(0x71);
                // Serial.write(comm_data[2]);
                // Serial.write(notePins[comm_data[2]]);
                // Serial.write(0x71);
                digitalWrite(notePins[comm_data[2]], LOW);
                break;
        }

        //2 [3] Disable all notes
        if(comm_data[1] == 2){
            for(uint8_t ii=0; ii<noteCount; ii++){
                digitalWrite(notePins[ii], 0);
            }
        }
        
        reduceQueue(comm_data, comm_len, commandLen); // Command complete, remove from queue
    }
    else{
        comm_len = 0;
    }
}
