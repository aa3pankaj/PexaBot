"""
This webhook is meant to be used with the cricbot agent for Dialogflow
"""
import re
import json
from dbutils import MatchDatabase
from message import Message
from helper import Helper, TelegramHelper
from flask import Flask, request as flask_request, make_response, jsonify
import os
import dialogflow_v2
from google.api_core.exceptions import InvalidArgument
from action_listners import ActionListener
from flask_assistant import Assistant, ask, request
from constants import DIALOGFLOW_LANGUAGE_CODE
from bson.json_util import dumps
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO

DIALOGFLOW_PROJECT_ID = os.getenv('DIALOGFLOW_PROJECT_ID')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'cricbot-qegqqr-a46e4f1cad3b.json'

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
assist = Assistant(app, route='/api', project_id=DIALOGFLOW_PROJECT_ID)
#assist = Assistant(app, project_id=DIALOGFLOW_PROJECT_ID)
log = app.logger

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app,cors_allowed_origins="*")

#not_used
@app.route('/live_match_data', methods=['GET'])
@cross_origin()
def get_live_match_data():
    match_doc = MatchDatabase.get_match_document("@pankajsingh08")
    return make_response(dumps(match_doc))

#using for live match as well as old match scoreboard
@app.route('/match_data/<id>', methods=['GET'])
@cross_origin()
def get_match_data(id):
    print(id)
    
    match_doc = MatchDatabase.get_match_document_by_id(id)
    return make_response(dumps(match_doc))

@assist.action('admin.link.users')
def link_bot_user(bot_user,platform_user):
    print('in ********* link_bot_user')
    try:
        if platform_user[:1]=='@':
            platform_user = platform_user[1:]
        source = request['originalDetectIntentRequest']['source']
        res= ''
        if source == 'telegram':
            if not TelegramHelper.validate_platform_user_request_message(request):
                res =  Message.get_invalid_request_payload()
                return json.dumps(res)
        print(bot_user)
        print(platform_user)
        print(source)
        if not MatchDatabase.user_already_exist(bot_user):
            res = MatchDatabase.link_users(bot_user,platform_user,source)
            if res == False:
                res =  Message.get_invalid_request_payload()
            else:
                res =  Message.general_message("done")
        else:
            res = Message.get_invalid_request_payload()
        return make_response(json.dumps(res))
    except Exception as e:
        return Message.get_invalid_request_payload()

@assist.action('fetch.most.runs')
def most_runs():
    return make_response(json.dumps(ActionListener.most_runs_listener()))

@assist.action('fetch.my.stats')
def user_stats():

    match_params = Helper.get_match_params(request)
    print("username="+match_params['username'])

    if not match_params['username'] == '':
        response = ActionListener.user_stats_listener(match_params['username'],match_params['source'])
        if response == None:
            return json.dumps(Message.get_invalid_request_payload())
        return json.dumps(response)
    else:
        return json.dumps(Message.get_invalid_request_payload())

@assist.action('test.run')
def test_runs(number):
    #score = req['queryResult']['parameters']['number']
    # flask_request_json = flask_request.get_json()
    number = int(number)
    match_params = Helper.get_match_params(request)
    
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']

    match_id = ''
    if match_params['username'] == '':
        match_id = request['queryResult']['parameters']['match_id']
    else:
        match_id = match_params['match_id']
    match_status = MatchDatabase.get_match_status(match_id)
    user_text = request['queryResult']['queryText']
    response =''
    session = request['session']
    intent_name = request['queryResult']['intent']['displayName']
    action = request['queryResult']['action']
    SESSION_ID = session.rpartition('/')[2] 
    
    if match_status == 'live':
        chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
        response = ActionListener.ball_action_listener(number,match_id,chat_id,request,SESSION_ID,action,intent_name,user_text,response) 
        match= MatchDatabase.get_match_document(match_id)
        send_live_data(match)
    elif match_status == 'resume':
        print('********** Resume *************')
        print("match_id:"+match_id)
        last_txn = ActionListener.get_last_txn_from_history(match_id,match_status)
        response = last_txn['response']
    print(response)
    return json.dumps(response)

