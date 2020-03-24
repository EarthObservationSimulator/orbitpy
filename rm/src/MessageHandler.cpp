//
// Created by Gabriel Apaza on 2019-02-11.
//

#include "MessageHandler.hpp"





using namespace std;


MessageHandler::MessageHandler()
{
    //Constructor
}


MessageHandler::MessageHandler(const MessageHandler &orig)
{
    //Copy constructor
}



MessageHandler::~MessageHandler()
{
    //Destructor
}



string MessageHandler::checkMessages()
{
    //Use semaphores to protect shared memory

    //Check messages here and handle accordingly

    //criticalSection.lock();
    //bool isEmpty = messagesIN.empty();
    //criticalSection.unlock();

    //if(isEmpty){return "";}//Return an empty string if there are no messages

    //criticalSection.lock();
    //string toReturn  = messagesIN.front();
    //messagesIN.pop();
    //criticalSection.unlock();

    //return toReturn;

    return "";
}




void MessageHandler::sendMessage(string message)
{

    //criticalSection.lock();
    //messagesOUT.push(message);
    //criticalSection.unlock();
}