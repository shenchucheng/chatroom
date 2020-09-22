#!/usr/bin/env python3
# -*- coding:UTF-8 -*-
# AUTHOR: Chucheng Shen
# DATE: 2020/09/19 Sat

# DESCRIPTION: Chatroom Server


import sys
sys.path.append('gen-py')

import logging

from time import time
from copy import copy
from typing import List

from chatroom import Chatroom
from chatroom.ttypes import ChatroomOperationError
from chatroom.ttypes import UniMsg, Msg, RMMsg
from chatroom.ttypes import Room, RoomInfo

from user.ttypes import UserOperationError, User, UserInfo
from user.UserService import getUser_args, getUser_result, TMessageType, TApplicationException

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.protocol.THeaderProtocol import THeaderProtocolFactory
from thrift.Thrift import TType

logger = logging.getLogger('chatroom')
logger.level = logging.DEBUG

def timestamp():
    return round(time())

class ChatroomHandler(Chatroom.Iface):
    def __init__(self):
        self.__lastUserId = 0
        self.__lastRoomId = 1 << 31
        self.__lastMsgId = 0
        self.__lastRMMsgId = 1 << 63
        self.__users = {}
        self.__rooms = {}
        self.__roomLastMsgTime = {}
        self.__userMsgTime = {}
        self.__userLastRMMsgTime = {}
        self.superUser = User(
            userId = self.__lastUserId,
            username = '系统管理员',
            userInfo = UserInfo(
                creatTime = timestamp(),
                introduce = '系统管理员'
            )
        )
        self.globalRoom = Room(
            roomId = self.nextRoomId,
            roomName =  '世界广场',
            roomOwer = self.superUser.userId,
            members = set(),
            roomInfo = RoomInfo(
                creatTime = timestamp(),
                introduce = '这里是属于所有人的广场'
            ),
            msgs = []
        )
        self.globalRoom.members.add(self.superUser.userId)
        self.__rooms[self.globalRoom.roomId] = self.globalRoom
        self.__saveRMMsg(self.genWelcomeMsg(self.globalRoom))

    @property
    def nextUserId(self) -> int:
        self.__lastUserId += 1
        logger.debug('User lastid is {}'.format(self.__lastUserId))
        return self.__lastUserId
    
    @property
    def nextRoomId(self) -> int:
        self.__lastRoomId -= 1
        logger.debug('Chatroom lastid is {}'.format(self.__lastRoomId))
        return self.__lastRoomId

    @property
    def nextMsgId(self) -> int:
        self.__lastMsgId += 1
        logger.debug('Msg lastid is {}'.format(self.__lastMsgId))
        return self.__lastMsgId

    @property
    def nextRMMsgId(self) -> int:
        self.__lastRMMsgId -= 1
        logger.debug('Chatroom msg lastid is {}'.format(self.__lastRMMsgId))
        return self.__lastRMMsgId

    def __saveUser(self, user: User):
        """持久化保存User

        Args:
            user (User): 新建用户
        """
        userId = user.userId
        self.__users[userId] = user
        self.globalRoom.members.add(userId)

    def __saveMsg(self, msg: Msg) -> bool:
        pass

    def __saveRMMsg(self, msg: RMMsg) -> bool:
        roomId = msg.chatroomId
        room = self.__querryRoom(roomId)
        if room and msg.userId in room.members:
            msg.saveTime = timestamp()
            room.msgs.append(msg)
            self.__roomLastMsgTime[msg.chatroomId] = msg.saveTime
            logger.debug('Chatroom {} recieve a msg {} from {}'.format(roomId, msg.content, msg.clientInfo))
            return True
        logger.warning('Add mesage error')
        print(msg)
        return False
            
    def __querryUser(self, userId: int) -> User:
        return self.__users.get(userId)

    def __querryRoom(self, roomId: int) -> Room:
        return self.__rooms.get(roomId)

    def __querryUserRooms(self, userId: int) -> List:
        # 待补充 先返回世界广场
        rooms = []
        for roomId, room in self.__rooms.items():
            if userId in room.members:
                rooms.append(roomId)
        return rooms
    
    def __querryUserMsg(self, userId, t) -> List:
        pass

    def __querryMsg(self, userId) -> UniMsg:
        msg = UniMsg()
        try:
            t1, t2 = self.__userMsgTime[userId]
            if t1 == t2:
                msg.user = []
            else:
                msg.user = self.__querryUserMsg(userId, t1)
                t = msg.user[-1].saveTime
                self.__userMsgTime[userId] = (t, t)
        except:
            # 待补充 首次查询消息
            pass

        msg.room = []
        ts = self.__userLastRMMsgTime.get(userId) or {}
        for i in self.__querryUserRooms(userId):
            try:
                t1 = ts.get(i) or 0
                if self.__roomLastMsgTime[i] > t1:
                    msglist = self.__querryRoom(i).msgs
                    k = -1
                    while msglist[k].saveTime > t1:
                        msg.room.append(msglist[k])
                        k -= 1
                    ts[i] = msglist[-1].saveTime
            except IndexError:
                ts[i] = msglist[-1].saveTime
                continue
            except Exception:
                raise Exception
        self.__userLastRMMsgTime[userId] = ts
        return msg
    
    def __saveRoom(self, room):
        self.__rooms[room.roomId] = room
        self.__saveRMMsg(self.genWelcomeMsg(room))

    def genWelcomeMsg(self, room: Room) -> RMMsg:
        return RMMsg(
            content = '欢迎来到{}！'.format(room.roomName),
            timestamp = timestamp(),
            chatroomId = room.roomId,
            userId = room.roomOwer,
            msgId = self.nextRMMsgId,
        )

    def createRoom(self, roomName, roomOwer, members, roomInfo=None):
        print(roomName, roomOwer, members, roomInfo)
        print(members)
        if not members:
            members = set()
        members.add(roomOwer)
        members.add(self.superUser.userId)
        roomId = self.nextRoomId
        room = Room(
            roomId = roomId,
            roomName = roomName,
            members = members,
            roomOwer = roomOwer,
            msgs = []
        )
        self.__saveRoom(room)
        return room

    def getUser(self, ip:str) -> User:
        userId = self.nextUserId
        userInfo = UserInfo(timestamp(), introduce='ip:{}'.format(ip))
        user = User(userId=userId, username='游客'+str(userId), userInfo=userInfo)
        self.__saveUser(user)
        self.globalRoom.members.add(userId)
        logger.debug('User with id {} from {} has added'.format(userId, ip))
        Users.append(user)
        return user

    def sendMsg(self, msg: Msg) -> bool:
        return self.__saveMsg(msg)
 
    def sendRMMsg(self, msg: RMMsg) -> bool:
        return self.__saveRMMsg(msg)
    
    def getMsg(self, userId) -> UniMsg:
        return self.__querryMsg(userId)


