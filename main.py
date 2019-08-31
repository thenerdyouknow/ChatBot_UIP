import os
import json
import tornado.options
import tornado.ioloop
import tornado.web
import tornado.websocket
 
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class EchoWebSocket(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        lol = {}
        lol["user"] = "Server"
        lol["message"] = "haha,it works!"
        self.write_message(message)
        self.write_message(lol)

    def on_close(self):
        print("WebSocket closed")
 
def make_app():
    return tornado.web.Application(
        handlers = [
            (r'/', MainHandler),
            (r'/websocket', EchoWebSocket),
        ],
        template_path = os.path.join(os.path.dirname( __file__ ),"templates"),
        static_path = os.path.join(os.path.dirname( __file__ ),"static"),
        # ui_modules={'package_includes': PackagesIncludeModule},
        debug = True,
    )
 
if __name__ == "__main__":
    app = make_app()
    app.listen(8100)
    tornado.ioloop.IOLoop.current().start()