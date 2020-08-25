import json
import tornado.ioloop
import tornado.web
from tornado import websocket


class MyWebSocketHandler(websocket.WebSocketHandler):
    # 保存连接的用户，用于后续推送消息
    connect_users = dict()

    def open(self):
        pass

    def on_message(self, message):
        try:
            connect_data = json.loads(message)
        except Exception as err:
            connect_data = json.loads({})

        if connect_data.get("connection", 0):
            # 将用户保存到connect_users中
            self.connect_users[connect_data.get("connection", 0)] = self

    def on_close(self):
        # 关闭连接时将用户从connect_users 字典中移除
        del self.connect_users[list(self.connect_users.keys())[list(self.connect_users.values()).index(self)]]

    def check_origin(self, origin):
        # 此处用于跨域访问
        return True

    # 服务端向客户端广播
    @classmethod
    def send_all_updates(cls, message):
        # 给所有用户推送消息（此处可以根据需要，修改为给指定用户进行推送消息）
        for user in cls.connect_users:
            cls.connect_users[user].write_message(message)
        return 1

    # 服务端向客户端一对一
    @classmethod
    def send_one_updates(cls, message, uuid):
        try:
            cls.connect_users[uuid].write_message(message)
            return 1
        except KeyError as err:
            return 0


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class StartHandler(tornado.web.RequestHandler):
    def get(self):
        MyWebSocketHandler.send_all_updates("这里是后端广播")
        MyWebSocketHandler.send_one_updates("这里是后端单播", "uuid1")
        self.write("ok")


class Printl(tornado.web.RequestHandler):
    def get(self):
        self.render("print.html")


settings = {
    'debug': False,
    'template_path': 'templates',
    'static_path': 'static'
}


def make_app():
    return tornado.web.Application([
        (r"/webSocket", MyWebSocketHandler),
        (r"/", MainHandler),
        (r"/start", StartHandler),
        (r"/print", Printl),
    ], **settings)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()