@assist.action('test.out.bat.bowlerchange')
def test_out_bowler_change(bowler):
    test_bowler_change(bowler)

@assist.action('test.run.bowlerchange')
def test_bowler_change(bowler):
    print("==> Request in test_bowler_change:")
    print(request)
    match_params = Helper.get_match_params(request)
    # flask_request_json = flask_request.get_json()
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']

    return ActionListener.bowler_change_action_listener(bowler,match_params['match_id'],chat_id)

@assist.action('test.out.batsmanchange')
def test_batsman_change(batsman):
    match_params = Helper.get_match_params(request)
   
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']
    return ActionListener.batsman_change_action_listener(batsman,match_params['match_id'],chat_id)


@assist.action('test.out.runout.strikerOrNonstriker')
def test_out_runout_strikerOrNonstriker(batsman_type):
    match_params = Helper.get_match_params(request)
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    match_id = match_params['match_id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']
    MatchDatabase.update_batsman_out(batsman_type,match_id)

   
@assist.action('test.out.runout.runs')
def test_out_runout_runs(run):
   out_common("runout",request,int(run))

@assist.action('test.out.runout.noball.runs')
def test_out_runout_noball_runs(run):
   out_common("noball_runout",request,int(run))

@assist.action('test.out.runout.wide.runs')
def test_out_runout_wide_runs(run):
   out_common("wide_runout",request,int(run))

#TODO
#test.out.hitwicket
#test.out.lbw
def out_common(out_type,request,run=None):
    #we are not updating strike batsman here
    match_params = Helper.get_match_params(request)
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    match_id = match_params['match_id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']
    response =  ActionListener.out_action_listener(match_id,chat_id,request,out_type,run=run)

    #websocket response start
    match= MatchDatabase.get_match_document(match_id)
    send_live_data(match)
    #websocket response end

    return response

@assist.action('test.out.fielder')
def test_out_fielder_update(fielder):
    print("===> Request in test_out_fielder_update: ")
    print(request)
    match_params = Helper.get_match_params(request)
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']
    
    return ActionListener.out_fielder_update_listner(match_params['match_id'],chat_id,request,fielder)
    

@assist.action('test.out.stumping')
def test_out_stumping():
    return out_common("stumping",request)

@assist.action('test.out.caught')
def test_out_caught():
    return out_common("caught",request)
   
@assist.action('test.out.bowled')
def test_out_bowled():
    return out_common("bowled",request)

@assist.action('test.wide.run')
def wide_with_number(number):
    #test.wide_with_number
    match_params = Helper.get_match_params(request)
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    match_id = match_params['match_id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']

    response =  ActionListener.wide_with_number_action_listener(number,match_params['match_id']) 
    #websocket response start
    match= MatchDatabase.get_match_document(match_id)
    send_live_data(match)
    #websocket response end

    return response

@assist.action('test.noball.run')   
def noball_with_number(number):
    #test.noball_with_number
    match_params = Helper.get_match_params(request)
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    match_id = match_params['match_id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']

    response =  ActionListener.noball_with_number_number_action_listener(number,match_params['match_id']) 

     #websocket response start
    match= MatchDatabase.get_match_document(match_id)
    send_live_data(match)
    #websocket response end

    return response

@assist.action('match.toss.won')  
def match_toss(team_name,decision,team1,team2,overs):
    #match.toss
    print('******Request message start*********')
    print(request)
    print('******Request message end*********')
    
    match_params = Helper.get_match_params(request)
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']
    response = ActionListener.toss_action_listener(team1,team2,decision,team_name,overs,match_params['match_id'],match_params['start_date']) 
    return response

@assist.action('match.team1players')  
def match_team1_players(team1,team1_players):
    #match.team1players
    match_params = Helper.get_match_params(request)
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']
    team1_players_list = team1_players.split()
    team1_players_list = [x.strip(' ') for x in team1_players_list]
    
    MatchDatabase.add_players(team1,team1_players_list,match_params['match_id'])
    return 'heak'  

