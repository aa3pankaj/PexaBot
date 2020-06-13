from __future__ import print_function
import time
# import pdf_generator_api_client
# from pdf_generator_api_client.rest import ApiException
from pprint import pprint
import json
import codecs
import jwt
# from pdfgeneratorapi import PDFGenerator
from dbutils import MatchDatabase
from constants import exit_set
from message import Message

from telegram import ReplyKeyboardMarkup, Bot, ReplyKeyboardRemove
import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

class Helper:
    @staticmethod
    def get_list_of_players(players_string):
        return players_string.split()

    @staticmethod
    def append_clear_context_payload(payload,request):
        for context in request['queryResult']['outputContexts']:
            context['lifespanCount']=0
            payload['outputContexts'].append(context)
        return payload
    @staticmethod
    def get_match_params(request):
        match_params = {}  
        source=''
        match_id=''
        username= ''
        start_date=''
        if 'source' in request['originalDetectIntentRequest']: 
            source = request['originalDetectIntentRequest']['source']
        # else:
        #     return json.dumps(Message.get_invalid_request_payload())
        #have to update for other platforms
        if source == 'telegram':
            username = request['originalDetectIntentRequest']['payload']['data']['from']['username']
            start_date = request['originalDetectIntentRequest']['payload']['data']['date']
            if username[:1]=='@':
                username = username[1:]
            match_id = MatchDatabase.userid_from_username(username,source)
        else:
            match_id= "test"
            start_date = ''
        match_params["username"] = username
        match_params["match_id"] = match_id
        match_params["start_date"] = start_date
        match_params["source"] = source
        if request['queryResult']['queryText'] in exit_set:
            match_params['exit']= Helper.clear_contexts(match_id,request)
        return match_params
    
    def remove_space(input): 
        pattern = re.compile(r'\s+') 
        return re.sub(pattern, '', input) 
    @staticmethod
    def clear_contexts(match_id,request):
        #can also be done using "resetContexts": True, using query_params in detect_intent
        res = Helper.exit_conversation(match_id,request)
        print(res)
        return json.dumps(res)

    @staticmethod
    def exit_conversation(match_id,request):
        # session = request['session']
        # SESSION_ID = session.rpartition('/')[2]
        MatchDatabase.set_match_status_end(match_id)
        exit_payload = Message.exit_payload()
        if not 'outputContexts' in request['queryResult']:
            return exit_payload
        return Helper.append_clear_context_payload(exit_payload,request)

class TelegramHelper:
    @staticmethod
    def send_scoring_keyboard(chat_id,match_info):
        print("testing telegram bot send_scoring_keyboard..........")
        bot = Bot(TELEGRAM_TOKEN)
        custom_keyboard = Message.scoring_custom_payload(match_info)
        reply_markup = ReplyKeyboardMarkup(keyboard=custom_keyboard,resize_keyboard=True)
        bot.send_message(chat_id=chat_id, text= "what happened on the next ball?", reply_markup=reply_markup)

    @staticmethod
    def remove_keyboard(chat_id):
        bot = Bot(TELEGRAM_TOKEN)
        remove_keyboard = ReplyKeyboardRemove(remove_keyboard= True)
        bot.send_message(chat_id=chat_id, text= "Ended conversation" ,reply_markup=remove_keyboard)

    @staticmethod
    def send_keyboard_general(chat_id,message,buttonList):
        print("testing telegram bot send_keyboard_general..........")
        bot = Bot(TELEGRAM_TOKEN)
        reply_markup = ReplyKeyboardMarkup(buttonList)
        bot.send_message(chat_id=chat_id, text= message , reply_markup=reply_markup)

    @staticmethod
    def send_ball_keyboard_message(chat_id):
        print("testing telegram bot send_ball_keyboard_message..........")
        bot = Bot(TELEGRAM_TOKEN)
        custom_keyboard = Message.ball_update_custom_keyboard()
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)
        bot.send_message(chat_id=chat_id, text= "Out Recorded!" , reply_markup=reply_markup)

    @staticmethod
    def validate_platform_user_request_message(request):

        # if len(request['originalDetectIntentRequest']['payload']['data']['entities']) > 2 or \
        #     len(request['originalDetectIntentRequest']['payload']['data']['entities']) == 0:
        #     return False
        # elif len(request['originalDetectIntentRequest']['payload']['data']['entities']) == 1: 
        #     if not request['originalDetectIntentRequest']['payload']['data']['entities'][0]['type']=='mention':
        #         return False
        return True

    @staticmethod
    def send_keyboard_message(chat_id,text,player_list):

        bot = Bot(TELEGRAM_TOKEN)
        custom_keyboard = []
        calback = Message.empty_keyboard_button()
        print("sending player select keyboard")
        for x in player_list:
            if "overs" in x:
                if x["overs"]==0:
                    calback[0]['text'] = x["name"]
                else:
                    #calback[0]['text'] = x["name"]+" "+x["overs"]
                    calback[0]['text'] = x["name"]
                calback[0]['callback_data'] = x["name"]
            else:
                calback[0]['text'] = x
                calback[0]['callback_data'] = x

            custom_keyboard.append(calback)
            calback =[{
                    
                    "text": "",
                    "callback_data": "" 
                }]
        
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)
        bot.send_message(chat_id=chat_id, text= text , reply_markup=reply_markup,resize_keyboard=True)
