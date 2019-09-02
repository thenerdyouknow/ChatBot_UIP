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

    def sum_and_modulo(self,number_to_sum):
        for each_alphabet in number_to_sum:
            sum_of_all_digits += int(each_alphabet)

        if(sum_of_all_digits%10 == 0):
            return True
        else:
            return False

    def luhns_algorithm(self,card_number):

        if(len(card_number)<13 or len(card_number)>16):
            return False

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
        
        return self.sum_and_modulo(card_number)

    def account_validator(self,account_number):
        raw_regex = re.compile("^\\d{9,18}$",re.IGNORECASE)
        incidences = raw_regex.findall(account_number)
        if(len(incidences) == 1):
            return True
        else:
            return False

    def find_word(self,word,given_string):
        raw_regex = re.compile(r"\b" + word + r"\b", re.IGNORECASE)
        incidences = raw_regex.findall(given_string)
        return len(incidences)

    def prepare_message(self,preprocessed_message):
        JSON_variable = {}
        JSON_variable['user'] = 'Server'
        JSON_variable['message'] = preprocessed_message
        return JSON_variable

    def open(self):
        self.write_message(self.prepare_message('Hello! I can help you with queries regarding your credit card or bank account! Please enter your query below'))
        self.name = None
        self.credit_card = None
        self.account_number = None
        self.credit = 0
        self.account = 0        
        return

    def message_preprocessing(self,message):

        
        if(self.credit_card == None):
            credit_card_possibilities = ['credit card','credit-card','credit - card','bank card','account card']
            for each_word in credit_card_possibilities:
                regex_result = self.find_word(each_word,message["message"])
                if(regex_result>0):
                    self.credit = 1
                    self.account = 0
                    return 'You query requires your credit card number! Please input it!'
            if(self.credit == 1):
                try:            
                    if(self.luhns_algorithm(message["message"]) == False):
                        return 'Invalid card number! Please recheck!(We require a valid number to move forward, refresh the page if you would like to ask something else!)'
                    elif(self.luhns_algorithm(message["message"]) == True):
                        self.credit_card = message["message"]
                        return 'Thank you for entering your card number! Now please enter your query again so we can assist you!'
                except ValueError:
                    pass
        
        if(self.account_number == None):
            account_number_possibilities = ['account','savings','checking','balance in account','account balance','remaining money','balance money','how much money']
            for each_word in account_number_possibilities:
                regex_result = self.find_word(each_word,message["message"])
                if(regex_result>0):
                    self.account = 1
                    self.credit = 0
                    return 'Your query requires your bank account number! Please input it!'
            if(self.account == 1):
                try:
                    if(self.account_validator(message["message"])):
                        self.account_number = message["message"]
                        return 'Thank you for entering your account number! Please enter your query again so we can assist you!'
                    elif(self.account_validator(message["message"]) == False):
                        return 'Invalid account number! (We require a valid number to move forward, refresh the page if you would like to ask something else!)'
                except:
                    pass
        return ''


    def on_message(self, message):

        if(self.name == None):
            self.name = message["user"]

        self.write_message(message)
        if(self.account_number == None or self.credit_card == None or self.name == None):
            preprocessed_message = self.message_preprocessing(json.loads(message))
            final_message = self.prepare_message(preprocessed_message)
            self.write_message(final_message)
            return
        self.write_message('Haha')
        return

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