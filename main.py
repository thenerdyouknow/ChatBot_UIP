import os
import re
import time
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
        sum_of_all_digits = 0
        for each_alphabet in number_to_sum:
            sum_of_all_digits += int(each_alphabet)

        if(sum_of_all_digits%10 == 0):
            return True
        else:
            return False

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
               
        return self.sum_and_modulo(card_number)

    def credit_validator(self,card_number):
        raw_regex = re.compile("^\\d{13,16}$", re.IGNORECASE)
        incidences = raw_regex.findall(card_number)
        if(len(incidences) == 1):
            return self.luhns_algorithm(card_number)
        else:
            return False

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

    def credit_find_word(self,word,given_string):
        raw_regex = re.compile(r"^\b" + word + r"\b$", re.IGNORECASE)
        incidences = raw_regex.findall(given_string)
        return len(incidences)

    def raw_find_word(self, given_regex,given_string):
        raw_regex = re.compile(given_regex, re.IGNORECASE)
        incidences = raw_regex.findall(given_string)
        return len(incidences)

    def prepare_message(self,preprocessed_message):
        JSON_variable = {}
        JSON_variable['user'] = 'Server'
        JSON_variable['message'] = preprocessed_message
        return JSON_variable

    def bank_account_regex(self,message):
        raw_account_number_regex = ['balance.*account|account.*balance','balance.*bank|bank.*balance','money left.*account|account.*money left','remainder.*account|account.*remainder','how much.*account|account.*how much']
        account_number_possibilities = ['balance in account','how much money do i have in the bank','remaining money','balance money','amount left','checkings balance','savings balance','how much can i withdraw','amount of debit','debit limit']
        for each_word in account_number_possibilities:
            regex_result = self.find_word(each_word,message)
            if(regex_result>0):
                return True
        for each_regex in raw_account_number_regex:
            raw_regex_result = self.raw_find_word(each_regex,message)
            if(raw_regex_result>0):
                return True
        return False

    def credit_card_regex(self,message):
        
        credit_card_possibilities = ['credit card','credit-card','credit - card','bank card','account card']
        for each_word in credit_card_possibilities:
            if(self.credit_find_word(each_word,message)>0):
                return 'Your query is too vague, please clarify!'
        
        credit_card_due_possibilities = ['credit.*due date|due date.*credit','payable.*credit|credit.*payable','owed.*credit|credit.*owed','date.*credit|credit.*date','have i paid.*credit|credit.*have i paid','credit.*bill|bill.*credit','last date.*bill|bill.*last date']
        credit_card_due_sentences = ['money due on credit card','when is my credit amount due','due amount on credit card','due credit amount','due money on credit card','amount due on credit card','due on credit card']
        for each_regex in credit_card_due_possibilities:
            if(self.raw_find_word(each_regex,message)>0):
                return 'Your credit card numbered ' +str(self.credit_card) + ' has dues that equal to 10,000 dollars! This needs to be paid by 24th July,2019.'
        for raw_sentence in credit_card_due_sentences:
            if(self.find_word(raw_sentence,message)>0):
                return 'Your credit card numbered ' +str(self.credit_card) + ' has dues that equal to 10,000 dollars! This needs to be paid by 24th July,2019.'

        raw_credit_card_possibilities = ['credit.*outstanding|outstanding.*credit','total.*credit|total.*credit','full.*credit|credit.*full']
        for each_regex in raw_credit_card_possibilities:
            if(self.raw_find_word(each_regex,message)>0):
                return 'Your credit card numbered ' +str(self.credit_card) + ' has total outstanding dues equal to 24,000 dollars!'
        return None        


    def open(self):
        self.write_message(self.prepare_message('Hello! I can help you with queries regarding your credit card or bank account! Please enter your query below!(Write "Stop" if you want to restart)'))
        self.name = None
        self.credit_card = None
        self.account_number = None
        self.credit = 0
        self.account = 0
        self.last_message = ''
        return

    def message_preprocessing(self,message):

        if(self.credit_card is None):
            result = self.credit_card_regex(message["message"])
            if(result is not None):
                self.last_message = message["message"]
                self.credit = 1
                self.account = 0
                return 'You query requires your credit card number! Please input it!'

            if(self.credit == 1):
                try:            
                    if(self.credit_validator(message["message"]) == False):
                        return 'Invalid card number! Please remove all formatting like spaces if you have put any!(We require a valid number to move forward, write "Stop" if you would like to ask something else!)'
                    elif(self.credit_validator(message["message"]) == True):
                        self.credit_card = message["message"]
                        return 'Thank you for entering your card number!'
                except ValueError:
                    pass
        
        if(self.account_number is None):
            result = self.bank_account_regex(message["message"])
            if(result):
                self.last_message = message["message"]
                self.account = 1
                self.credit = 0
                return 'Your query requires your bank account number! Please input it!'

            if(self.account == 1):
                try:
                    if(self.account_validator(message["message"])):
                        self.account_number = message["message"]
                        return 'Thank you for entering your account number!'

                    elif(self.account_validator(message["message"]) == False):
                        return 'Invalid account number! Please remove all formatting like spaces if you have put any! (We require a valid number to move forward, write "Stop" if you would like to ask something else!)'

                except ValueError:
                    pass

    def providing_details(self,message):
        if(self.account_number is not None):
            result = self.bank_account_regex(message)
            if(result):
                return 'Your bank account numbered '+str(self.account_number)+ ' has a balance of 3400 dollars!'

        if(self.credit_card is not None):
            if(self.credit_card_regex(message) is not None):
                return self.credit_card_regex(message)

        return "I can't answer that. Please contact the branch!"


    def conversation_starter(self,message):
        starter_possibilities = ['hello','hi',"what's up",'sup',"how's it going",'how are they hanging','what can you do','help']
        for each_word in starter_possibilities:
            regex_count = self.find_word(each_word,message)
            if(regex_count>0):
                return 'Hello! I am the bank chatbot. I deal with queries related to your savings or checking account!'


    def on_message(self, message):

        self.write_message(message)
        JSON_message = json.loads(message)

        message_to_check = JSON_message['message']

        if(self.name is None):
            self.name = JSON_message["user"]

        hello_check = self.conversation_starter(JSON_message["message"])
        if(hello_check is not None):
            self.write_message(self.prepare_message(hello_check))
            return

        stop_flag = self.find_word('stop',JSON_message["message"])
        if(stop_flag == 1):
            self.write_message(self.prepare_message('Resetting conversation...'))
            time.sleep(1.5)
            self.write_message(self.prepare_message('Wipe'))
            self.open()
            return

        preprocessed_message = self.message_preprocessing(JSON_message)
        final_message = self.prepare_message(preprocessed_message)
        if(preprocessed_message == 'Thank you for entering your account number!' or
            preprocessed_message == 'Thank you for entering your card number!'):
            self.write_message(final_message)
            message_to_check = self.last_message
        elif(preprocessed_message is not None):
            self.write_message(final_message)
            return

        response = self.providing_details(message_to_check)
        final_message = self.prepare_message(response)
        self.write_message(final_message)
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
        debug = True,
    )
 
if __name__ == "__main__":
    app = make_app()
    app.listen(8100)
    tornado.ioloop.IOLoop.current().start()