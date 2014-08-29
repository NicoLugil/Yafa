// author: Nico Lugil
// TODO: some more text here + license. Would appreciate if you mention
// my name if you use this code

#include "BridgeComm.h"
#include <Bridge.h>

void BridgeComm::begin()
{
   Bridge.begin();
}

bool BridgeComm::check_for_command()
{
   unsigned int r;
   r=Bridge.get(key_get,buffer,(unsigned int)BUFF_LEN-1);
   if(r==BridgeClass::TRANSFER_TIMEOUT || r==0)
   {                                  
      return false;
   }
   if(buffer[0]!=previous_rx_ID)
   {
      for(uint8_t i=1;i<BUFF_LEN;i++)
      {
         if(buffer[i]==filler)
         {
            buffer[i]='\0';
         }
      }
      //Console.print("new msg, length of get is ");
      //Console.println(r);
      previous_rx_ID=buffer[0];
      rx_ID=buffer[0];
      strncpy(rx_command_buff,buffer+1,COMMAND_LEN);
      rx_command_buff[COMMAND_LEN]='\0';
      strncpy(rx_value_buff,buffer+1+COMMAND_LEN,VALUE_LEN);
      rx_value_buff[VALUE_LEN]='\0';
      return true;
   }
   //Console.println("No new msg");
   return false;
}

void BridgeComm::send(char *command, char *value)
{
   char ID=previous_tx_ID+1;
   if(ID<'A' || ID>'Z')
   {
      ID='A';
   }
   buffer[0]=ID;
   previous_tx_ID=ID;
   // strncpy(buffer+1,command,COMMAND_LEN);  --> would have been ideal, but zero padds with \0
   // in CPU, means the get stops at that first \0  :-(
   // think this is not how bridge should work
   // So for now, put fillers instead
   strncpy(buffer+1,command,COMMAND_LEN);  
   strncpy(buffer+1+COMMAND_LEN,value,VALUE_LEN);
   for(uint8_t i=1; i<1+COMMAND_LEN+VALUE_LEN; i++)
   {
      if(buffer[i]=='\0')
      {
         buffer[i]=filler;
      }
   }
   buffer[BUFF_LEN-1]='\0';
   Bridge.put(key_put,buffer);
}

void BridgeComm::set_tx_value(float v, uint8_t prec)
{

   if(fabs(v)>TX_FLOAT_CONVERT_VAL_MAXABS)
   {
      // TODO: handle this better
      strncpy(tx_value_buff,"CONV_RNG_EXC",VALUE_LEN);
   }
   if(prec>TX_FLOAT_CONVERT_VAL_MAX_PRECISION)
   {
      // TODO: handle this better
      prec = TX_FLOAT_CONVERT_VAL_MAX_PRECISION;
   }

   // +2 for - and ., extra 2 for maybe /0, ???
   // we have space enough with 32 now...
   dtostrf(v,2+prec+2,prec,tx_value_buff);
}

void BridgeComm::set_tx_value(unsigned int v)
{
   // TODO: check if fits in string
   //Console.println(v);
   itoa(v,tx_value_buff,10);
   //Console.println(tx_value_buff);
}
void BridgeComm::set_tx_value_long(uint32_t v)
{
   // TODO: check if fits in string
   //Console.println(v);
   ultoa(v,tx_value_buff,10);
   //Console.println(tx_value_buff);
}

float BridgeComm::get_rx_value_as_float()
{
   // TODO: better checking
   float x = atof(rx_value_buff);
   return x;
}

