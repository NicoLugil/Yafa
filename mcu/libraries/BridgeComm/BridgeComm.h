// author: Nico Lugil
// TODO: some more text here + license. Would appreciate if you mention
// my name if you use this code

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
    void send()
    {
       send(tx_command_buff,tx_value_buff);
    }

    // sets tx_value based on float
    // prec: number of chars behind dec point
    // abs(v) should be <=TX_VAL_MAXABS
    // TODO: handle if not in range
    void set_tx_value(float v, uint8_t prec);

    // sets tx_value based on unsigned int (16bit) or 32bit
    void set_tx_value(unsigned int v);
    void set_tx_value_long(uint32_t v);

  private:
    // I am using the dtostrf function to convert from float --> char array
    // imho this isn't an extremely safe function. For now: put bound on "char before 
    // and after dec point with the 2 consts below, which after conversion should
    // easily fit in the the allowed char array
    // TODO: optimize
    const static uint8_t TX_FLOAT_CONVERT_VAL_MAX_PRECISION=5;   // max #char used behind dec point for float conversion
    const static float TX_FLOAT_CONVERT_VAL_MAXABS=999998;   // max abs(val) for float conversion

  public:
    const static uint8_t COMMAND_LEN=16;  
    const static uint8_t VALUE_LEN=32;

  private:
    const static uint8_t BUFF_LEN=1+COMMAND_LEN+VALUE_LEN+1;  // last +1 is to put the \0 for the put command  

    char buffer[BUFF_LEN];  
    char previous_rx_ID;   // uses A->Z (and 0 for nothing yet)
    char previous_tx_ID;
    char key_get[8];
    char key_put[8];

    const static char filler='#';  // should not appear in real commands

    const static uint8_t REQ_CMD_BUFF_LEN=COMMAND_LEN+1;  // +1 for \0
    const static uint8_t REQ_VAL_BUFF_LEN=VALUE_LEN+1;  // +1 for \0

public:

    char rx_command_buff[REQ_CMD_BUFF_LEN];
    char rx_value_buff[REQ_VAL_BUFF_LEN];
    char rx_ID;

    // these can be used to send
    char tx_command_buff[COMMAND_LEN];
    char tx_value_buff[VALUE_LEN];
  
};

