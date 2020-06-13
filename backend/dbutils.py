
import pymongo
import json
from message import Message
from bson.objectid import ObjectId
from bson.json_util import dumps
import os
MONGO_KEY = os.getenv('MONGO_KEY')
client = pymongo.MongoClient(MONGO_KEY)
db = client["cric"]


class MatchDatabase:
    @staticmethod
    def delete_live_matches_of_user(match_id):
        #delete all pause or live matches
        result = db.matches.remove(
            {'$and': [{'$or': [{"status": "live"}, {"status": "pause"}]}, {"match_id": match_id}]})

    @staticmethod
    def get_live_match_info(match_id):
        match = MatchDatabase.get_match_document(match_id)
        current_batting_team = match["current_batting_team"]
        strike_batsman = match['strike_batsman']
        non_strike_batsman = match['non_strike_batsman']
        current_batting_team = match['current_batting_team']
        runs_scored = match[current_batting_team]['runs_scored']
        running_over = match['running_over']
        ball_number = match['ball_number']
        over_status = None
        if "over_status" in match[current_batting_team]:
            print(match[current_batting_team]['over_status'])
            if str(running_over) in match[current_batting_team]['over_status']:
                over_status = match[current_batting_team]['over_status'][str(running_over)]

        return {"current_batting_team":current_batting_team,"runs_scored":runs_scored,"running_over":running_over,"ball_number":ball_number,
                "strike_batsman":strike_batsman,"non_strike_batsman":non_strike_batsman,"over_status":over_status }


    @staticmethod
    def update_batsman_out(batsman_type,match_id):
        match = MatchDatabase.get_match_document(match_id)
        current_batting_team = match["current_batting_team"]
        strike_batsman = match['strike_batsman']
        non_strike_batsman = match['non_strike_batsman']

        if batsman_type== 'strike batsman':
            db.matches.update_one({'_id': match['_id']}, {'$set': {
                                current_batting_team+".batting."+strike_batsman+".status": False}})
        else:
            db.matches.update_one({'_id': match['_id']}, {'$set': {
                                current_batting_team+".batting."+non_strike_batsman+".status": False}})


    @staticmethod
    def update_over_status(match, over_number, ball_number, score_type, run):
        db.matches.update_one({'_id': match['_id']}, {'$push': {
                              match["current_batting_team"]+".over_status"+"."+over_number+"."+ball_number:{score_type: run}}})

    @staticmethod
    def get_available_batsman(match_id):
        match = MatchDatabase.get_match_document(match_id)
        current_batting_team = match["current_batting_team"]
        player_list = match[current_batting_team]['did_not_bat']
        print('batsman list from **get_available_batsman** ')
        print(json.dumps(player_list))
        return player_list

    @staticmethod
    def get_available_bowlers(match_id):
        player_with_overs = []
        match = MatchDatabase.get_match_document(match_id)
        current_bowling_team = match["current_bowling_team"]
        player_list = match[current_bowling_team]['players']
        bowling_dict = ''
        if "bowling" in match[current_bowling_team]:
            bowling_dict = match[current_bowling_team]['bowling']
        for x in player_list:
            if bowling_dict != '' and x in bowling_dict and "balls" in bowling_dict[x]:
                player_with_overs.append(
                    {"name": x, "overs": str(bowling_dict[x]["balls"]/6)})
            else:
                player_with_overs.append({"name": x, "overs": 0})

        print('bowler list from **get_available_bowlers** ')
        print(json.dumps(player_with_overs))
        return player_with_overs

    @staticmethod
    def get_current_ball_number(match_id):
        match = db.matches.find_one(
            {'$and': [{"status": "live"}, {"match_id": match_id}]})
        return match['ball_number']

    @staticmethod
    def set_match_status_end(match_id):
        db.matches.update_one({'$and': [{'$or': [{"status": "live"}, {"status": "pause"}]}, {
                              "match_id": match_id}]}, {'$set': {"status": "end"}})

    @staticmethod
    def update_match_id(scorer_id, new_match_id):
        match = MatchDatabase.get_match_document(scorer_id)
        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {"match_id": new_match_id}})

    @staticmethod
    def get_match_status(match_id):
        match = db.matches.find_one({'$and': [{'$or': [{"status": "live"}, {
                                    "status": "pause"}, {"status": "resume"}]}, {"match_id": match_id}]})
        return match['status']
          

    @staticmethod
    def set_match_status_resume(match_id, status):
        print("** In -->set_match_status_resume() **")
        print("-"+match_id+"-")
        match = MatchDatabase.get_match_document(match_id)
        print(dumps(match))
        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {"status": status}})

    @staticmethod
    def set_match_status_live(match_id, status):
        match = MatchDatabase.get_resume_match_document(match_id)
        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {"status": status}})

    @staticmethod
    def get_input_context_from_intent_name(intent_name):
        dialogflow_links = db.user_links.distinct("dialogflow")
        return dialogflow_links[0][intent_name]

    @staticmethod
    def get_last_txn(match_id):
        print("** In -->get_last_txn() **")
        # match1= db.matches.find_one({'$and':[{'$or':[{"status" : "live"}, {"status" : "pause"}]},{"match_id": match_id}]})
        # print(dumps(match1))
        match = db.matches.find_one({'$and': [{'$or': [{"status": "live"}, {"status": "pause"}]}, {
                                    "match_id": match_id}]}, {'txn': {'$slice': -1}})
        print(dumps(match))
        print("** Out -->get_last_txn() **")
        return match['txn'][0]

    @staticmethod
    def get_resume_match_document(match_id):
        #not used
        match = db.matches.find_one(
            {'$and': [{"status": "resume"}, {"match_id": match_id}]})
        return match

    @staticmethod
    def get_live_match_document(match_id):
        match = db.matches.find_one(
            {'$and': [{"status": "live"}, {"match_id": match_id}]})
        return match

    @staticmethod
    def push_history(match_id, SESSION_ID, action, intent_name, user_text, response):
        match = MatchDatabase.get_live_match_document(match_id)
        # db.matches.update_one({'_id':match['_id']},{'$set':{"status":"live"}})
        db.matches.update_one({'_id': match['_id']}, {'$push': {"txn": {
                              "SESSION_ID": SESSION_ID, "action": action, "intent_name": intent_name, "user_text": user_text, "response": response}}})

    @staticmethod
    def pause_match(match_id):
        match = db.matches.find_one(
            {'$and': [{"status": "live"}, {"match_id": match_id}]})
        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {"status": "pause"}})
        return True

    @staticmethod
    def get_match_document_by_id(id):
        match = db.matches.find_one({"_id": ObjectId(id)})
        return match

    @staticmethod
    def get_match_document(match_id):
        # improve query by having live matches document
        #match = db.matches.findOne({'$query': {'match_id':match_id}, '$orderby': {'_id' : -1}})
        match = db.matches.find_one(
            {'$and': [{'$or': [{"status": "live"}, {"status": "pause"}]}, {"match_id": match_id}]})
        return match

    @staticmethod
    def innings_complete_doc_refresh(match_id):
        #match = db.matches.find_one({'match_id':match_id})
        match = MatchDatabase.get_match_document(match_id)

        current_batting_team = match['current_batting_team']
        current_bowling_team = match['current_bowling_team']
        db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {'running_innings': 1}})

        running_innings = MatchDatabase.get_match_document(match_id)['running_innings']
        if running_innings != 2:
            db.matches.update_one({"_id": match['_id']}, {'$set': {"current_batting_team": current_bowling_team, "current_bowling_team": current_batting_team,
                                                                   "running_over": -1, "ball_number": 0, "non_strike_batsman": "", "strike_batsman": "", "current_bowler": ""}})

    @staticmethod
    def update_teams(team1, team2, decision, toss_team, overs, start_date, match_id):
        current_batting_team = ''
        current_bowling_team = ''
        innings1_team = ''
        innings2_team = ''
        print(str(team1)+" "+str(team2)+" "+str(decision)+" " +
              str(toss_team)+" "+str(overs)+" "+str(start_date)+" "+str(match_id))

        if decision == 'batting':
            current_batting_team = toss_team
            innings1_team = toss_team
            current_bowling_team = team1 if team1 != toss_team else team2
            innings2_team = current_bowling_team
        else:
            current_bowling_team = toss_team
            innings2_team = toss_team
            current_batting_team = team1 if team1 != toss_team else team2
            innings1_team = current_batting_team

        _id = db.matches.insert({'match_id': match_id, "match_number": db.matches.count()+1, 
                                                       "ball_number": 0,
                                                        "running_over": -1, 
                                                        "total_overs": overs, 
                                                        "running_innings": 0, 
                                                        "status": "live", 
                                                        "start_date": start_date, 
                                                        team1: {"players": [], "runs_scored": 0, "balls_faced": 0, "wickets_fallen": 0},
                                                        team2: {"players": [], "runs_scored": 0, "balls_faced": 0, "wickets_fallen": 0}, 
                                                        "current_bowling_team": current_bowling_team, 
                                                        "current_batting_team": current_batting_team, 
                                                        "innings1_team": innings1_team, 
                                                        "innings2_team": innings2_team, 
                                                        "toss": [toss_team, decision]})
        return _id

    @staticmethod
    def update_match_document(run, match_id):
        
        match = MatchDatabase.get_match_document(match_id)
        current_ball_number = match['ball_number']
        ball_number = match['ball_number']
        current_batting_team = match["current_batting_team"]
        refresh_needed = False
        runs_scored = ''
        running_over = match['running_over']
        strike_batsman = ''
        non_strike_batsman = ''
        current_bowler = ''

        if ball_number == 6:
            current_ball_number = 1
        else:
            current_ball_number = ball_number+1

        print("ball_number="+str(ball_number))
        print("current_ball_number="+str(current_ball_number))
        print("match['running_over']=" + str(match['running_over']))

        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {"ball_number": current_ball_number}})
        db.matches.update_one({'_id': match['_id']}, {'$inc': {
                              current_batting_team+".runs_scored": int(run), current_batting_team+".balls_faced": 1}})
        #db.matches.update_one( {'_id':match['_id']},{ '$inc':{current_batting_team+".balls_faced":1}})
 
        #test-comment
        # if current_ball_number == 1:
        #     db.matches.update_one({'_id': match['_id']}, {
        #                           '$inc': {'running_over': 1}})

        match = MatchDatabase.get_match_document(match_id)
        runs_scored = match[current_batting_team]['runs_scored']
        running_over = match['running_over']
        strike_batsman = match['strike_batsman']
        non_strike_batsman = match['non_strike_batsman']
        current_bowler = match['current_bowler']

        MatchDatabase.update_over_status(match, str(
            running_over), str(current_ball_number), "run", run)

        if current_ball_number == 6:
            if match['running_over']+1 == match["total_overs"]:
                refresh_needed = True
                print("refresh_needed due to all overs")
                print(refresh_needed)
                MatchDatabase.innings_complete_doc_refresh(match_id)
        running_innings = MatchDatabase.get_match_document(match_id)['running_innings']
       
        print("running_innings:")
        print(running_innings)
        if refresh_needed:
            if running_innings == 2:
                return {"type": "end","response":"end"}
            return {"type": "change","response":"change"}
        if current_ball_number == 6 and running_over != -1:
            return {"type": "ask_next_bowler", "response": Message.next_bowler_ask_payload(current_batting_team, running_over, current_ball_number, runs_scored, strike_batsman, non_strike_batsman)}
        return Message.get_update_match_document_payload(current_batting_team, running_over, current_ball_number, runs_scored, strike_batsman, non_strike_batsman, current_bowler)

    @staticmethod
    def link_users(bot_user, platform_user, source):
        print("****** linking ******** "+bot_user+" with "+platform_user)
        try:
            user = db.players.insert_one(
                {"user_id": bot_user, "run": 0, "balls": 0, "strike_rate": 0, "avg": 0})
            print(str(user))
            db.user_links.update_one(
                {}, {'$set': {source+"."+platform_user: bot_user}})
            return True
        except Exception as e:
            return False

    @staticmethod
    def add_players(team_name, players_list, match_id):
        match = MatchDatabase.get_match_document(match_id)
        print(type(match['_id']))
        x = db.matches.find_one({'_id': match['_id']})
        print(dumps(x))
        db.matches.update({'_id': match['_id']}, {'$set': {
                          team_name+".players": players_list, team_name+".did_not_bat": players_list}})
            
        


    @staticmethod
    def user_already_exist(bot_user):
        #user = db.players.find( { bot_user : { '$exists' : 1 } } )
        print("searching... " + bot_user)
        user = db.players.find_one({"user_id": bot_user})
        if user:
            print("Found user!")
            return True
        else:
            return False

    @staticmethod
    def update_on_strike_batsmen(opening_batsmen_list, match_id):
        print("opening pair:")
        print(opening_batsmen_list)

        match = MatchDatabase.get_match_document(match_id)
        current_batting_team = match['current_batting_team']

        #db.matches.update_one( {'_id':match['_id']},{ '$set':{"strike_batsman":opening_batsmen_list[0],"non_strike_batsman":opening_batsmen_list[1]}})
        db.matches.update_one({'_id': match['_id']}, {
                              '$push': {current_batting_team+".batting_order": opening_batsmen_list[0]}})
        db.matches.update_one({'_id': match['_id']}, {
                              '$push': {current_batting_team+".batting_order": opening_batsmen_list[1]}})

        db.matches.update_one({'_id': match['_id']}, {'$set': {"strike_batsman": opening_batsmen_list[0],
                                                               "non_strike_batsman": opening_batsmen_list[1],
                                                               current_batting_team+".batting."+opening_batsmen_list[0]+".4s": 0,
                                                               current_batting_team+".batting."+opening_batsmen_list[0]+".6s": 0,
                                                               current_batting_team+".batting."+opening_batsmen_list[0]+".runs": 0,
                                                               current_batting_team+".batting."+opening_batsmen_list[0]+".balls": 0,
                                                               current_batting_team+".batting."+opening_batsmen_list[0]+".status": True,
                                                               current_batting_team+".batting."+opening_batsmen_list[1]+".4s": 0,
                                                               current_batting_team+".batting."+opening_batsmen_list[1]+".6s": 0,
                                                               current_batting_team+".batting."+opening_batsmen_list[1]+".runs": 0,
                                                               current_batting_team+".batting."+opening_batsmen_list[1]+".balls": 0,
                                                               current_batting_team+".batting."+opening_batsmen_list[1]+".status": True,
                                                               current_batting_team+".batting."+opening_batsmen_list[0]+".strike_rate": 0.0,
                                                               current_batting_team+".batting."+opening_batsmen_list[1]+".strike_rate": 0.0
                                                               }})
        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+opening_batsmen_list[0]+".6s":0}})
        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+opening_batsmen_list[0]+".runs":0}})
        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+opening_batsmen_list[0]+".balls":0}})
        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+opening_batsmen_list[0]+".status":True}})

        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+opening_batsmen_list[1]+".4s":0}})
        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+opening_batsmen_list[1]+".6s":0}})
        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+opening_batsmen_list[1]+".runs":0}})
        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+opening_batsmen_list[1]+".balls":0}})
        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+opening_batsmen_list[1]+".status":True}})
        # removing opening batsmen from match.team_name.did_not_bat
        db.matches.update_one({'_id': match['_id']}, {
                              '$pull': {current_batting_team+".did_not_bat": opening_batsmen_list[0]}})
        db.matches.update_one({'_id': match['_id']}, {
                              '$pull': {current_batting_team+".did_not_bat": opening_batsmen_list[1]}})

        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+opening_batsmen_list[0]+".strike_rate":0.0}})
        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+opening_batsmen_list[1]+".strike_rate":0.0}})

    @staticmethod
    def update_current_bowler(current_bowler, match_id):
        match = MatchDatabase.get_match_document(match_id)
        current_bowling_team = match['current_bowling_team']
        ball_number = match['ball_number']
        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {"current_bowler": current_bowler}})
        
        #test-code
        if ball_number == 0 or ball_number == 6:
            db.matches.update_one({'_id': match['_id']}, {
                                  '$inc': {'running_over': 1}})


        if "bowling" not in match[current_bowling_team] or (current_bowler not in match[current_bowling_team]['bowling']):
            db.matches.update_one({'_id': match['_id']}, {'$set': {current_bowling_team+".bowling."+current_bowler+".runs": 0,
                                                                   current_bowling_team+".bowling."+current_bowler+".balls": 0,
                                                                   current_bowling_team+".bowling."+current_bowler+".wickets": 0,
                                                                   current_bowling_team+".bowling."+current_bowler+".wides": 0,
                                                                   current_bowling_team+".bowling."+current_bowler+".noballs": 0,
                                                                   current_bowling_team+".bowling."+current_bowler+".economy_rate": 0.0
                                                                   }})
            # db.matches.update_one({'_id':match['_id']},{'$set':{current_bowling_team+".bowling."+current_bowler+".balls":0}})
            # db.matches.update_one({'_id':match['_id']},{'$set':{current_bowling_team+".bowling."+current_bowler+".wickets":0}})
            # db.matches.update_one({'_id':match['_id']},{'$set':{current_bowling_team+".bowling."+current_bowler+".wides":0}})
            # db.matches.update_one({'_id':match['_id']},{'$set':{current_bowling_team+".bowling."+current_bowler+".noballs":0}})
            # db.matches.update_one({'_id':match['_id']},{'$set':{current_bowling_team+".bowling."+current_bowler+".economy_rate":0.0}})

    @staticmethod
    def update_sr_and_er(match, run, type= None):
        print("updating sr_and_er... ")
        strike_batsman = match["strike_batsman"]
        current_batting_team = match["current_batting_team"]
        current_bowling_team = match["current_bowling_team"]
        current_bowler = match["current_bowler"]
        
        batsman_runs = match[current_batting_team]['batting'][strike_batsman]['runs']
        
        batsman_balls = match[current_batting_team]['batting'][strike_batsman]['balls']+1
        strike_rate = (batsman_runs/batsman_balls)*100
        strike_rate = str(round(strike_rate, 2))
    
        db.matches.update_one({'_id': match['_id']}, {'$set': {
                              current_batting_team+".batting."+strike_batsman+".strike_rate": strike_rate}})

        # update overs in the formula instead of balls
        bowler_runs_conceded = match[current_bowling_team]['bowling'][current_bowler]['runs']+run
        bowler_balls = match[current_bowling_team]['bowling'][current_bowler]['balls']+1

        economy_rate = (bowler_runs_conceded/bowler_balls)*6
        economy_rate = str(round(economy_rate, 2))
        print("economy_rate:")
        print(economy_rate)
        db.matches.update_one({'_id': match['_id']}, {'$set': {
                              current_bowling_team+".bowling."+current_bowler+".economy_rate": economy_rate}})

    @staticmethod
    def update_players_stats(run, match_id):
        match = MatchDatabase.get_match_document(match_id)
        # strike_batsman = db.matches.find_one({'match_id':"test"})['strike_batsman']
        # current_bowler = db.matches.find_one({'match_id':"test"})['current_bowler']
        # current_batting_team = db.matches.find_one({'match_id':"test"})['current_batting_team']

        strike_batsman = match['strike_batsman']
        current_bowler = match['current_bowler']
        current_batting_team = match['current_batting_team']
        current_bowling_team = match['current_bowling_team']

        if run == 6:
            db.matches.update_one({'_id': match['_id']}, {
                                  '$inc': {current_batting_team+".batting."+strike_batsman+".6s": 1}})
        elif run == 4:
            db.matches.update_one({'_id': match['_id']}, {
                                  '$inc': {current_batting_team+".batting."+strike_batsman+".4s": 1}})
        db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {current_batting_team+".batting."+strike_batsman+".runs": run}})
        db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {current_batting_team+".batting."+strike_batsman+".balls": 1}})

        db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {current_bowling_team+".bowling."+current_bowler+".runs": run}})
        db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {current_bowling_team+".bowling."+current_bowler+".balls": 1}})
        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+strike_batsman+".status":True}})
        # batsman_runs = match[current_batting_team]['batting'][strike_batsman]['runs']+run
        # batsman_balls = match[current_batting_team]['batting'][strike_batsman]['balls']+1
        # strike_rate = (batsman_runs/batsman_balls)*100
        # strike_rate = str(round(strike_rate, 2))
        # db.matches.update_one({'_id':match['_id']},{'$set':{current_batting_team+".batting."+strike_batsman+".strike_rate":strike_rate}})

        # #update overs in the formula instead of balls
        # bowler_runs_conceded = match[current_bowling_team]['bowling'][current_bowler]['runs']+run
        # bowler_balls = match[current_bowling_team]['bowling'][current_bowler]['balls']+1

        # economy_rate = (bowler_runs_conceded/bowler_balls)*6
        # economy_rate = str(round(economy_rate, 2))
        # db.matches.update_one({'_id':match['_id']},{'$set':{current_bowling_team+".bowling."+current_bowler+".economy_rate":economy_rate}})
        MatchDatabase.update_sr_and_er(match, run)
        MatchDatabase.update_personnel_stats(
            strike_batsman, current_bowler, run)

    @staticmethod
    def update_personnel_stats(strike_batsman, current_bowler, run):
        if MatchDatabase.user_already_exist(strike_batsman):
            if run == 6:
                db.players.update_one({'user_id': strike_batsman}, {
                                      '$inc': {"batting.6s": 1}})
            elif run == 4:
                db.players.update_one({'user_id': strike_batsman}, {
                                      '$inc': {"batting.4s": 1}})

            db.players.update({'user_id': strike_batsman}, {
                              '$inc': {"batting.runs": run}})
            db.players.update({'user_id': strike_batsman}, {
                              '$inc': {"batting.balls": 1}})

            db.players.update({'user_id': current_bowler}, {
                              '$inc': {"bowling.runs": run}})
            db.players.update({'user_id': current_bowler}, {
                              '$inc': {"bowling.balls": 1}})

    @staticmethod
    def strike_change(match_id):
        match = MatchDatabase.get_match_document(match_id)
        strike_batsman = match['strike_batsman']
        non_strike_batsman = match['non_strike_batsman']
        db.matches.update_one({'_id': match['_id']}, {'$set': {
                              "strike_batsman": non_strike_batsman, "non_strike_batsman": strike_batsman}})

    @staticmethod
    def get_most_runs_user():
        #user_detail = db.players.find().sort({"run":-1})
        user_detail = db.players.find_one(sort=[("batting.runs", -1)])
        print(str(user_detail))
        # print(user_detail['user_id'],flush=True)
        # print(user_detail['run'],flush=True)
        # print(user_detail['balls'])
        # rint(str(user_details))
        return user_detail

    @staticmethod
    def userid_from_username(username, source):

        # TODO fix user_links design
        source_users = db.user_links.distinct(source)
        print("###############")
        user_id = source_users[0][username]
        #user = db.user_links.find({source:{}})
        print("user_id that we got:"+user_id)
        return user_id

    @staticmethod
    def user_stats(user_id):
        print("*** searching user with id "+user_id)
        user = db.players.find_one({'user_id': user_id})
        return user

    @staticmethod
    def batsman_change(batsman, match_id):
        #strike_batsman = db.matches.find_one({'match_id':"test"})['strike_batsman']
        # if over ended send bowler change message else normal
        # innings refresh? update match doc, update status of strike batsman to out, wickets fallen update,
        match = MatchDatabase.get_match_document(match_id)
        #match = db.matches.find_one({'match_id':"test"})
        current_ball_number = match['ball_number']
        current_batting_team = match["current_batting_team"]

        runs_scored = match[current_batting_team]['runs_scored']
        running_over = match['running_over']

        non_strike_batsman = match['non_strike_batsman']
        strike_batsman = match['strike_batsman']
        current_bowler = match['current_bowler']
        
        if match[current_batting_team]['batting'][strike_batsman]["status"]==False:
            db.matches.update_one({'_id': match['_id']}, {
                              '$set': {"strike_batsman": batsman}})
            strike_batsman = batsman
            
        elif match[current_batting_team]['batting'][non_strike_batsman]["status"] == False:
            db.matches.update_one({'_id': match['_id']}, {
                              '$set': {"non_strike_batsman": batsman}})
            non_strike_batsman = batsman
           

        db.matches.update_one({'_id': match['_id']}, {
                              '$push': {current_batting_team+".batting_order": batsman}})


        
        # strike_batsman = batsman

        # strike_batsman = db.matches.find_one({'match_id':"test"})['strike_batsman']
        # current_bowler = db.matches.find_one({'match_id':"test"})['current_bowler']
        # current_batting_team = db.matches.find_one({'match_id':"test"})['current_batting_team']

        current_bowling_team = match['current_bowling_team']

        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {current_batting_team+".batting."+batsman+".4s": 0}})

        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {current_batting_team+".batting."+batsman+".6s": 0}})
        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {current_batting_team+".batting."+batsman+".runs": 0}})
        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {current_batting_team+".batting."+batsman+".balls": 0}})
        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {current_batting_team+".batting."+batsman+".strike_rate": 0.0}})

        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {current_batting_team+".batting."+batsman+".status": True}})
        # removing batsman from did_not_bat
        db.matches.update_one({'_id': match['_id']}, {
                              '$pull': {current_batting_team+".did_not_bat": batsman}})

        if current_ball_number == 6 and running_over != -1:
            return {"type": "ask_next_bowler", "response": Message.next_bowler_ask_payload(current_batting_team, running_over, current_ball_number, runs_scored, strike_batsman, non_strike_batsman)}
        return {"type": "next", "response": Message.get_update_match_document_payload(current_batting_team, running_over, current_ball_number, runs_scored, strike_batsman, non_strike_batsman, current_bowler)}

    @staticmethod
    def update_wide(run, match_id):
        # extra++, update team score
        match = MatchDatabase.get_match_document(match_id)
        #match = db.matches.find_one({'match_id':"test"})
        current_batting_team = match["current_batting_team"]
        current_bowling_team = match["current_bowling_team"]
        current_bowler = match["current_bowler"]
        ball_number = match['ball_number']
        current_ball_number= ''
        if ball_number == 6:
            current_ball_number = 1
        else:
            current_ball_number = ball_number

        running_over = match['running_over']

        # team_update
        db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {current_batting_team+'.runs_scored': int(run+1)}})

        # bowler
        db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {current_bowling_team+".bowling."+current_bowler+".wides": 1}})
        db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {current_bowling_team+".bowling."+current_bowler+".runs": int(run+1)}})

        MatchDatabase.update_over_status(match, str(
            running_over), str(current_ball_number), "wide", int(run))

        #er and sr
        MatchDatabase.update_sr_and_er(match, run)

        if run % 2 != 0:
            MatchDatabase.strike_change(match_id)

    @staticmethod
    def update_noball(run, match_id):
        # TODO extra++
        match = MatchDatabase.get_match_document(match_id)
        current_batting_team = match["current_batting_team"]
        current_bowling_team = match["current_bowling_team"]
        current_bowler = match["current_bowler"]
        strike_batsman = match["strike_batsman"]
        ball_number = match['ball_number']
        current_ball_number= ''

        if ball_number == 6:
            current_ball_number = 1
        else:
            current_ball_number = ball_number
        running_over = match['running_over']

        # team_update
        db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {current_batting_team+'.runs_scored': int(run+1)}})

        # batsman_update
        db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {current_batting_team+".batting."+strike_batsman+".runs": run,
                                       current_batting_team+".batting."+strike_batsman+".balls": 1}})
        # db.matches.update_one({'_id': match['_id']}, {
        #                       '$inc': {current_batting_team+".batting."+strike_batsman+".balls": 1}})

        # bowler_update
        db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {current_bowling_team+".bowling."+current_bowler+".noballs": 1,
                                       current_bowling_team+".bowling."+current_bowler+".runs": int(run+1)}})
        # db.matches.update_one({'_id': match['_id']}, {
        #                       '$inc': {current_bowling_team+".bowling."+current_bowler+".runs": int(run+1)}})

        MatchDatabase.update_over_status(match, str(
            running_over), str(current_ball_number), "noball", int(run))

        #er and sr
        MatchDatabase.update_sr_and_er(match, run)

        if run % 2 != 0:
            MatchDatabase.strike_change(match_id)


    @staticmethod
    def out_common(match_id, fielder=None, out_type=None):
        match = MatchDatabase.get_match_document(match_id)

        # #er and sr
        # MatchDatabase.update_sr_and_er(match, 0)

        current_ball_number = ''
        ball_number = match['ball_number']
        current_batting_team = match["current_batting_team"]
        current_bowling_team = match["current_bowling_team"]
        refresh_needed = False

        runs_scored = ''
        strike_batsman = match['strike_batsman']
        non_strike_batsman = match['non_strike_batsman']
        current_bowler = match['current_bowler']
        
        print("out type:"+out_type)
        if ball_number == 6:
            current_ball_number = 1
        else:
            current_ball_number = ball_number+1

        print("ball_number="+str(ball_number))
        print("current_ball_number="+str(current_ball_number))
        print("match['running_over']=" + str(match['running_over']))

        # batsman
        #for runout status change is from other intent

        #shifted 1 layer down for other cases
        if out_type == 'bowled':
            db.matches.update_one({'_id': match['_id']}, {
                                '$set': {current_batting_team+".batting."+strike_batsman+".status": False}})
            db.matches.update_one({'_id': match['_id']}, {
                                '$inc': {current_batting_team+".batting."+strike_batsman+".balls": 1}})
            #er and sr
            MatchDatabase.update_sr_and_er(match, 0)
    

       
        if out_type!='wide_runout' and out_type!='noball_runout':
            db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {current_bowling_team+".bowling."+current_bowler+".wickets": 1}
                                     })
             # bowler, bowler runs updated in below layer
            db.matches.update_one({'_id': match['_id']}, {'$inc': {
                                current_bowling_team+".bowling."+current_bowler+".balls": 1}})
    
        db.matches.update_one({'_id': match['_id']}, {
                              '$inc': {current_batting_team+".wickets_fallen": 1}})

        #db.matches.update_one( {'match_id':"test"},{ '$inc':{current_batting_team+".runs_scored":int(run)}})
        if out_type != 'runout' and out_type!='wide_runout' and out_type!='noball_runout':
            db.matches.update_one({'_id': match['_id']}, {
                                '$inc': {current_batting_team+".balls_faced": 1}})
        running_over = db.matches.find_one({'$and': [{'$or': [{"status": "live"}, {
                                           "status": "pause"}]}, {"match_id": match_id}]})["running_over"]
        runs_scored = match[current_batting_team]['runs_scored']
        #fix this for noball
        db.matches.update_one({'_id': match['_id']}, {'$push': {current_batting_team+".fall_of_wickets": {
                              "batsman": strike_batsman, "over_number": running_over, "ball_number": current_ball_number, "team_score": runs_scored}}})

        if fielder != None:
            if match[current_batting_team]['batting'][strike_batsman]["status"]==False:
              
                db.matches.update_one({'_id': match['_id']}, {'$set': {
                                  current_batting_team+".batting."+strike_batsman+".out_fielder": fielder}})
            elif match[current_batting_team]['batting'][non_strike_batsman]["status"] == False:
                db.matches.update_one({'_id': match['_id']}, {'$set': {
                                  current_batting_team+".batting."+non_strike_batsman+".out_fielder": fielder}})

           
        if out_type == 'bowled':
            db.matches.update_one({'_id': match['_id']}, {'$set': {
                                  current_batting_team+".batting."+strike_batsman+".out_type": out_type}})
            db.matches.update_one({'_id': match['_id']}, {'$set': {
                                  current_batting_team+".batting."+strike_batsman+".out_bowler": current_bowler}})

        # checing if all wickets fallen, if yes then refresh innings required.
        did_not_bat = match[current_batting_team]['did_not_bat']
        if len(did_not_bat) == 0:
            refresh_needed = True
            print("refresh_needed due to all out")
            MatchDatabase.innings_complete_doc_refresh(match_id)

        MatchDatabase.update_over_status(match, str(
            running_over), str(current_ball_number), "out", 0)

        #test-comment
        # if current_ball_number == 1:
        #     db.matches.update_one({'_id': match['_id']}, {
        #                           '$inc': {'running_over': 1}})
        #elif
        if current_ball_number == 6 and refresh_needed == False:
            if match['running_over']+1 == match["total_overs"]:
                refresh_needed = True
                print("refresh_needed due to all overs and out")
                MatchDatabase.innings_complete_doc_refresh(match_id)

        if refresh_needed:
            if db.matches.find_one({'_id': match['_id']})["running_innings"] == 2:
                return {"type": "end"}
            return {"type": "change","response":"change"}

        return {"type": "ask_next_batsman", "response": Message.next_batsman_ask_payload()}

    @staticmethod
    def out_update(match_id, out_type,run=None):
        # TODO Out with run out
        match = MatchDatabase.get_match_document(match_id)
        current_batting_team = match["current_batting_team"]
        current_bowling_team = match["current_bowling_team"]
        strike_batsman = match['strike_batsman']
        non_strike_batsman = match['non_strike_batsman']
        current_bowler = match['current_bowler']


        if out_type != 'runout' and out_type!='wide_runout' and out_type!='noball_runout':
            db.matches.update_one({'_id': match['_id']}, {'$set': {
                                current_batting_team+".batting."+strike_batsman+".out_type": out_type,
                                current_batting_team+".batting."+strike_batsman+".out_bowler": current_bowler
                                }})
            db.matches.update_one({'_id': match['_id']}, {
                                '$set': {current_batting_team+".batting."+strike_batsman+".status": False}})
            db.matches.update_one({'_id': match['_id']}, {
                                '$inc': {
                                current_batting_team+".batting."+strike_batsman+".balls": 1,
                                current_batting_team+".balls_faced":1
                                }})
            #er and sr
            MatchDatabase.update_sr_and_er(match,0)
           
        else:
            print("runs that we got in out_update with runout:")
            print(run)
            if out_type != "wide_runout":
                db.matches.update_one({'_id': match['_id']}, {'$inc': {
                                current_batting_team+".batting."+strike_batsman+".runs": run,
                                current_batting_team+".batting."+strike_batsman+".balls": 1}})
            if run != None:
                db.matches.update_one({'_id': match['_id']}, {'$inc': {
                                    current_batting_team+".runs_scored": run+1}})
                if out_type == "wide_runout" or out_type == "noball_runout":
                    db.matches.update_one({'_id': match['_id']}, {'$inc': {
                                    current_bowling_team+".bowling."+current_bowler+".runs": run+1,
                                    }})
                    if out_type == "wide_runout":
                        db.matches.update_one({'_id': match['_id']}, {
                                '$inc': {current_bowling_team+".bowling."+current_bowler+".wides": 1}})
                    else:
                        db.matches.update_one({'_id': match['_id']}, {
                                '$inc': {current_bowling_team+".bowling."+current_bowler+".noballs": 1}})
                    

                    bowler_runs_conceded = match[current_bowling_team]['bowling'][current_bowler]['runs']+run
                    bowler_balls = match[current_bowling_team]['bowling'][current_bowler]['balls']+1

                    economy_rate = (bowler_runs_conceded/bowler_balls)*6
                    economy_rate = str(round(economy_rate, 2))
                    print("economy_rate:")
                    print(economy_rate)
                    db.matches.update_one({'_id': match['_id']}, {'$set': {
                                        current_bowling_team+".bowling."+current_bowler+".economy_rate": economy_rate}})
                    MatchDatabase.update_sr_and_er(match,run,type=out_type)
                     
                else:
                    db.matches.update_one({'_id': match['_id']}, {'$inc': {
                                    current_batting_team+".balls_faced": 1
                                    }})
                    db.matches.update_one({'_id': match['_id']}, {'$inc': {
                                    current_bowling_team+".bowling."+current_bowler+".runs": run}})
                    MatchDatabase.update_sr_and_er(match,run,type=out_type)


            if match[current_batting_team]['batting'][strike_batsman]["status"]==False:
               db.matches.update_one({'_id': match['_id']}, {'$set': {
                                current_batting_team+".batting."+strike_batsman+".out_type": out_type,
                                current_batting_team+".batting."+strike_batsman+".out_bowler": current_bowler
                                }})
            
            elif match[current_batting_team]['batting'][non_strike_batsman]["status"] == False:
                db.matches.update_one({'_id': match['_id']}, {'$set': {
                                current_batting_team+".batting."+non_strike_batsman+".out_type": out_type,
                                current_batting_team+".batting."+non_strike_batsman+".out_bowler": current_bowler
                                }})

