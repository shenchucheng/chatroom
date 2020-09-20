#!/usr/bin/env python3
# -*- coding:UTF-8 -*-
# AUTHOR: Chucheng Shen
# DATE: 2020/09/20 Sun

# DESCRIPTION: Chatroom Client

import sys
sys.path.append('gen-py')

import socket, time

from threading import Thread

from chatroom.ttypes import ChatroomOperationError, RMMsg
from chatroom.Chatroom import Client


from user.ttypes import User


from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


from server import timestamp

Client.getMsg
class ChatroomClient(Client):
    def __init__(self, iport, oport=None):
        super().__init__(iport, oprot=oport)
        self.__user = User()
        self.__rooms = None
    
    def getUser(self, ip):
        self.__user = super().getUser(ip=ip)
        return self.__user

    def sendRMMsg(self, content, chatroomId=2147483647):
        msg = RMMsg(
            content = content,
            timestamp = timestamp(),
            userId = self.__user.userId,
            chatroomId = chatroomId
        )
        return super().sendRMMsg(msg)

    def getMsg(self):
        return super().getMsg(self.__user.userId)


def timeFormat(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

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
client.getUser(ip)
# Close!
# transport.close()

def test():
    while 1:
        msgs = client.getMsg()
        if not msgs.room:
            time.sleep(1)
            # print(msgs)
            continue
        for i in msgs.room:
            print('User', i.userId,  timeFormat(i.timestamp))
            print(i.content)
        
Thread(target=test).start()
while 1:
    try:
        inp = input('1：.exit + 回车 退出；2：其他任意内容回车发送')
        if inp == '':
            continue
        elif inp == '.exit' :
            sys.exit('bye')
        else:
            client.createRoom
            client.sendRMMsg(inp)
    except KeyboardInterrupt:
        break
        

# if __name__ == '__main__':
#     try:
#         main()
#     except Thrift.TException as tx:
#         print('%s' % tx.message)
