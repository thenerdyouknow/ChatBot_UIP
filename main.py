import os
import re
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
        self.name = None
        self.credit_card = None
        self.account_number = None
        return

    def find_word(self,word,given_string):
        preprocessed_word = word.strip()
        raw_regex = re.compile(r"\b" + preprocessed_word + r"\b")


    def message_preprocessing(self,message):
        print(message)
        if(self.name == None):
            self.name = message["user"]
        return

    def construct_response(self,message):
        server_response = {}
        server_response["user"] = "Server"
        server_response["message"] = "haha,it works!"
        return server_response

    def on_message(self, message):
        server_response = self.construct_response(message)
        preprocessed_message = self.message_preprocessing(json.loads(message))
        print(self.name)
        self.write_message(message)
        self.write_message(server_response)

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