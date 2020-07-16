from dbutils import MatchDatabase
import json
from message import Message
from helper import Helper
from constants import front_end_url
from helper import TelegramHelper
from db_util import BotDatabase
from constants import group_notification_enabled, group_id

class ActionListener:

    @staticmethod
    def undo_listener(chat_id,match_id):
        bot = BotDatabase(match_id)
        bot.undo_match()
        match_info = bot.get_live_match_info()
        if match_info["ball_number"] == 6:
            TelegramHelper.send_scoring_keyboard(chat_id,match_info,undo=True)
        else:
            TelegramHelper.send_scoring_keyboard(chat_id,match_info)

    @staticmethod
    def undo_next_over_action(chat_id,match_id):
        bot = BotDatabase(match_id)
        bowler_list = bot.get_available_bowlers()
        TelegramHelper.send_keyboard_message(chat_id,"Next Bowler?",bowler_list)

    @staticmethod
    def delete_live_matches_action(match_id):
        bot = BotDatabase(match_id)
        bot.delete_live_matches_of_user()

    @staticmethod
    def strike_change_action(chat_id,match_id):
        bot = BotDatabase(match_id)
        bot.strike_change()
        bot.match["undo_count"] = 1
        bot.match.save()
        match_info = bot.get_live_match_info()
        TelegramHelper.send_scoring_keyboard(chat_id,match_info)
        return json.dumps({})

    @staticmethod
    def add_players_action(team_name,team_players_list,match_id,chat_id,intent_name):
        bot = BotDatabase(match_id)
        bot.add_players(team_name,team_players_list)
        if intent_name == 'match.team2players':
            batsman_list = bot.get_available_batsman()
            TelegramHelper.send_keyboard_message(chat_id,"strike-batsman name?",batsman_list)
        return json.dumps({})

    @staticmethod
    def test_ball_listener(bowler,match_id,chat_id):
        bot = BotDatabase(match_id)
        bot.current_bowler_update(bowler)
        match_info = bot.get_live_match_info()
        TelegramHelper.send_scoring_keyboard(chat_id,match_info)

    @staticmethod
    def get_last_txn_from_history(match_id,status=None):
        print("status from get_last_txn_from_history:")
        print(status)
        if status == 'resume':
            BotDatabase.set_match_status(match_id,from_status="resume",to_status="live")
        last_txn = BotDatabase.get_last_txn(match_id)
        return last_txn
   
    @staticmethod
    def pause_match_listner(match_id,username,request):
        success = BotDatabase.set_match_status(match_id=match_id,from_status="live",to_status="pause")
        if not success:
            return json.dumps(Message.get_invalid_request_payload())
        else:
            #exit_payload = ActionListener.exit_listner(match_id,request)
            pause_payload = Message.get_match_pause_payload(username)
            pause_payload = Helper.append_clear_context_payload(pause_payload,request)
            return json.dumps(pause_payload)
    
    @staticmethod
    def toss_action_listener(team1,team2,decision,toss_team,overs,match_id,start_date):
        _id = BotDatabase.update_teams(team1,team2,decision,toss_team,overs,start_date,match_id)
        if group_notification_enabled:
            TelegramHelper.send_general_message(group_id,Message.match_start_group_payload(front_end_url+str(_id),team1,team2,match_id))
        return json.dumps(Message.match_start_payload(front_end_url+str(_id),team1))

    @staticmethod
    def ball_action_listener(run,match_id,chat_id,request,SESSION_ID,action,intent_name,user_text,response):
        #TODO bowler stats update
        bot = BotDatabase(match_id)
        bot.players_stats_update(int(run))
        res = bot.run_update(int(run))
        
        #for resume match only
        #TODO below
        BotDatabase.push_history(match_id,SESSION_ID,action,intent_name,user_text,res["response"])
    
        if res["type"] == "ask_next_bowler":
            bowler_list = bot.get_available_bowlers()
            TelegramHelper.send_keyboard_message(chat_id,res['response']+"\n\nNext Bowler?",bowler_list)
            return json.dumps({})
        elif res["type"] == "end":
            # end_message = Message.end_match_payload()
            # res =  Helper.append_clear_context_payload(end_message,request)
            clear =  Helper.clear_contexts(match_id,request)
            TelegramHelper.remove_keyboard(chat_id)
            return clear
        elif res["type"] == "change":
            TelegramHelper.send_keyboard_general(chat_id,"change innings?",[[{"text":"change"},{"text":"Undo"}]])
            return json.dumps({})

        match_info = bot.get_live_match_info()
        TelegramHelper.send_scoring_keyboard(chat_id,match_info)
        return json.dumps({})

    @staticmethod   
    def most_runs_listener():
        user_detail = BotDatabase.get_most_runs_user()
        return Message.get_user_stats_payload(user_detail)

    @staticmethod
    def user_stats_listener(username,source):
        user_id=BotDatabase.userid_from_username(username,source)
        if user_id == None:
            return None
        user_detail = BotDatabase.user_stats(user_id)
        print("user_stats********")
        print(str(user_detail))
        return Message.get_user_stats_payload(user_detail)

    @staticmethod
    def bowler_change_action_listener(bowler,match_id,chat_id):
        bot = BotDatabase(match_id)
        bot.current_bowler_update(bowler)
        match_info = bot.get_live_match_info()
        TelegramHelper.send_scoring_keyboard(chat_id,match_info)
        return json.dumps({})

    @staticmethod
    def wide_with_number_action_listener(run,match_id,chat_id):
        bot = BotDatabase(match_id)
        bot.wide_update(int(run))
        match_info = bot.get_live_match_info()
        TelegramHelper.send_scoring_keyboard(chat_id,match_info)
        return json.dumps({})

    @staticmethod
    def noball_with_number_number_action_listener(run,match_id,chat_id):
        bot = BotDatabase(match_id)
        bot.noball_update(int(run))
        match_info = bot.get_live_match_info()
        TelegramHelper.send_scoring_keyboard(chat_id,match_info)
        return json.dumps({})

    #no fielder intent required
    @staticmethod
    def out_without_fielder_action(match_id,chat_id,request,out_type):
        bot = BotDatabase(match_id)
        response = bot.out_without_fielder(out_type)
        if response["type"] == 'ask_next_batsman':
            batsman_list = bot.get_available_batsman()
            TelegramHelper.send_keyboard_message(chat_id,"Next Batsman?",batsman_list)
            return json.dumps({})
                
        elif response["type"] == "end":
            BotDatabase.set_match_status(match_id=match_id,from_status="live",to_status="end")
            clear =  Helper.clear_contexts(match_id,request)
            TelegramHelper.remove_keyboard(chat_id)
            return clear

        elif response["type"] == "change":
            TelegramHelper.send_keyboard_general(chat_id,"change innings?",[[{"text":"change"},{"text":"Undo"}]])
            return json.dumps({})

    @staticmethod
    def batsman_change_action_listener(batsman,match_id,chat_id):
        bot = BotDatabase(match_id)
        response = bot.batsman_change(batsman)
       
        if response["type"]=='ask_next_bowler':
            bowler_list = bot.get_available_bowlers()
            TelegramHelper.send_keyboard_message(chat_id,response['response']+"\n\nNext Bowler?",bowler_list)
            return json.dumps({})
        elif response["type"]=='next':
            match_info = bot.get_live_match_info()
            TelegramHelper.send_scoring_keyboard(chat_id,match_info)
            # TelegramHelper.send_ball_keyboard_message(chat_id)
            return json.dumps({})
        return json.dumps({})


    """
    runout start
    """
    @staticmethod
    def runout_batsman_action(match_id,chat_id,batsman_type):
        bot = BotDatabase(match_id)
        bot.runout_batsman_out_update(batsman_type)
       
    @staticmethod
    def runout_update(match_id,chat_id,request,out_type,run):
        #TODO bowler stats update, personnel
        bot = BotDatabase(match_id)
        bot.run_out_update(out_type,int(run))

        fielder_list = bot.get_available_bowlers()
        TelegramHelper.send_keyboard_message(chat_id,"Fielder name?",fielder_list)
        return json.dumps({})
    """
    runout end
    """
        
    #fielder intent required
    @staticmethod
    def out_with_fielder_action(match_id,chat_id,request,out_type):
        bot = BotDatabase(match_id)
        bot.out_with_fielder(out_type)

        fielder_list = bot.get_available_bowlers()
        TelegramHelper.send_keyboard_message(chat_id,"Fielder name?",fielder_list)
        return json.dumps({})
        

    @staticmethod
    def out_fielder_update_listner(match_id,chat_id,request,fielder):
        bot = BotDatabase(match_id)
        response = bot.out_fielder_update(fielder)

        if response["type"] == 'ask_next_batsman':
            batsman_list = bot.get_available_batsman()
            TelegramHelper.send_keyboard_message(chat_id,"Next Batsman?",batsman_list)
            return json.dumps({})
            
        elif response["type"] == "end":
            BotDatabase.set_match_status(match_id=match_id,from_status="live",to_status="end")
           
            clear =  Helper.clear_contexts(match_id,request)
            TelegramHelper.remove_keyboard(chat_id)
            return clear
            
        elif response["type"] == "change":
            TelegramHelper.send_keyboard_general(chat_id,"change innings?",[[{"text":"change"},{"text":"Undo"}]])
            return json.dumps({})

        return json.dumps(response['response'])

    @staticmethod
    def update_on_strike_batsmen_listener(batsman,match_id,chat_id,batsman_type):
        bot = BotDatabase(match_id)
        bot.on_strike_batsmen_update(batsman,batsman_type)
        player_list=[]
        if batsman_type == "strike_batsman":
            player_list = bot.get_available_batsman()
            TelegramHelper.send_keyboard_message(chat_id,"non-strike batsman?",player_list)
        else:
            player_list = bot.get_available_bowlers()
            TelegramHelper.send_keyboard_message(chat_id,"Opening Bowler?",player_list)
        return json.dumps({})

        
       
