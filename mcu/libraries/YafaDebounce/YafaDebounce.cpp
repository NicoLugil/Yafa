#include "YafaDebounce.h"

YafaDebounce::YafaDebounce(uint8_t _pin ,uint32_t _MaxCnt) : pin(_pin), MaxCnt(_MaxCnt)
{
}

void YafaDebounce::init()
{
   pinMode(pin, INPUT);
   integrator=MaxCnt/2;

   // try to get a stable value
   // TODO: make this more robust
   output=false;
   for(uint64_t i=0;i<2*(uint64_t)MaxCnt;i++)
   {
      get_val();
   }

   r_rise=false;
   r_fall=false;

}

bool YafaDebounce::get_val()
{
   // read pin
   uint8_t val = digitalRead(pin);
   if(val==LOW)
   {
      if(integrator>0)
      {
         integrator--;
      }
   }
   else
   {
      if(integrator<MaxCnt)
      {
         integrator++;
      }
   }

   bool prev_output = output;
   if(integrator==0)
   {
      output=false;
   }
   if(integrator>=MaxCnt)
   {
      output=true;
      integrator=MaxCnt; //safety
   }
   if(prev_output && (!output))
   {
      r_fall=true;
   }
   if((!prev_output) && output)
   {
      r_rise=true;
   }

   return output;
}

bool YafaDebounce::is_rising()
{
   get_val();
   if(r_rise)
   {
      r_rise=false;
      return true;
   }

   return false;
}

bool YafaDebounce::is_falling()
{
   get_val();
   if(r_fall)
   {
      r_fall=false;
      return true;
   }

   return false;
}


