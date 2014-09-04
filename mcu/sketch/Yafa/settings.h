// Nico Lugil

#pragma once

class settings
{

   public:
      float desiredTemp;

      float HystOneSide_cool_ON;   // cooling ON when temp > desiredTemp+HystOneSide_cool_ON
      float HystOneSide_cool_OFF;  // cooling OFF when temp < desiredTemp+HystOneSide_cool_OFF
      float HystOneSide_heat_ON;   // heating ON when temp < desiredTemp+HystOneSide_heat_ON
      float HystOneSide_heat_OFF;  // heating OFF when temp > desiredTemp+HystOneSide_heat_OFF

      uint8_t FridgeTimeOff;    // Fridge can not be turned on shorter than this time after turning it off (minutes)

      settings()
      {
         ToDefault();
      }

      void ToDefault()
      {
         desiredTemp=19.5;

         HystOneSide_cool_ON=0.25;
         HystOneSide_cool_OFF=0.0;
         HystOneSide_heat_ON=-0.2;
         HystOneSide_heat_OFF=-0.1;

         FridgeTimeOff=10;
      }

};

