namespace cl user
namespace cpp user
namespace d user
namespace dart user
namespace java user
namespace php user
namespace perl user
namespace haxe user
namespace netstd user

typedef i32 iTime

struct User {
    1: i32 userId,
    2: optional string username,
    3: optional UserInfo userInfo,
}

struct UserInfo {
    1:iTime creatTime,
    2:iTime registerTime,
    3:string introduce
}

exception UserOperationError {
    1: string operation,
    2: string username,
    3: string why,
}

service UserService {
    //  游客身份连接时，获取User唯一标识符
    User getUser(1:optional string ip),

    //  注册用户
    User userRegister(
        1:string username, 
        2:string passwd, 
        3:optional i32 userId, 
        4:optional map<string,string> userInfo
        ) throws (1: UserOperationError error),

    // 用户登陆
    User userLogin(1:string username, 2:string passwd) throws (
        1: UserOperationError error
    ),

    // 用户登出
    bool userLogout(1:i32 userId, 2:string username)
    // 修改密码
    bool updatePasswd(
        1:string username,
        2:string passwd,
        3:string newpasswd
    ) throws (1: UserOperationError error)

    // 修改信息
    bool updateUserInfo(
        1:string userId,
        2:optional string username,
        3:optional map<string,string> userInfo
    )
}

