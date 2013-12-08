// simple integrating YafaDebounce - not using absolute time, results depend on how fast you call this method
// Based on: http://www.kennethkuhn.com/electronics/debounce.c
//
// Nico Lugil

#pragma once

#include <Arduino.h>

class YafaDebounce
{

   public:
      YafaDebounce(uint8_t pin ,uint32_t _MaxCnt);

      void init();

      // these 3 methods sample the input
      // get_val returns debounced value
      // is_rising and is_falling return true if there
      // was a debounced rising or falling edge
      bool get_val();
      bool is_rising();
      bool is_falling();

   private:

      uint32_t integrator;
      uint32_t MaxCnt;
      bool output;  
      uint8_t pin;

      bool r_rise;
      bool r_fall;

};


