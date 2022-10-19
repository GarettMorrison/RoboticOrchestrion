#include <Arduino.h>

// Load custom lib
#include "InstrumentControl.h"


// Define calliope
uint8_t calliopePins[] = {22, 24, 26, 28, 30, 32, 34, 36};
discretePolyphone calliope(1, calliopePins, 8);


// // Define orchestrion strings
// orchestrion orchString_1(2, 24, 28, 32, 34, 36, 38);
// orchestrion orchString_2(3, 22, 26, 40, 42, 44, 46);
// orchestrion orchString_3(4, 0, 0, 0, 0, 0, 0);
// orchestrion orchString_4(5, 0, 0, 0, 0, 0, 0);


uint8_t comm_data[40];
uint8_t comm_len = 0;

double currTime;
double lastTime;


void setup() {
  // aal.begin(19200);
  Serial.begin(9600);
  currTime = micros();
  lastTime = micros();
  delay(500);
}


void loop() {
  currTime = micros();
  uint16_t timeGap = currTime - lastTime;
  lastTime = currTime;
  
  if(Serial.available()){
    comm_data[comm_len] = (uint8_t)Serial.read();
    comm_len += 1;
    // comm_len += (uint8_t)Serial.readBytes(comm_data+comm_len, 40-comm_len);

    // for(uint8_t ii=0; ii<comm_len; ii++){
    //   Serial.write(comm_data[ii]);
    // }
  }



  // Call execute on all instruments
  if(comm_len > 2){
    calliope.execute(timeGap, comm_data, comm_len);

    // orchString_1.execute(timeGap, comm_data, comm_len);
    // orchString_2.execute(timeGap, comm_data, comm_len);
    // orchString_3.execute(timeGap, comm_data, comm_len);
    // orchString_4.execute(timeGap, comm_data, comm_len);
  }
}