// Nico Lugil

#pragma once

class settings
{

   public:
      float desiredTemp;
      float HystOneSide_ON;   // cooling ON when temp > desiredTemp+HystOneSide_ON
                              // heating ON when temp < desiredTemp-HystOneSide_ON
      float HystOneSide_OFF;  // cooling OFF when temp < desiredTemp-HystOneSide_OFF
                              // heating OFF when temp > desiredTemp+HystOneSide_OFF
      uint8_t FridgeTimeOff;    // Fridge can not be turned on shorter than this time after turning it off (minutes)

      settings()
      {
         ToDefault();
      }

      void ToDefault()
      {
         desiredTemp=19.5;
         HystOneSide_ON=0.13;
         HystOneSide_OFF=0.13;
         FridgeTimeOff=10;
      }

};

