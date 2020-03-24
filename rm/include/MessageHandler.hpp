//
// Created by Gabriel Apaza on 2019-02-11.
//

#ifndef ORBIT_MESSAGEHANDLER_HPP
#define ORBIT_MESSAGEHANDLER_HPP


#include <queue>
#include <string>
#include "source.hpp"



using namespace std;



//!  This class handles incoming and outgoing messages to the GUI
/*!
    The Metrics class is capable of computing access history metrics for one or multiple Satellites. <br>
    Both Ground Network and Area of Interest access metrics can be computed

*/
class MessageHandler {
public:


    //!  OrbitSimulator Constructor
    /*!
        Constructor
    */
    MessageHandler();


    //!  MessageHandler Copy Constructor
    /*!
        Copies a MessageHandler object
    */
    MessageHandler(const MessageHandler& orig);


    //!  MessageHandler Destructor
    /*!
        Destroys a MessageHandler object
    */
    virtual ~MessageHandler();


    //!  This functions checks for messages sent by the GUI
    /*!
        The return value alerts the OrbitSimulator what the message was and what to do next
            --If there are no messages in the queue a blank string will be returned
    */
    string checkMessages();


    //!  This functions sends a message to the GUI
    /*!
        The return value alerts the OrbitSimulator what the message was and what to do next
            --If there are no messages in the queue a blank string will be returned
    */
    void sendMessage(string message);













private:



};


#endif //ORBIT_MESSAGEHANDLER_HPP
