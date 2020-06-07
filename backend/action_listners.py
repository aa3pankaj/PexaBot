from dbutils import MatchDatabase
import json
from message import Message
from helper import Helper
from constants import front_end_url
from helper import TelegramHelper


class ActionListener:
    
    @staticmethod
    def get_last_txn_from_history(match_id,status=None):
        if status == 'resume':
            MatchDatabase.set_match_status_live(match_id,"live")
        last_txn = MatchDatabase.get_last_txn(match_id)
        return last_txn
    @staticmethod
    def push_into_txn_history(match_id,SESSION_ID,action,intent_name,user_text,response):
        MatchDatabase.push_history(match_id,SESSION_ID,action,intent_name,user_text,response)
       
    @staticmethod
    def pause_match_listner(match_id,username,request):
        success = MatchDatabase.pause_match(match_id)
        if not success:
            return json.dumps(Message.get_invalid_request_payload())
        else:
            #exit_payload = ActionListener.exit_listner(match_id,request)
            pause_payload = Message.get_match_pause_payload(username)
            pause_payload = Helper.append_clear_context_payload(pause_payload,request)
            return json.dumps(pause_payload)
    
    @staticmethod
    def toss_action_listener(team1,team2,decision,toss_team,overs,match_id,start_date):
        _id =  MatchDatabase.update_teams(team1,team2,decision,toss_team,overs,start_date,match_id)
        return json.dumps(Message.match_start_payload(front_end_url+str(_id),team1))

    @staticmethod
    def ball_action_listener(run,match_id,chat_id,request,SESSION_ID,action,intent_name,user_text,response):
        MatchDatabase.update_players_stats(run,match_id)
        
        #just changuing strike for match score display of strike batsman in update_match_document(), 
        # no effect on conditions
        if run%2!=0:
            MatchDatabase.strike_change(match_id)
        res = MatchDatabase.update_match_document(run,match_id)
        
        #for live match only
        ActionListener.push_into_txn_history(match_id,SESSION_ID,action,intent_name,user_text,response)

        if (res is not None) and ("type" in res):
            if res["type"] == "ask_next_bowler":
                bowler_list = MatchDatabase.get_available_bowlers(match_id)
                TelegramHelper.send_keyboard_message(chat_id,"Next Bowler?",bowler_list)
                return res["response"]
            elif res["type"] == "end":
                MatchDatabase.set_match_status_end(match_id)
                end_message = Message.end_match_payload()
                res =  Helper.append_clear_context_payload(end_message,request)
                TelegramHelper.remove_keyboard(chat_id)
        return res
    @staticmethod   
    def most_runs_listener():
        user_detail = MatchDatabase.get_most_runs_user()
        return Message.get_user_stats_payload(user_detail)
    @staticmethod
    def user_stats_listener(username,source):
        user_id=MatchDatabase.userid_from_username(username,source)
        if user_id == None:
            return None
        user_detail = MatchDatabase.user_stats(user_id)
        print("user_stats********")
        print(str(user_detail))
        return Message.get_user_stats_payload(user_detail)
    @staticmethod
    def bowler_change_action_listener(bowler,match_id,chat_id):
        MatchDatabase.update_current_bowler(bowler,match_id)
        ball_number = MatchDatabase.get_current_ball_number(match_id)
        if ball_number == 6:
            MatchDatabase.strike_change(match_id)
        #TelegramHelper.send_ball_keyboard_message(chat_id)
        return ''
    @staticmethod
    def batsman_change_action_listener(batsman,match_id,chat_id):
        res = MatchDatabase.batsman_change(batsman,match_id)
        if (res is not None) and ("type" in res):
            if res["type"]=='ask_next_bowler':
                bowler_list = MatchDatabase.get_available_bowlers(match_id)
                TelegramHelper.send_keyboard_message(chat_id,"Next Bowler?",bowler_list)
                return json.dumps(res["response"])
            elif res["type"]=='next':
                TelegramHelper.send_ball_keyboard_message(chat_id)
                return json.dumps(res["response"])


        return json.dumps(res)
    @staticmethod
    def wide_with_number_action_listener(run,match_id):
        MatchDatabase.update_wide(run,match_id)
        return ''
    @staticmethod
    def noball_with_number_number_action_listener(run,match_id):
        MatchDatabase.update_noball(run,match_id)
        return ''
    @staticmethod
    def out_fielder_update_listner(match_id,chat_id,request,fielder=None):
        res = MatchDatabase.out_common(match_id,fielder=fielder)
        if res is not None and "type" in res:
            if res["type"] == 'ask_next_batsman':
                batsman_list = MatchDatabase.get_available_batsman(match_id)
                TelegramHelper.send_keyboard_message(chat_id,"Next Batsman?",batsman_list)
                return json.dumps({})
               
            elif res["type"] == "end":
                MatchDatabase.set_match_status_end(match_id)
                end_message = Message.end_match_payload()
                response =  Helper.append_clear_context_payload(end_message,request)
                TelegramHelper.remove_keyboard(chat_id)
                return json.dumps(response)
        return json.dumps(res)

    @staticmethod
    def out_action_listener(match_id,chat_id,request,out_type,run=None):
        # if innings over, send innings end message, if match ended , send message, else new batsman
        res=''
        print("run that we got in out_action_listener")
        print(run)
        
        if out_type == "bowled":
            res = MatchDatabase.out_common(match_id,out_type=out_type)

            if res is not None and "type" in res:
                if res["type"] == 'ask_next_batsman':
                    batsman_list = MatchDatabase.get_available_batsman(match_id)
                    TelegramHelper.send_keyboard_message(chat_id,"Next Batsman?",batsman_list)
                    return json.dumps({})
                    
                elif res["type"] == "end":
                    MatchDatabase.set_match_status_end(match_id)
                    end_message = Message.end_match_payload()
                    response =  Helper.append_clear_context_payload(end_message,request)
                    return json.dumps(response)

        else:
            res = MatchDatabase.out_update(match_id,out_type,run=run)
            if run != None and run%2!=0:
                MatchDatabase.strike_change(match_id)

            fielder_list = MatchDatabase.get_available_bowlers(match_id)
            TelegramHelper.send_keyboard_message(chat_id,"Fielder name?",fielder_list)

        return json.dumps(res)

    @staticmethod
    def update_on_strike_batsmen_listener(opening_batsmen_list,match_id,chat_id):
        
        MatchDatabase.update_on_strike_batsmen(opening_batsmen_list,match_id)
        bowler_list = MatchDatabase.get_available_bowlers(match_id)
        print('chat_id=')
        print(chat_id)
        TelegramHelper.send_keyboard_message(chat_id,"Opening Bowler?",bowler_list)
        #return json.dumps(Message.bowler_ask_payload(bolwer_list))

        
       
