// Nico Lugil

#pragma once

#include <Arduino.h>

class BridgeComm
{
  public:
    BridgeComm() 
    {
      previous_rx_ID='0';   // shouldnt be used as real ID
      previous_tx_ID='0';   // not te be used as real ID
      strcpy(key_get,"key_get");
      strcpy(key_put,"key_put");
    }
    
    // starts bridge
    void begin();

#if 0
    // initial 'handshaking' between both sides - to be done before check_for_command ..
    // no timeout for now
    void setup_communication();
#endif

    // checks for new command from CPU: if so, will return true.
    // new command and value will be in rx_command_buff and rx_value_buff
    //     both are guaranteed to be \0 terminated
    // message ID will be in rx_ID
    bool check_for_command();

    // sends command and value to CPU
    // command and value should max be COMMAND_LEN and VALUE_LEN
    // they do not need to be \0 terminated
    void send(char *command, char *value);

    const static uint8_t COMMAND_LEN=16;  
    const static uint8_t VALUE_LEN=32;

  private:
    const static uint8_t BUFF_LEN=1+COMMAND_LEN+VALUE_LEN+1;  // last +1 is to put the \0 for the put command  

    char buffer[BUFF_LEN];  
    char previous_rx_ID;   // uses A->Z (and 0 for nothing yet)
    char previous_tx_ID;
    char key_get[8];
    char key_put[8];

    const static uint8_t REQ_CMD_BUFF_LEN=COMMAND_LEN+1;  // +1 for \0
    const static uint8_t REQ_VAL_BUFF_LEN=VALUE_LEN+1;  // +1 for \0

public:

    char rx_command_buff[REQ_CMD_BUFF_LEN];
    char rx_value_buff[REQ_VAL_BUFF_LEN];
    char rx_ID;
  
};

