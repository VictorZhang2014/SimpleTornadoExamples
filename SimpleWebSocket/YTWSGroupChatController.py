#! encoding: utf-8
# 
# WebSocket的群组消息聊天
#
# Nginx配置
# http {
#   map $http_upgrade $connection_upgrade {
#        default upgrade;
#        ''      close;
#   }

#   server {
#        location ~ ^/stream/ws/gchat/([0-9a-z]+)$ {
#            proxy_pass http://localhost:8100;
#            proxy_http_version 1.1;
#            proxy_set_header Upgrade $http_upgrade;
#            proxy_set_header Connection "upgrade";
#            proxy_set_header Origin '';
#            proxy_read_timeout 300s;
#        } 
#    }
# }
# 


import tornado.websocket
import logging
import json, uuid, base64


class ErrorCode:
    failed_to_connect      = 1  
    message_not_valid      = 2


class ProtocolTypes:
    # 创建会话房间
    createRoom      = 1001  
    # 发送内容
    sendContent     = 1002
    # 发送文件
    sendFile        = 1003


logger = logging.getLogger('/home/wwwlogs/chat.log') 


GLOBAL_GROUP_ASSIGNED_NODES = {}   # 已分配房间的客户端节点

class YTWSGroupChatNode(object):
    def __init__(self, name, clients=[]):
        self.name = name
        self.clients = clients

    def __repr__(self):
        return "YTWSGroupChatNode: {0}.".format(self.name)


class YTWSGroupChatController(tornado.websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super(YTWSGroupChatController, self).__init__(application, request, **kwargs)
        self.current_node = None
        self.user_id = None
        self.user_uuid = None
        self.token = None

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def check_origin(self, origin):
        # To allow connections from any subdomain of your site, you might do something like: 
        print("====check_origin:" + origin) 
        if origin.split("://")[1] == "localhost:" or origin.split("://")[1] == "yooul.com":
            return True
        return True


    def open(self, roomNumber): 
        logger.info('WebSocket连接房间号：{} in IP {}'.format(roomNumber, self.request.remote_ip))
        if not self.is_valid_connect(roomNumber):
            self.__close_ws_connection(ErrorCode.failed_to_connect, "Your application for this connection is not valid! Please contact the website Admin.")
            return 
        # 把客户端加入到指定的房间里，每个房间有一个房间号，默认未分配房间的客户端将进入0号房间
        if roomNumber not in GLOBAL_GROUP_ASSIGNED_NODES:
            GLOBAL_GROUP_ASSIGNED_NODES[roomNumber] = YTWSGroupChatNode(roomNumber, [self])
        else:
            GLOBAL_GROUP_ASSIGNED_NODES[roomNumber].clients.append(self)
        # 设置当前连接的客户端
        self.current_node = GLOBAL_GROUP_ASSIGNED_NODES[roomNumber]
        logger.info('连接成功，当前客户端数量：{}'.format(len(self.current_node.clients)))

        # if len(self.current_node.clients) == 1:
        #     self.write_message('owner')
        # elif len(self.current_node.clients) == 2:
        #     self.write_message('guest')
        # else:
        #     self.write_message('magic_overload')

    def on_message(self, message):
        logger.info('Received message from {}'.format(self.request.remote_ip))
        if not self.is_valid_message(message):
            self.__close_ws_connection(ErrorCode.message_not_valid, "Message is not valid!")
            return
        self.__handle_message(message)


    def on_close(self): 
        if self.current_node is not None:
            logger.info('WebSocket连接已关闭。user_id={}'.format(self.user_id))
            self.current_node.clients.remove(self)

    # def close(self, code, reason):
    #     logger.info("Websocket closed, code={}, reason={}", code, reason)

    
    def __close_ws_connection(self, code, reason):
        # 关闭WebSocket连接
        self.close()
            
 
    def __handle_message(self, message):
        # 处理接收到的消息
        msgDict = json.loads(message)
        print("准备处理消息")
        # print(msgDict)
        protocol = msgDict["protocol"]
        roomNumber = msgDict["roomNumber"]
        userName = msgDict["userName"] 
        content = msgDict["content"]  
        language = msgDict["language"] 

        img_filepath, img_file_ext = "", ""
        if protocol == ProtocolTypes.sendFile:
            img_filepath, img_file_ext = self.save_image(content)
         
        # 设置当前连接的客户端
        self.current_node = GLOBAL_GROUP_ASSIGNED_NODES[roomNumber]

        # 发送消息
        for client in self.current_node.clients: 
            # if client is self:
            #     continue
            msgJsonStr = self.__construct_message_body(protocol, userName, roomNumber, content, language, filePath=img_filepath, fileExt=img_file_ext)
            print("发送的消息：" + msgJsonStr)
            client.write_message(msgJsonStr)


    def __construct_message_body(self, protocol, userName, roomNumber, content, language, filePath="", fileExt=""):
        body = {
            "protocol": protocol,
            "roomNumber": roomNumber,
            "userName": userName,
            "content": content,
            "language": language
        }
        if protocol == ProtocolTypes.sendFile:
            body["filepath"] = filePath
            body["fileext"] = fileExt
        print(body)
        return json.dumps(body)


    def __check_valid_token(self, token):
        # 用户的token是否有效
        return True


    def is_valid_connect(self, roomNum):
        # 请求连接的客户端是否合法 
        if roomNum is None or len(roomNum) <= 0:
            return False
        # host_name = self.request.host_name
        # if host_name != "localhost":
        #     return False
        # user_id = self.request.query_arguments.get("uid")
        # if user_id is None or len(user_id) <= 0:
        #     return False
        # user_uuid = self.request.query_arguments.get("uuid")
        # if user_uuid is None or len(user_uuid) <= 0:
        #     return False
        # self.user_id = int(str(user_id[0], encoding="utf-8"))
        # self.user_uuid = str(user_uuid[0], encoding="utf-8")
        return True


    def is_valid_message(self, message):
        # 接收到的消息是否是有效数据
        if message is None:
            return False
        try:
            msgDict = json.loads(message)
        except:
            return False
        else:
            if msgDict is None:
                return False
            protocol = msgDict["protocol"]
            if protocol is None or protocol <= 0:
                return False
            roomNumber = msgDict["roomNumber"]
            if roomNumber is None or len(roomNumber) <= 0:
                return False 
            # userName = msgDict["userName"]
            # if userName is None or len(userName) <= 0:
            #     return False
            # content = msgDict["content"] 
            # if content is None or len(content) <= 0:
            #     return False
            return True


    def save_image(self, filecontent):
        jpeg = "data:image/jpeg"
        jpg = "data:image/jpg"
        png = "data:image/png"
        file_ext = ""
        if filecontent.startswith(jpeg):
            file_ext = ".jpeg"
        elif filecontent.startswith(jpg):
            file_ext = ".jpg"
        elif filecontent.startswith(png):
            file_ext = ".png"
        saved_filepath = "static/tmp/" + str(uuid.uuid4()) + file_ext
        with open(saved_filepath, 'wb') as f:
            f.write(base64.b64decode(filecontent))
        return saved_filepath, file_ext





