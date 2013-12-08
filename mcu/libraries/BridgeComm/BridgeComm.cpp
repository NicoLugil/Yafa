#include "BridgeComm.h"
#include <Bridge.h>

bool BridgeComm::check_for_command()
{
   unsigned int r;
   r=Bridge.get(key_get,buffer,(unsigned int)BUFF_LEN);
   if(r==BridgeClass::TRANSFER_TIMEOUT)  // --> bug in Bridge.h TODO: comment this in when fixed || r==0)
   {                                     // see http://forum.arduino.cc/index.php?topic=200621.msg1482353#msg1482353
      return false;
   }
   if(buffer[0]!=previous_msg_ID)
   {
       //Console.print("new msg, length of get is ");
       //Console.println(r);
       previous_msg_ID=buffer[0];
       strncpy(command_buff,buffer+1,COMMAND_LEN);
       command_buff[COMMAND_LEN]='\0';
       strncpy(value_buff,buffer+1+COMMAND_LEN,VALUE_LEN);
       value_buff[VALUE_LEN]='\0';
       return true;
   }
   //Console.println("No new msg");
   return false;
}

void BridgeComm::begin()
{
   Bridge.begin();
}
  
void BridgeComm::setup_communication()
{
   // this will look for cmd==start_link with value==0
   // next does a put of ack_start_link_0 (other side waits for this)
   // then waits for cmd==start_link with value==1 
   // next does a put of ack_start_link_1 (other side waits for this)
   
   


}
 
