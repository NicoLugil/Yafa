/* vim: set filetype=cpp: */

// Nico Lugil

#include <Console.h>
#include "TinkerKit.h"
#include "YafaDebounce.h"
#include "BridgeComm.h"
#include "OneWire.h"
#include "DallasTemperature.h"

#define PIN_CO2 2
#define PIN_TEMP 10
#define PIN_COOL 7
#define PIN_HEAT 5

TKRelay Cool(PIN_COOL);
TKRelay Heat(PIN_HEAT);
YafaDebounce CO2(PIN_CO2,20); // TODO - tweak MaxCnt
BridgeComm myBridgeComm;

OneWire ow(PIN_TEMP);
DallasTemperature sensors(&ow);

// arrays to hold device address
DeviceAddress Thermometer;

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

   // locate devices on the bus
   Console.print("Locating devices...");
   sensors.begin();
   Console.print("Found ");
   Console.print(sensors.getDeviceCount(), DEC);
   Console.println(" devices.");
   // report parasite power reqs
   Console.print("Parasitic power is: ");
   if (sensors.isParasitePowerMode()) Console.println("ON");
   else Console.println("OFF");
   // Method 1:
   // search for devices on the bus and assign based on an index.  ideally,
   // you would do this to initially discover addresses on the bus and then 
   // use those addresses and manually assign them (see above) once you know 
   // the devices on your bus (and assuming they don't change).
   if (!sensors.getAddress(Thermometer, 0)) Console.println("Unable to find address for Device 0"); 
   // show the addresses we found on the bus
   Console.print("Device 0 Address: ");
   printAddress(Thermometer);
   Console.println();


   uint8_t res=sensors.getResolution(Thermometer);
   Console.print("Device 0 Resolution: ");
   Console.print(res, DEC); 
   Console.println();
   if(res!=12)
   {
      // set the resolution to 12 bit (Each Dallas/Maxim device is capable of several different resolutions)
      // actually wanted less, but it did not seem to retain after power down?? TODO
      sensors.setResolution(Thermometer, 12);
      Console.print("Changed Device 0 Resolution to: ");
      uint8_t res=sensors.getResolution(Thermometer);
      Console.print(res, DEC); 
      Console.println();
   }
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
      if(strcmp(myBridgeComm.rx_command_buff,"Temp?")==0)
      {
         sensors.requestTemperatures();
         float temp = sensors.getTempCByIndex(0);
         //alternative: float temp = sensors.getTempC(Thermometer);
         Console.println(temp);
         strncpy(myBridgeComm.tx_command_buff,"Temp=",myBridgeComm.COMMAND_LEN);
         myBridgeComm.set_tx_value(temp,2);
      }
      myBridgeComm.send();
   }



   delay(100);

}


// function to print a device address
void printAddress(DeviceAddress deviceAddress)
{
   for (uint8_t i = 0; i < 8; i++)
   {
      if (deviceAddress[i] < 16) Console.print("0");
      Console.print(deviceAddress[i], HEX);
   }
}


