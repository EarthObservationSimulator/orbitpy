//
// Created by Gabriel Apaza on 2019-03-10.
//

#ifndef ORBIT_SOURCE_HPP
#define ORBIT_SOURCE_HPP


#include <queue>
#include <string>
#include <mutex>



using namespace std;



extern mutex criticalSection;

//!  Queue holding incoming messages from the GUI
extern queue <string> messagesIN;

//!  Queue holding outgoing messages to the GUI
extern queue <string> messagesOUT;

//!  Boolean telling the socket thread when to close the connection
extern bool closeConnection;





#endif //ORBIT_SOURCE_HPP
