// Nico Lugil

#pragma once

class settings
{

   public:
      float desiredTemp;

      float delta_cool_ON;  
      float delta_cool_OFF; 
      float delta_heat_ON;  
      float delta_heat_OFF; 

      uint8_t FridgeTimeOff;    // Fridge can not be turned on shorter than this time after turning it off (minutes)

      settings()
      {
         ToDefault();
      }

      void ToDefault()
      {
         desiredTemp=19.5;

         delta_cool_ON=0.25;
         delta_cool_OFF=0.0;
         delta_heat_ON=-0.2;
         delta_heat_OFF=-0.1;

         FridgeTimeOff=10;
      }

};

