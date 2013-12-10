// Nico Lugil

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
   strncpy(buffer+1,command,COMMAND_LEN);
   strncpy(buffer+1+COMMAND_LEN,value,VALUE_LEN);
   buffer[BUFF_LEN-1]='\0';
   Bridge.put(key_put,buffer);

}


