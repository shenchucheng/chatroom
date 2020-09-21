include "./user.thrift"

namespace cl chatroom
namespace cpp chatroom
namespace d chatroom
namespace dart chatroom
namespace java chatroom
namespace php chatroom
namespace perl chatroom
namespace haxe chatroom
namespace netstd chatroom


typedef i32 iUserId
typedef i32 iRoomId
typedef i32 iTime
typedef i64 iMsg
typedef i64 iRMMsg

// 个人消息
struct Msg {
    1:string content,
    2:iTime timestamp,
    3:iUserId fromUserId,
    4:iUserId toUserId,
    5:iMsg msgId,
    6:iTime saveTime,
    7:optional string clientInfo
}

// 群聊消息
struct RMMsg {
    1:string content,
    2:iTime timestamp,
    3:iUserId userId,
    4:iRoomId chatroomId,
    5:iRMMsg msgId,
    6:iTime saveTime,
    7:optional string clientInfo
}

// 轮询返回消息
struct UniMsg {
    1:list<Msg> user,
    2:list<RMMsg> room
}

// 群聊房间
struct Room {
    1:iRoomId roomId,
    2:string roomName,
    3:set<iUserId> members,
    4:iUserId roomOwer,
    5:optional RoomInfo roomInfo,
    6:list<RMMsg> msgs
}

// 群信息
struct RoomInfo{
    1:iTime creatTime,
    2:string introduce
}

exception ChatroomOperationError{
    1:string operation,
    2:string reason
}

service Chatroom extends user.UserService {
    // 发送个人消息
    bool sendMsg(1:Msg msg),

    // 发送群聊消息
    bool sendRMMsg(1:RMMsg msg),

    // 消息轮询 所有消息处理
    UniMsg getMsg(1:iUserId userId),

    // 建立群聊
    Room createRoom(
        1:string roomName,
        2:iUserId roomOwer,
        3:optional set<iUserId> members,
        4:optional RoomInfo roomInfo
    ) throws (1:ChatroomOperationError error),

    // 解散群聊
    bool dismissRoom(1:iRoomId roomId, 2:iUserId userId) throws(
        1:ChatroomOperationError error
    ),

    // 用户加入群聊
    bool joinRoom(
        1:iRoomId roomId, 
        2:list<iUserId> members, 
        3:optional string msg
    ) throws (1:ChatroomOperationError error),

    // 管理员处理群聊请求
    bool processRoomRequest(
        1:iRoomId chatroomId, 
        2:iUserId userId, 
        3:iUserId memberId
    ) throws (1:ChatroomOperationError error),
    
    // 管理员移除群用户
    bool removeRoomMenbers(
        1:iRoomId roomId,
        2:iUserId userId,
        3:list<iUserId> members,
    ) throws(1:ChatroomOperationError error),

    // 退出群聊
    bool leaveRoom(1:iRoomId roomId, 2:iUserId userId),
}