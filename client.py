#!/usr/bin/env python3
# -*- coding:UTF-8 -*-
# AUTHOR: Chucheng Shen
# DATE: 2020/09/20 Sun

# DESCRIPTION: Chatroom Client

import sys
sys.path.append('gen-py')

import socket

from chatroom.ttypes import ChatroomOperationError, RMMsg
from chatroom.Chatroom import Client


from user.ttypes import User


from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


from server import timestamp

# Client.sendRMMsg
class ChatroomClient(Client):
    def __init__(self, iport, oport=None):
        super().__init__(iport, oprot=oport)
        self.__user = User()
        self.__rooms = None
    
    def getUser(self, ip):
        self.__user = super().getUser(ip=ip)
        return self.__user

    def sendRMMsg(self, content, chatroomId):
        msg = RMMsg(
            content = content,
            timestamp = timestamp(),
            userId = self.__user.userId,
            chatroomId = chatroomId
        )
        return super().sendRMMsg(msg)




# Make socket
transport = TSocket.TSocket('localhost', 9090)

# Buffering is critical. Raw sockets are very slow
transport = TTransport.TBufferedTransport(transport)

# Wrap in a protocol
protocol = TBinaryProtocol.TBinaryProtocol(transport)

# Create a client to use the protocol encoder
client = ChatroomClient(protocol)
ip = socket.gethostbyname(socket.gethostname())
# Connect!
transport.open()
# Close!
# transport.close()


# if __name__ == '__main__':
#     try:
#         main()
#     except Thrift.TException as tx:
#         print('%s' % tx.message)
