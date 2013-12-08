//#include <string.h>

#include <Arduino.h>
#pragma once

class BridgeComm
{
  public:
    BridgeComm() 
    {
      previous_msg_ID='0';
      strcpy(key_get,"key_get");
      strcpy(key_put,"key_put");
    }
    
    // starts bridge
    void begin();

    // initial 'handshaking' between both sides - to be done before check_for_command ..
    // no timeout for now
    void setup_communication();

    bool check_for_command();

  private:
    const static uint8_t COMMAND_LEN=16;  
    const static uint8_t VALUE_LEN=32;
    const static uint8_t BUFF_LEN=1+COMMAND_LEN+VALUE_LEN;    

    char buffer[BUFF_LEN];  
    char previous_msg_ID;   // uses A->Z (and 0 for nothing yet)
    char key_get[8];
    char key_put[8];

    const static uint8_t REQ_CMD_BUFF_LEN=COMMAND_LEN+1;  // +1 for \0
    const static uint8_t REQ_VAL_BUFF_LEN=VALUE_LEN+1;  // +1 for \0

public:

    char command_buff[REQ_CMD_BUFF_LEN];
    char value_buff[REQ_VAL_BUFF_LEN];
  
};

