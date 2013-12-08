/* vim: set filetype=cpp: */

#include <Console.h>
#include <Bridge.h>
#include "TinkerKit.h"
#include "YafaDebounce.h"

#define PIN_CO2 2
#define PIN_TEMP 10
#define PIN_COOL 7
#define PIN_HEAT 5

TKRelay Cool(PIN_COOL);
TKRelay Heat(PIN_HEAT);
YafaDebounce CO2(PIN_CO2,20); // TODO - tweak MaxCnt

void setup() {
  pinMode(PIN_TEMP, INPUT);
  pinMode(PIN_COOL, OUTPUT);
  pinMode(PIN_HEAT, OUTPUT);
  
  CO2.init();
  Bridge.begin();
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
  
   delay(200);

}
