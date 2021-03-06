/* vim: set filetype=cpp: */

// Nico Lugil

#include <Console.h>
#include "TinkerKit.h"
#include "YafaDebounce.h"
#include "BridgeComm.h"
#include "OneWire.h"
#include "DallasTemperature.h"
#include "settings.h"

#define PIN_CO2 10
#define PIN_TEMP 12
#define PIN_COOL 9
#define PIN_HEAT 8

#define ENABLE_CONSOLEPRINT

TKRelay Cool(PIN_COOL);
TKRelay Heat(PIN_HEAT);
YafaDebounce CO2(PIN_CO2,20); // TODO - tweak MaxCnt
BridgeComm myBridgeComm;

OneWire ow(PIN_TEMP);
DallasTemperature sensors(&ow);
settings mySettings;

// arrays to hold device address
DeviceAddress Thermometer;

// co2 stuff
int pulses_between_checks;  // only 16 bit, ok?

// regulate?
bool regulate=false;

// heat/cool stuff
bool heat_on;
bool cool_on;
unsigned long last_time_cool_on;

void set_heat(bool v)
{
   v=v&&regulate;
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
   v=v&&regulate;
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
float t_max, t_min;

// Console extension
// TODO: make class
bool Console_on;

void ConsPrint(const char d[])
{
#ifdef ENABLE_CONSOLEPRINT
   if(Console_on)
   {
      Console.print(d);
   }
#endif
}
void ConsPrint(int d)
{
#ifdef ENABLE_CONSOLEPRINT
   if(Console_on)
   {
      Console.print(d);
   }
#endif
}
void ConsPrint(int d, int f)
{
#ifdef ENABLE_CONSOLEPRINT
   if(Console_on)
   {
      Console.print(d, f);
   }
#endif
}

// todo make class or so
unsigned long last_tmp_meas_time;
float temp_measured;
float get_temp()
{
   // TODO: if weird, or sensor not found --> regulate=false
   unsigned long s1;
   s1=millis();
   sensors.requestTemperatures();
   float tmp = sensors.getTempCByIndex(0);
   if(tmp>-5 && tmp<45)
   {
      temp_measured = tmp;
      last_tmp_meas_time=millis();
      ConsPrint("temp measured=");
      ConsPrint(temp_measured);
      ConsPrint(" took ");
      ConsPrint(last_tmp_meas_time-s1);
      ConsPrint(" millis\n");
   }
   else
   {
      // TODO something here
      ConsPrint("Sensor returned weird temp, ignoring\n");
   }
   return temp_measured;
}

void setup() {

   delay(4000+2000); // pass uboot

   pinMode(PIN_TEMP, INPUT);
   pinMode(PIN_COOL, OUTPUT);
   pinMode(PIN_HEAT, OUTPUT);
   pinMode(13,OUTPUT);

   CO2.init();

   myBridgeComm.begin();
   while(!myBridgeComm.check_for_command())
   {}
   if(strcmp(myBridgeComm.rx_command_buff,"Init?")==0)
   {
      strncpy(myBridgeComm.tx_command_buff,"Init!",myBridgeComm.COMMAND_LEN);
      myBridgeComm.set_tx_value(1234);
   }
   else
   {
      strncpy(myBridgeComm.tx_command_buff,"UnExp!",myBridgeComm.COMMAND_LEN);
      strncpy(myBridgeComm.tx_value_buff,myBridgeComm.rx_command_buff,myBridgeComm.VALUE_LEN);
   }
   myBridgeComm.send();

   Console_on=false;
   unsigned int long t1 = millis();
   while(!Console && ((millis()-t1<10000))) { }
   if(Console)
   {
      Console_on=true;
   }
   ConsPrint("Console started\n");

   // locate devices on the bus
   ConsPrint("Locating devices...");
   sensors.begin();
   ConsPrint("Found ");
   ConsPrint(sensors.getDeviceCount(), DEC);
   ConsPrint(" devices.\n");
   // report parasite power reqs
   ConsPrint("Parasitic power is: ");
   if (sensors.isParasitePowerMode()) ConsPrint("ON\n");
   else ConsPrint("OFF\n");
   // Method 1:
   // search for devices on the bus and assign based on an index.  ideally,
   // you would do this to initially discover addresses on the bus and then 
   // use those addresses and manually assign them (see above) once you know 
   // the devices on your bus (and assuming they don't change).
   if (!sensors.getAddress(Thermometer, 0)) 
   { 
      ConsPrint("Unable to find address for Device 0\n"); 
   }
   else
   {
      regulate=true;
      // show the addresses we found on the bus
      ConsPrint("Device 0 Address: ");
      printAddress(Thermometer);
      ConsPrint("\n");

      uint8_t res=sensors.getResolution(Thermometer);
      ConsPrint("Device 0 Resolution: ");
      ConsPrint(res, DEC); 
      ConsPrint("\n");
      if(res!=12)
      {
         // set the resolution to 12 bit (Each Dallas/Maxim device is capable of several different resolutions)
         // actually wanted less, but it did not seem to retain after power down?? TODO
         sensors.setResolution(Thermometer, 12);
         ConsPrint("Changed Device 0 Resolution to: ");
         uint8_t res=sensors.getResolution(Thermometer);
         ConsPrint(res, DEC); 
         ConsPrint("\n");
      }
   }

   while(!myBridgeComm.check_for_command())
   {}
   if(strcmp(myBridgeComm.rx_command_buff,"TSensor?")==0)
   {
      strncpy(myBridgeComm.tx_command_buff,"TSensor!",myBridgeComm.COMMAND_LEN);
      if(regulate)
      {
         for(unsigned int i=0;i<8;i++)
         {
            snprintf(myBridgeComm.tx_value_buff+2*i,myBridgeComm.VALUE_LEN-2*i,"%.2X",Thermometer[i]);
         }
      }
      else
      {
         strncpy(myBridgeComm.tx_value_buff,"ERROR",myBridgeComm.VALUE_LEN);
      }
   }
   else
   {
      strncpy(myBridgeComm.tx_command_buff,"UnExp!",myBridgeComm.COMMAND_LEN);
      strncpy(myBridgeComm.tx_value_buff,myBridgeComm.rx_command_buff,myBridgeComm.VALUE_LEN);
   }
   myBridgeComm.send();

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
   t_max=temp_measured;
   t_min=temp_measured;

   // get settings from CPU
   uint8_t set=0;
   while(set!=31)  // TODO: timeout
   {
      if(myBridgeComm.check_for_command())
      {
         if(strcmp(myBridgeComm.rx_command_buff,"setTemp=")==0)
         {
            mySettings.desiredTemp=myBridgeComm.get_rx_value_as_float();
            strncpy(myBridgeComm.tx_command_buff,"setTemp=",myBridgeComm.COMMAND_LEN);
            myBridgeComm.set_tx_value(mySettings.desiredTemp);
            myBridgeComm.send();
            set=set|1;
         }
         else if(strcmp(myBridgeComm.rx_command_buff,"setdHeatOn=")==0)
         {
            mySettings.delta_heat_ON=myBridgeComm.get_rx_value_as_float();
            strncpy(myBridgeComm.tx_command_buff,"setdHeatOn=",myBridgeComm.COMMAND_LEN);
            myBridgeComm.set_tx_value(mySettings.delta_heat_ON);
            myBridgeComm.send();
            set=set|2;
         }
         else if(strcmp(myBridgeComm.rx_command_buff,"setdHeatOff=")==0)
         {
            mySettings.delta_heat_OFF=myBridgeComm.get_rx_value_as_float();
            strncpy(myBridgeComm.tx_command_buff,"setdHeatOff=",myBridgeComm.COMMAND_LEN);
            myBridgeComm.set_tx_value(mySettings.delta_heat_OFF);
            myBridgeComm.send();
            set=set|4;
         }
         else if(strcmp(myBridgeComm.rx_command_buff,"setdCoolOn=")==0)
         {
            mySettings.delta_cool_ON=myBridgeComm.get_rx_value_as_float();
            strncpy(myBridgeComm.tx_command_buff,"setdCoolOn=",myBridgeComm.COMMAND_LEN);
            myBridgeComm.set_tx_value(mySettings.delta_cool_ON);
            myBridgeComm.send();
            set=set|8;
         }
         else if(strcmp(myBridgeComm.rx_command_buff,"setdCoolOff=")==0)
         {
            mySettings.delta_cool_OFF=myBridgeComm.get_rx_value_as_float();
            strncpy(myBridgeComm.tx_command_buff,"setdCoolOff=",myBridgeComm.COMMAND_LEN);
            myBridgeComm.set_tx_value(mySettings.delta_cool_OFF);
            myBridgeComm.send();
            set=set|16;
         }

      }
      delay(100);
   }
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
      digitalWrite(13,HIGH);
      get_temp();
      if(temp_measured>t_max)
      {
         t_max=temp_measured;
      }
      if(temp_measured<t_min)
      {
         t_min=temp_measured;
      }
      digitalWrite(13,LOW);

      // TODO: avoid switch to same situation
      // TODO: code below wont work for all settings (!cool && !heat)

      if(!cool_on && !heat_on)
      {
         if(temp_measured>(mySettings.desiredTemp+mySettings.delta_cool_ON))
         {
            if( (now-last_time_cool_on) > 60*1000*mySettings.FridgeTimeOff)
            {
               set_cool(true);  
            }
            set_heat(false); // remove ??
         }
         else if(temp_measured<(mySettings.desiredTemp+mySettings.delta_heat_ON)) 
         {
            set_cool(false); // remove ??
            set_heat(true);
         }
      }
      else if(cool_on)
      {
         if(temp_measured<=mySettings.desiredTemp+mySettings.delta_cool_OFF) 
         {
            set_cool(false);
         }
         set_heat(false);  // remove ??
      }
      else
      {
         // heat && !cool
         if(temp_measured>=mySettings.desiredTemp+mySettings.delta_heat_OFF) 
         {
            set_heat(false); 
         }
         set_cool(false); // remove ??
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
      ConsPrint(n_cool_on);
      ConsPrint(" ");
      ConsPrint(n_heat_on);
      ConsPrint(" ");
      ConsPrint(n_total);
      ConsPrint("\n");
   }
   if(cool_on)
   {
      last_time_cool_on=now;
   }

   if(CO2.is_falling())
   {
      ConsPrint("Fall\n");
   }
   if(CO2.is_rising())
   {
      ConsPrint("Rise: total cnts between checks=");
      pulses_between_checks++;
      ConsPrint(pulses_between_checks);
      ConsPrint("\n");
   }

   if(myBridgeComm.check_for_command())
   {
      ConsPrint(myBridgeComm.rx_command_buff);
      ConsPrint("\n");
      ConsPrint(myBridgeComm.rx_value_buff);
      ConsPrint("\n");
      if(strcmp(myBridgeComm.rx_command_buff,"Temp?")==0)
      {
         get_temp();
         ConsPrint("Temp request\n");
         strncpy(myBridgeComm.tx_command_buff,"Temp=",myBridgeComm.COMMAND_LEN);
         myBridgeComm.set_tx_value(temp_measured,2);
         myBridgeComm.send();
      }
      if(strcmp(myBridgeComm.rx_command_buff,"Tmax?")==0)
      {
         get_temp();
         ConsPrint("Temp max request\n");
         strncpy(myBridgeComm.tx_command_buff,"Tmax=",myBridgeComm.COMMAND_LEN);
         myBridgeComm.set_tx_value(t_max,2);
         myBridgeComm.send();
         t_max=temp_measured;
      }
      if(strcmp(myBridgeComm.rx_command_buff,"Tmin?")==0)
      {
         get_temp();
         ConsPrint("Temp min request\n");
         strncpy(myBridgeComm.tx_command_buff,"Tmin=",myBridgeComm.COMMAND_LEN);
         myBridgeComm.set_tx_value(t_min,2);
         myBridgeComm.send();
         t_min=temp_measured;
      }
      else if(strcmp(myBridgeComm.rx_command_buff,"CO2?")==0)
      {
         ConsPrint("CO2 request\n");
         strncpy(myBridgeComm.tx_command_buff,"CO2=",myBridgeComm.COMMAND_LEN);
         myBridgeComm.set_tx_value(pulses_between_checks);
         pulses_between_checks=0;
         myBridgeComm.send();
      }
      else if(strcmp(myBridgeComm.rx_command_buff,"setTemp=")==0)
      {
         mySettings.desiredTemp=myBridgeComm.get_rx_value_as_float();
         ConsPrint(mySettings.desiredTemp);
         ConsPrint("\n");
         // acknowledge with the parsed temp (approx requested one)
         strncpy(myBridgeComm.tx_command_buff,"setTemp=",myBridgeComm.COMMAND_LEN);
         myBridgeComm.set_tx_value(mySettings.desiredTemp);
         myBridgeComm.send();
      }
      else if(strcmp(myBridgeComm.rx_command_buff,"setdHeatOn=")==0)
      {
         mySettings.delta_heat_ON=myBridgeComm.get_rx_value_as_float();
         strncpy(myBridgeComm.tx_command_buff,"setdHeatOn=",myBridgeComm.COMMAND_LEN);
         myBridgeComm.set_tx_value(mySettings.delta_heat_ON);
         myBridgeComm.send();
      }
      else if(strcmp(myBridgeComm.rx_command_buff,"setdHeatOff=")==0)
      {
         mySettings.delta_heat_OFF=myBridgeComm.get_rx_value_as_float();
         strncpy(myBridgeComm.tx_command_buff,"setdHeatOff=",myBridgeComm.COMMAND_LEN);
         myBridgeComm.set_tx_value(mySettings.delta_heat_OFF);
         myBridgeComm.send();
      }
      else if(strcmp(myBridgeComm.rx_command_buff,"setdCoolOn=")==0)
      {
         mySettings.delta_cool_ON=myBridgeComm.get_rx_value_as_float();
         strncpy(myBridgeComm.tx_command_buff,"setdCoolOn=",myBridgeComm.COMMAND_LEN);
         myBridgeComm.set_tx_value(mySettings.delta_cool_ON);
         myBridgeComm.send();
      }
      else if(strcmp(myBridgeComm.rx_command_buff,"setdCoolOff=")==0)
      {
         mySettings.delta_cool_OFF=myBridgeComm.get_rx_value_as_float();
         strncpy(myBridgeComm.tx_command_buff,"setdCoolOff=",myBridgeComm.COMMAND_LEN);
         myBridgeComm.set_tx_value(mySettings.delta_cool_OFF);
         myBridgeComm.send();
      }
      else if(strcmp(myBridgeComm.rx_command_buff,"Act?")==0)
      {
         ConsPrint("actuators request\n");
         strncpy(myBridgeComm.tx_command_buff,"ActCool=",myBridgeComm.COMMAND_LEN);
         // TODO: better concat of the 3 values - for now assume never above 1024
         // and hence 3 values fitting in 32bit
         uint32_t myVal=n_cool_on+1024lu*n_heat_on+1024lu*1024lu*n_total;
         ConsPrint("myVal=");
         ConsPrint(myVal);
         ConsPrint("\n");
         myBridgeComm.set_tx_value_long(myVal);
         n_cool_on=0;
         n_heat_on=0;
         n_total=0;
         myBridgeComm.send();
      }
      else
      {
         // TODO: handle it
      }

   }

   delay(100);

}


// function to print a device address
void printAddress(DeviceAddress deviceAddress)
{
   for (uint8_t i = 0; i < 8; i++)
   {
      if (deviceAddress[i] < 16) ConsPrint("0");
      ConsPrint(deviceAddress[i], HEX);
   }
}


