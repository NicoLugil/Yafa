/* vim: set filetype=cpp: */

// Nico Lugil

#include <Console.h>
#include "TinkerKit.h"
#include "YafaDebounce.h"
#include "BridgeComm.h"

#define PIN_CO2 2
#define PIN_TEMP 10
#define PIN_COOL 7
#define PIN_HEAT 5

TKRelay Cool(PIN_COOL);
TKRelay Heat(PIN_HEAT);
YafaDebounce CO2(PIN_CO2,20); // TODO - tweak MaxCnt
BridgeComm myBridgeComm;

void setup() {
  pinMode(PIN_TEMP, INPUT);
  pinMode(PIN_COOL, OUTPUT);
  pinMode(PIN_HEAT, OUTPUT);
  
  CO2.init();

  myBridgeComm.begin();

  while(!Console)
  {
  }
  Console.println("Console started");
}

void loop() {

   if(CO2.is_falling())
   {
      Console.println("Fall");
   }
   if(CO2.is_rising())
   {
      Console.println("Rise");
   }

   if(myBridgeComm.check_for_command())
   {
      Console.println(myBridgeComm.rx_command_buff);
      Console.println(myBridgeComm.rx_value_buff);
      strncpy(myBridgeComm.tx_command_buff,"Temperature",myBridgeComm.COMMAND_LEN);
      strncpy(myBridgeComm.tx_value_buff,"21.5",myBridgeComm.VALUE_LEN);
      myBridgeComm.send();
   }


  
   delay(200);

}
