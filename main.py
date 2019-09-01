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
        raw_regex = re.compile(r"\b" + word + r"\b", re.IGNORECASE)
        incidences = raw_regex.findall(given_string)
        return len(incidences)

    def luhns_algorithm(self,card_number):
        for i in range(len(card_number)-2,-1,-2):
            sum_number = 0
            modified_number = str(int(card_number[i])*2)
            if(len(modified_number) > 1):
                for each_alphabet in modified_number:
                    sum_number += int(each_alphabet)
            else:
                sum_number = int(modified_number)
            card_number = card_number[:i] + str(sum_number) + card_number[i+1:]
        
        sum_of_all_digits = 0
        
        for each_alphabet in card_number:
            sum_of_all_digits += int(each_alphabet)

        if(sum_of_all_digits%10 == 0):
            return True
        else:
            return False

    def message_preprocessing(self,message):
        if(self.name == None):
            self.name = message["user"]
        if(self.credit_card == None):
            credit_card_possibilities = ['credit card', 'CREDIT CARD', 'Credit Card', 'cReDiT CaRd','credit-card','credit - card','bank card','account card']
            for each_word in credit_card_possibilities:
                regex_result = self.find_word(each_word,message["message"])
                if(regex_result>0):
                    return 'You query requires your credit card number! Please input it!'
            try:            
                if(self.luhns_algorithm(message["message"]) == False):
                    return 'Invalid card number! Please recheck!'
                elif(self.luhns_algorithm(message["message"]) == True):
                    self.credit_card = message["message"]
                    return 'Thank you for entering your card number! Now please enter your query again so we can assist you!'
            except ValueError:
                pass
        return 'It hit nothing'

    def prepare_message(self,preprocessed_message):
        JSON_variable = {}
        JSON_variable['user'] = 'Server'
        JSON_variable['message'] = preprocessed_message
        return JSON_variable

    def on_message(self, message):
        preprocessed_message = self.message_preprocessing(json.loads(message))
        final_message = self.prepare_message(preprocessed_message)
        # print(self.name)
        # print(self.credit_card)
        self.write_message(message)
        self.write_message(final_message)

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