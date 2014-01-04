// Nico Lugil

#pragma once

class settings
{

   public:
      float desiredTemp;
      float HystOneSide;   // e.g. cooling on when temp > desiredTemp+HystOneSide
      uint8_t FridgeTimeOff;    // Fridge can not be turned on shorter than this time after turning it off (minutes)

      settings()
      {
         ToDefault();
      }

      void ToDefault()
      {
         desiredTemp=19.5;
         HystOneSide=0.25;
         FridgeTimeOff=10;
      }

};