@assist.action('match.team2players')  
def match_team2_players(team2,team2_players):
    #match.team2players
    match_params = Helper.get_match_params(request)
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']
    team2_players_list = team2_players.split()
    team2_players_list = [x.strip(' ') for x in team2_players_list]

    MatchDatabase.add_players(team2,team2_players_list,match_params['match_id'])
    return 'heak'

@assist.action('match.opening.batsman') 
def match_opening_batsmen(opening_batsmen):
    #match.opening-batsman
    match_params = Helper.get_match_params(request)
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']
    #TODO : get list directly from diagflow
    opening_batsmen_list = opening_batsmen.split(' and ')
    opening_batsmen_list = [x.strip(' ') for x in opening_batsmen_list]
    print(opening_batsmen_list)
    
    res = ActionListener.update_on_strike_batsmen_listener(opening_batsmen_list,match_params['match_id'],chat_id)
    return res

@assist.action('test.ball') 
def test_ball(bowler):
    match_params = Helper.get_match_params(request)
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']
    MatchDatabase.update_current_bowler(bowler,match_params['match_id'])
    return 'heak'
   
@assist.action('test.ball.strikechange')
def test_ball_strikechange():
    match_params = Helper.get_match_params(request)
    MatchDatabase.strike_change(match_params['match_id'])
    return json.dumps(Message.general_message("strike changed"))

@assist.action('match.pause') 
def match_pause():
    match_params = Helper.get_match_params(request)
    chat_id = request['originalDetectIntentRequest']['payload']['data']['chat']['id']
    if 'exit' in match_params:
        TelegramHelper.remove_keyboard(chat_id)
        return match_params['exit']
    return ActionListener.pause_match_listner(match_params['match_id'],match_params['username'],request)

@assist.action('match.resume') 
def match_resume(scorer_id):
    match_id = Helper.get_match_params(request)['match_id']
    scorer_username = scorer_id
    if scorer_username[:1]=='@':
        scorer_username = scorer_username[1:]
    scorer_id = MatchDatabase.userid_from_username(scorer_username,'telegram')
    session_client = dialogflow_v2.SessionsClient()
    last_txn = ActionListener.get_last_txn_from_history(scorer_id)
    SESSION_ID = last_txn['SESSION_ID']
    intent_name = last_txn['intent_name']
    user_text = last_txn['user_text']
    input_context = MatchDatabase.get_input_context_from_intent_name(intent_name)
    parameters = dialogflow_v2.types.struct_pb2.Struct()
    
    MatchDatabase.update_match_id(scorer_id,match_id)
    parameters["match_id"] = match_id
    context_1 = dialogflow_v2.types.context_pb2.Context(
    name="projects/cricbot-qegqqr/agent/sessions/"+SESSION_ID+"/contexts/"+input_context,
    lifespan_count=2,
    parameters=parameters
    )

    query_params_1 = {"contexts": [context_1]}

    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)

    text_input = dialogflow_v2.types.TextInput(text=user_text, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow_v2.types.QueryInput(text=text_input)
    # context=dialogflow_v2.types.context_pb2.Context(name='projects/cricbot-qegqqr/agent/sessions/b630631f-19ae-396b-9477-6ba29737d8e8/contexts/ball')
    # contexts_input = dialogflow_v2.types.QueryParameters(contexts=[context_1])

    #set match_status == 'resume'
    MatchDatabase.set_match_status_resume(match_id,"resume")
    try:
        response = session_client.detect_intent(session=session, query_input= query_input,query_params = query_params_1)
    except InvalidArgument:
        raise

    print("Query text:", response.query_result.query_text)
    print("Detected intent:", response.query_result.intent.display_name)
    print("Detected intent confidence:", response.query_result.intent_detection_confidence)
    print("Fulfillment text:", response.query_result.fulfillment_text)
    return Message.get_resume_payload()

@socketio.on('connect')
def handle_message():
    print('websocket connected')

def send_live_data(match):
    print('Sending live data.................... ')
    socketio.emit('live', dumps(match))
    
if __name__ == '__main__':
    # app.run(port=5222,debug=True)
    port = int(os.environ.get('PORT', 33507))
    socketio.run(app,port=port,debug=True)
