/* vim: set filetype=cpp: */

// Nico Lugil

#include <Console.h>
#include "TinkerKit.h"
#include "YafaDebounce.h"
#include "BridgeComm.h"
#include "OneWire.h"
#include "DallasTemperature.h"
#include "settings.h"

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
settings mySettings;

// arrays to hold device address
DeviceAddress Thermometer;

// todo make class or so
unsigned long last_tmp_meas_time;
float temp_measured;
float get_temp()
{
   sensors.requestTemperatures();
   temp_measured = sensors.getTempCByIndex(0);
   last_tmp_meas_time=millis();
   Console.print("temp measured=");
   Console.println(temp_measured);
   return temp_measured;
}

// co2 stuff
int pulses_between_checks;  // only 16 bit, ok?

// heat/cool stuff
bool heat_on;
bool cool_on;
unsigned long last_time_cool_on;
void set_heat(bool v)
{
   heat_on=v;
   if(v)
   {
      Heat.on();
   }
   else
   {
      Heat.off();
   }
}

void set_cool(bool v)
{
   cool_on=v;
   if(v)
   {
      Cool.on();
   }
   else
   {
      Cool.off();
   }
}
uint32_t n_cool_on;
uint32_t n_heat_on;
uint32_t n_total;

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

   // init temp
   get_temp();

   // init c02
   pulses_between_checks=0;

   // init heat/cool
   set_heat(false);
   set_cool(false);
   last_time_cool_on=millis();  // assume cooler was on
   n_cool_on=0;
   n_heat_on=0;
   n_total=0;
}

void loop() 
{

   // do all the local stuff
   // - meas tmp
   // - control heat/cool
   // - meas CO2 production
   //
   // temp/ do every 30 sec
   unsigned int long now = millis();
   if((now-last_tmp_meas_time)>10000)
   {
      get_temp();

      // TODO: avoid switch to same situation
      if(temp_measured>(mySettings.desiredTemp+mySettings.HystOneSide))
      {
         if( (now-last_time_cool_on) > 1000*mySettings.FridgeTimeOff)
         {
            set_cool(true);  // TODO: delay compressor
         }
         set_heat(false);
      }
      else if(temp_measured<(mySettings.desiredTemp-mySettings.HystOneSide)) 
      {
         set_cool(false);
         set_heat(true);
      }
      else
      {
         set_cool(false);
         set_heat(false);
      }
      if(cool_on)
      {
         n_cool_on++;
      }
      if(heat_on)
      {
         n_heat_on++;
      }
      n_total++;
      Console.print(n_cool_on);
      Console.print(" ");
      Console.print(n_heat_on);
      Console.print(" ");
      Console.println(n_total);
   }
   if(cool_on)
   {
      last_time_cool_on=now;
   }

   if(CO2.is_falling())
   {
      Console.println("Fall");
   }
   if(CO2.is_rising())
   {
      Console.print("Rise: total cnts between checks=");
      pulses_between_checks++;
      Console.println(pulses_between_checks);
   }

   if(myBridgeComm.check_for_command())
   {
      Console.println(myBridgeComm.rx_command_buff);
      Console.println(myBridgeComm.rx_value_buff);
      if(strcmp(myBridgeComm.rx_command_buff,"Temp?")==0)
      {
         get_temp();
         Console.println("Temp request");
         strncpy(myBridgeComm.tx_command_buff,"Temp=",myBridgeComm.COMMAND_LEN);
         myBridgeComm.set_tx_value(temp_measured,2);
         myBridgeComm.send();
      }
      if(strcmp(myBridgeComm.rx_command_buff,"CO2?")==0)
      {
         Console.println("CO2 request");
         strncpy(myBridgeComm.tx_command_buff,"CO2=",myBridgeComm.COMMAND_LEN);
         myBridgeComm.set_tx_value(pulses_between_checks);
         pulses_between_checks=0;
         myBridgeComm.send();
      }
      if(strcmp(myBridgeComm.rx_command_buff,"Act?")==0)
      {
         Console.println("actuators request");
         strncpy(myBridgeComm.tx_command_buff,"ActCool=",myBridgeComm.COMMAND_LEN);
         // TODO: better concat of the 3 values - for now assume never above 1024
         // and hence 3 values fitting in 32bit
         uint32_t myVal=n_cool_on+1024lu*n_heat_on+1024lu*1024lu*n_total;
         Console.print("myVal=");
         Console.println(myVal);
         myBridgeComm.set_tx_value_long(myVal);
         n_cool_on=0;
         n_heat_on=0;
         n_total=0;
         myBridgeComm.send();
      }

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