# class MyServer(TServer.TThreadPoolServer):
#      def serveClient(self, client):
#         """Process input/output from a client for as long as possible"""
#         itrans = self.inputTransportFactory.getTransport(client)
#         iprot = self.inputProtocolFactory.getProtocol(itrans)

#         # for THeaderProtocol, we must use the same protocol instance for input
#         # and output so that the response is in the same dialect that the
#         # server detected the request was in.
#         if isinstance(self.inputProtocolFactory, THeaderProtocolFactory):
#             otrans = None
#             oprot = iprot
#         else:
#             otrans = self.outputTransportFactory.getTransport(client)
#             oprot = self.outputProtocolFactory.getProtocol(otrans)
#         # 修改
#         # iprot.writeStructBegin('getUser_args')
#         # iprot.writeFieldBegin('ip', TType.STRING, 1)
#         # iprot.writeString(str(client.handle.getpeername()))
#         # iprot.writeFieldEnd()
#         # iprot.writeFieldStop()
#         # iprot.writeStructEnd()
#         iprot.clientInfo = str(client.handle.getpeername())
#         logger.warning(iprot.clientInfo)
#         try:
#             while True:
#                 self.processor.process(iprot, oprot)
#         except TTransport.TTransportException:
#             pass
#         except Exception as x:
#             logger.exception(x)

#         itrans.close()
#         if otrans:
#             otrans.close()


class MyServer(TServer.TThreadedServer):
    def handle(self, client):
        itrans = self.inputTransportFactory.getTransport(client)
        iprot = self.inputProtocolFactory.getProtocol(itrans)

        # for THeaderProtocol, we must use the same protocol instance for input
        # and output so that the response is in the same dialect that the
        # server detected the request was in.
        if isinstance(self.inputProtocolFactory, THeaderProtocolFactory):
            otrans = None
            oprot = iprot
        else:
            otrans = self.outputTransportFactory.getTransport(client)
            oprot = self.outputProtocolFactory.getProtocol(otrans)
        iprot.clientInfo = str(client.handle.getpeername())
        print(iprot.clientInfo)
        try:
            while True:
                self.processor.process(iprot, oprot)
        except TTransport.TTransportException:
            print('离线')
            pass
        except Exception as x:
            logger.exception(x)

        itrans.close()
        if otrans:
            otrans.close()

class MyProcess(Chatroom.Processor):
    def __init__(self, handler):
        super().__init__(handler)
        self._processMap["getUser"] = MyProcess.process_getUser
        self._processMap["sendRMMsg"] = MyProcess.process_sendRMMsg


    def process_getUser(self, seqid, iprot, oprot):
        args = getUser_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = getUser_result()
        args.ip = iprot.clientInfo
        try:
            result.success = self._handler.getUser(args.ip)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except TApplicationException as ex:
            logging.exception('TApplication exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = ex
        except Exception:
            logging.exception('Unexpected exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("getUser", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_sendRMMsg(self, seqid, iprot, oprot):
        from chatroom.Chatroom import sendRMMsg_args, sendRMMsg_result
        args = sendRMMsg_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = sendRMMsg_result()
        args.msg.clientInfo = iprot.clientInfo
        try:
            result.success = self._handler.sendRMMsg(args.msg)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except TApplicationException as ex:
            logging.exception('TApplication exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = ex
        except Exception:
            logging.exception('Unexpected exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("sendRMMsg", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()


if __name__ == '__main__':
    Users = []
    Request = []
    ServerHandle = []
    handler = ChatroomHandler()
    processor = MyProcess(handler)
    transport = TSocket.TServerSocket(host='0.0.0.0', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    # server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)
    server = MyServer(processor, transport, tfactory, pfactory)
    

    # You could do one of these for a multithreaded server
    # server = TServer.TThreadedServer(
    #     processor, transport, tfactory, pfactory)
    # server = TServer.TThreadPoolServer(
    #     processor, transport, tfactory, pfactory)

    print('Starting the server...')
    server.serve()
    print('done.')
