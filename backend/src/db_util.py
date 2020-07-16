
import pymongo
import json
from message import Message
from bson.objectid import ObjectId
import os
from bson.json_util import dumps
from message import Message
from model.pymongo_model import SimpleModel, DiffHistoryModelV1

MONGO_KEY = os.getenv('MONGO_KEY')
client = pymongo.MongoClient(MONGO_KEY)
db = client["cric"]

class Match(DiffHistoryModelV1):
    db_object = db
    collection = db.matches  
    delta_collection_name = "_delta_matches"   #name of the collection where revisions will be stored
class Player(SimpleModel):
    collection = db.players

class BotDatabase:

    def __init__(self,match_id):
        self.match_id = match_id
        self.match = Match({"_id":self.__get_match_document_id(match_id)})
        self.match.reload()
        self.current_batting_team = self.match.current_batting_team
        self.current_bowling_team = self.match.current_bowling_team

    @classmethod
    def get_match_document_by_id(cls,id):
        match = db.matches.find_one({"_id": ObjectId(id)})
        return match

    @classmethod
    def get_live_match_document(cls,match_id):
        doc = db.matches.find_one(
            {'$and': [{"status": "live"}, {"match_id": match_id}]})
        return doc

    @classmethod
    def get_match_document(cls,match_id):
        doc = db.matches.find_one(
            {'$and': [{'$or': [{"status": "live"}, {"status": "pause"}]}, {"match_id": match_id}]})
        return doc

    def __get_match_document_id(self,match_id):
        doc = db.matches.find_one(
            {'$and': [{'$or': [{"status": "live"}, {"status": "pause"}]}, {"match_id": match_id}]})
        return doc['_id']

    def __update_over_status(self,score_type, run=0, ball_number = None):
       if ball_number == None:
           ball_number = self.match.ball_number
       if str(self.match.running_over) not in self.match[self.current_batting_team]['over_status']:
           self.match[self.current_batting_team]['over_status'].update({str(self.match.running_over):{}})
       
       self.match[self.current_batting_team]['over_status'][str(self.match.running_over)].setdefault(str(ball_number),[]).append({score_type: run})

    def __innings_complete_doc_refresh(self):
        """
        Refreshing common variables in doc like current_ball_number,Strike_batsman if innings over
        """
        self.match.running_innings += 1
        if self.match.running_innings != 2:
         
            self.match.current_batting_team , self.match.current_bowling_team =  self.match.current_bowling_team , self.match.current_batting_team 
            self.match.running_over = -1
            self.match.ball_number = 0
            self.match.non_strike_batsman = ""
            self.match.strike_batsman = ""
            self.match.current_bowler = ""

    def get_live_match_info(self):
        runs_scored = self.match[self.current_batting_team]['runs_scored']
        over_status = {}
        if "over_status" in self.match[self.current_batting_team] and str(self.match.running_over) in self.match[self.current_batting_team]["over_status"]:
            over_status = self.match[self.current_batting_team]['over_status'][str(self.match.running_over)]

        return {
               "current_batting_team":self.current_batting_team,
               "runs_scored":int(runs_scored),
               "wickets_fallen":self.match[self.current_batting_team]['wickets_fallen'],
               "running_over":self.match.running_over,
               "ball_number":self.match.ball_number,
               "strike_batsman":self.match.strike_batsman,
               "non_strike_batsman":self.match.non_strike_batsman,
               "over_status":over_status,
               "strike_batsman_runs":self.match[self.match.current_batting_team]['batting'][self.match.strike_batsman]['runs'],
               "non_strike_batsman_runs":self.match[self.match.current_batting_team]['batting'][self.match.non_strike_batsman]['runs'],
               "strike_batsman_balls":self.match[self.match.current_batting_team]['batting'][self.match.strike_batsman]['balls'],
               "non_strike_batsman_balls":self.match[self.match.current_batting_team]['batting'][self.match.non_strike_batsman]['balls']
               }

    @classmethod
    def update_teams(cls,team1, team2, decision, toss_team, overs, start_date,match_id):
      
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

        match = Match( {'match_id': match_id, 
                            "match_number": db.matches.count()+1, 
                            "start_date": start_date,
                            "status": "live", 
                            "undo_count":1,
                            "ball_number": 0,
                            "running_over": -1,
                            "total_overs": overs, 
                            "running_innings": 0, 
                            "strike_batsman":'',
                            "non_strike_batsman":'',
                            'current_bowler':'',
                            team1: {"players": [],"did_not_bat":[],
                                    "batting_order":[],"batting":{},
                                    "bowling":{},"fall_of_wickets":[],
                                    "runs_scored": 0,"balls_faced": 0, 
                                    "wickets_fallen": 0,"over_status":{}},
                            team2: {"players": [], "did_not_bat":[],
                                    "batting_order":[],"batting":{},
                                    "bowling":{},"fall_of_wickets":[],
                                    "runs_scored": 0,"balls_faced": 0,
                                    "wickets_fallen": 0,"over_status":{}}, 
                            "current_bowling_team": current_bowling_team, 
                            "current_batting_team": current_batting_team, 
                            "innings1_team": innings1_team, 
                            "innings2_team": innings2_team, 
                            "toss": [toss_team, decision],
                            "txn":[]
                                })
        match.save()
        return match._id

    def add_players(self,team_name, players_list):
        self.match[team_name]['players'] = players_list
        self.match[team_name]['did_not_bat'] = players_list
        self.match.save()
    
    def current_bowler_update(self,current_bowler):
        self.match.current_bowler = current_bowler
        current_bowling_team = self.match.current_bowling_team

        if self.match.ball_number == 6:
            self.strike_change()
        
        #updating ball number if start of match or next over
        if self.match.ball_number == 0 or self.match.ball_number == 6:
            self.match.running_over += 1
            self.match.ball_number = 0

        if self.match.current_bowler not in self.match[self.current_bowling_team]['bowling']:
            self.match[current_bowling_team]['bowling'].update( {current_bowler: {
                    "runs":0,
                    "balls":0,
                    "wickets":0,
                    "wides":0,
                    "noballs":0,
                    "economy_rate":0.0
                    }
                    } )
        self.match['undo_count'] = 1
        self.match.save()
                                                       
    def strike_change(self):
        self.match.non_strike_batsman,self.match.strike_batsman = self.match.strike_batsman,self.match.non_strike_batsman

    def sr_and_er_update(self,type= None):
        batsman_runs = self.match[self.match.current_batting_team]['batting'][self.match.strike_batsman]['runs'] 
        batsman_balls = self.match[self.match.current_batting_team]['batting'][self.match.strike_batsman]['balls']
        strike_rate = 0.0
        if batsman_balls != 0:
            strike_rate = (batsman_runs/batsman_balls)*100
            strike_rate = str(round(strike_rate, 2))

        self.match[self.match.current_batting_team]['batting'][self.match.strike_batsman]['strike_rate'] = strike_rate

        # TODO update overs in the formula instead of balls
        bowler_runs_conceded = self.match[self.match.current_bowling_team]['bowling'][self.match.current_bowler]['runs']
        bowler_balls = self.match[self.match.current_bowling_team]['bowling'][self.match.current_bowler]['balls']

        economy_rate = 0.0
        if bowler_balls != 0:
            economy_rate = (bowler_runs_conceded/bowler_balls)*6
            economy_rate = str(round(economy_rate, 2))

        self.match[self.match.current_bowling_team]['bowling'][self.match.current_bowler]['economy_rate'] = economy_rate
      
    @classmethod
    def user_already_exist(cls,bot_user):
        #user = db.players.find( { bot_user : { '$exists' : 1 } } )
        print("searching... " + bot_user)
        user = db.players.find_one({"user_id": bot_user})
        if user:
            print("Found user!")
            return True
        else:
            return False

    def on_strike_batsmen_update(self,batsman,batsman_type):

        self.match[self.current_batting_team]['batting_order'].append(batsman)    
        self.match[self.current_batting_team]['batting'].update({ batsman: {'4s': 0 }})
        self.match[self.current_batting_team]['batting'][batsman].update( {'6s': 0 })
        self.match[self.current_batting_team]['batting'][batsman].update( {'runs': 0 })
        self.match[self.current_batting_team]['batting'][batsman].update( {'balls': 0 })
        self.match[self.current_batting_team]['batting'][batsman].update( {'status': True })
        self.match[self.current_batting_team]['batting'][batsman].update( {'strike_rate': 0.0 })
        self.match[self.current_batting_team]['batting'][batsman].update( {'out_fielder': '' })
        # removing opening batsmen from match.team_name.did_not_bat
        self.match[self.current_batting_team]['did_not_bat'].remove(batsman)

        if batsman_type == "strike_batsman":
             self.match.strike_batsman = batsman 
        else:
            self.match.non_strike_batsman = batsman
        
        self.match.save()

    def personnel_stats_update(self,run):
        if BotDatabase.user_already_exist(self.match.strike_batsman):
            if run == 6:
                db.players.update_one({'user_id': self.match.strike_batsman}, {
                                      '$inc': {"batting.6s": 1}})
            elif run == 4:
                db.players.update_one({'user_id': self.match.strike_batsman}, {
                                      '$inc': {"batting.4s": 1}})

            db.players.update({'user_id': self.match.strike_batsman}, {
                              '$inc': {"batting.runs": run}})
            db.players.update({'user_id': self.match.strike_batsman}, {
                              '$inc': {"batting.balls": 1}})

            db.players.update({'user_id': self.match.current_bowler}, {
                              '$inc': {"bowling.runs": run}})
            db.players.update({'user_id': self.match.current_bowler}, {
                              '$inc': {"bowling.balls": 1}})

    def players_stats_update(self,run):

        if run == 6:
            self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['6s'] += 1
        elif run == 4:
            self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['4s'] += 1

        self.match[self.match.current_batting_team]['batting'][self.match.strike_batsman]['runs'] += run
        self.match[self.match.current_batting_team]['batting'][self.match.strike_batsman]['balls'] += 1
        self.match[self.match.current_bowling_team]['bowling'][self.match.current_bowler]['runs'] += run
        self.match[self.match.current_bowling_team]['bowling'][self.match.current_bowler]['balls'] += 1

        self.personnel_stats_update(run)


    def run_update(self,run):
        """
        This method updates runs in team & players records in current match, 
        match can end here or innings can change
        """

        refresh_needed = False   
        if self.match.ball_number == 0:
            self.match.ball_number = 1
        else:
            self.match.ball_number += 1

        #updating for "This over" status on ui
        self.__update_over_status("run", run)

        self.match[self.current_batting_team]['runs_scored'] += int(run)
        self.match[self.current_batting_team]['balls_faced'] += 1

        #er and sr update
        self.sr_and_er_update()

        if run%2!=0:
            self.strike_change()
        
        if self.match.ball_number == 6:
            if self.match.running_over+1 == self.match.total_overs:
                refresh_needed = True
                self.__innings_complete_doc_refresh()

        self.match["undo_count"] = 1
        self.match.save()

        if refresh_needed:
            if self.match.running_innings == 2:
                return {"type": "end","response":"end"}
            return {"type": "change","response":"change"}

        if self.match.ball_number == 6 and self.match.running_over != -1:
            return {"type": "ask_next_bowler", 
                    "response": Message.next_bowler_ask_payload(self.current_batting_team, 
                                                                self.match.running_over, 
                                                                self.match.ball_number, 
                                                                self.match[self.current_batting_team]['runs_scored'], 
                                                                self.match[self.current_batting_team]['wickets_fallen'], 
                                                                self.match.strike_batsman, 
                                                                self.match.non_strike_batsman)}

        return {"type":"next","response":Message.get_update_match_document_payload(self.current_batting_team, 
                                                        self.match.running_over, self.match.ball_number, 
                                                         self.match[self.current_batting_team]['runs_scored'], self.match.strike_batsman, 
                                                        self.match.non_strike_batsman, self.match.current_bowler)}


    def get_available_bowlers(self):
        #TODO dont send current bowler
        player_with_overs = []
        current_bowling_team = self.match.current_bowling_team
        player_list = self.match[current_bowling_team]['players']
        bowling_dict = {}
        if "bowling" in self.match[current_bowling_team]:
            bowling_dict = self.match[current_bowling_team]['bowling']
        for x in player_list:
            if bowling_dict and x in bowling_dict and "balls" in bowling_dict[x]:
                player_with_overs.append(
                    {"name": x, "overs": str(bowling_dict[x]["balls"]/6)})
            else:
                player_with_overs.append({"name": x, "overs": 0})
        return player_with_overs

    def get_available_batsman(self):
        player_list = self.match[self.current_batting_team]['did_not_bat']
        print('batsman list from **get_available_batsman** ')
        print(json.dumps(player_list))
        return player_list

    def wide_update(self,run):
        #TODO # extra++
        local_ball_number = self.match.ball_number

        #handling case of wide on first ball of over, so that this wide is recorded in current over.
        if self.match.ball_number == 0:
            local_ball_number = 1

        # team_update
        self.match[self.current_batting_team]['runs_scored'] += (run+1)
    
        # bowler
        self.match[self.current_bowling_team]['bowling'][self.match.current_bowler]['wides'] += 1
        self.match[self.current_bowling_team]['bowling'][self.match.current_bowler]['runs'] += (run+1)

        self.__update_over_status("wide", int(run), ball_number=local_ball_number)

        #er and sr
        self.sr_and_er_update()

        if run % 2 != 0:
            self.strike_change()

        self.match["undo_count"] = 1
        self.match.save()

    def noball_update(self,run):
        # TODO update extras

        #handling case of wide on first ball of over here, so that this wide is recorded in current over.
        local_ball_number = self.match.ball_number
        if self.match.ball_number == 0:
            local_ball_number = 1

        # team_update
        self.match[self.current_batting_team]['runs_scored'] += (run+1)

        # batsman_update
        self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['balls'] += 1
        self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['runs'] += run
        
        # bowler_update
        self.match[self.current_bowling_team]['bowling'][self.match.current_bowler]['noballs'] += 1
        self.match[self.current_bowling_team]['bowling'][self.match.current_bowler]['runs'] += (run+1)
       
        self.__update_over_status("noball", int(run), ball_number=local_ball_number)

        #er and sr
        self.sr_and_er_update()

        if run % 2 != 0:
            self.strike_change()

        self.match["undo_count"] = 1
        self.match.save()

    def delete_live_matches_of_user(self):
        result = db.matches.remove(
            {'$and': [{'$or': [{"status": "live"}, {"status": "pause"}]}, {"match_id": self.match_id}]})

    @classmethod
    def set_match_status(cls,match_id,from_status,to_status):
        print('updating match status from '+from_status +" to "+to_status)
        match = db.matches.find_one(
                    {'$and': [{"status": from_status}, {"match_id": match_id}]})
        if match != None:
            db.matches.update_one({'_id': match['_id']}, {
                                '$set': {"status": to_status}})
            print('Success')
            return True
        print('Failed') 
        return False

    @classmethod
    def get_match_status(cls,match_id):
        match = db.matches.find_one({'$and': [{'$or': [{"status": "live"}, {
                                    "status": "pause"}, {"status": "resume"}]}, {"match_id": match_id}]})
        return match['status']

    
    def out_without_fielder(self,out_type):
        """
        This method is for bowled,hitwicket,lbw actions, this is the last commit for these actions
        match can end here, or innings can change
        """
        refresh_needed = False
        #live data update
        if self.match.ball_number == 0:
            self.match.ball_number = 1
        else:
            self.match.ball_number += 1

        #team update
        self.match[self.current_batting_team]['balls_faced'] +=1
        self.match[self.current_batting_team]['wickets_fallen'] +=1
        self.match[self.current_batting_team]['fall_of_wickets'].append({
                              "batsman": self.match.strike_batsman, 
                              "over_number": self.match.running_over, 
                              "ball_number": self.match.ball_number, 
                              "team_score": self.match[self.current_batting_team]['runs_scored']})


        #batsman update
        self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['status'] = False
        self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['balls'] += 1

        #bowler update
        self.match[self.current_bowling_team]['bowling'][self.match.current_bowler]['balls'] += 1
        self.match[self.current_bowling_team]['bowling'][self.match.current_bowler]['wickets'] += 1

        #over status update
        self.__update_over_status("out")
        self.sr_and_er_update()
        
        did_not_bat = self.match[self.current_batting_team]['did_not_bat']
        
        if len(did_not_bat) == 0 or (self.match.ball_number == 6 and self.match.running_over+1 == self.match.total_overs):
            refresh_needed = True
            print("refresh_needed due to all out or all overs with all out")
            self.__innings_complete_doc_refresh()

        self.match["undo_count"] = 2
        self.match.save()

        if refresh_needed:
            if self.match.running_innings == 2:
                return {"type": "end"}
            return {"type": "change","response":"change"}

        return {"type": "ask_next_batsman", "response": Message.next_batsman_ask_payload()}

    def out_with_fielder(self,out_type):
        """
        This method is for catch_out, out_fielder_update() method is called in the next transaction
        """
        #live data update
        if self.match.ball_number == 0:
            self.match.ball_number = 1
        else:
            self.match.ball_number += 1
    
        #team update
        self.match[self.current_batting_team]['balls_faced'] +=1
        self.match[self.current_batting_team]['wickets_fallen'] +=1
        self.match[self.current_batting_team]['fall_of_wickets'].append({
                              "batsman": self.match.strike_batsman, 
                              "over_number": self.match.running_over, 
                              "ball_number": self.match.ball_number, 
                              "team_score": self.match[self.current_batting_team]['runs_scored']})


        #batsman update
        self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['status'] = False
        self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['balls'] += 1

        #bowler update
        self.match[self.current_bowling_team]['bowling'][self.match.current_bowler]['balls'] += 1
        self.match[self.current_bowling_team]['bowling'][self.match.current_bowler]['wickets'] += 1

        #over status update
        self.__update_over_status("out")
        self.sr_and_er_update()

        self.match.save()


    #for runout, strike or non strike bastsman update
    def runout_batsman_out_update(self,batsman_type):

        if batsman_type== 'strike batsman':
            self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['status'] = False
            
        else:
            self.match[self.current_batting_team]['batting'][self.match.non_strike_batsman]['status'] = False
        self.match.save()

    def run_out_update(self,out_type,run):
    
        if self.match.ball_number==0:
            if out_type == 'runout_runs':
                self.match.ball_number = 1
        else:
            if out_type == 'runout_runs':
                self.match.ball_number += 1
                
        #team update
        if out_type != "runout_runs":
            self.match[self.current_batting_team]['runs_scored'] += (run+1)
            if out_type == "runout_noball":
                self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['runs'] += (run)
                self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['balls'] += 1
            self.match[self.current_bowling_team]['bowling'][self.match.current_bowler]['runs'] += (run)

        else:
            self.match[self.current_batting_team]['runs_scored'] += run
            self.match[self.current_batting_team]['balls_faced'] += 1

            self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['runs'] += (run)
            self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['balls'] += 1

            self.match[self.current_bowling_team]['bowling'][self.match.current_bowler]['runs'] += (run)
            self.match[self.current_bowling_team]['bowling'][self.match.current_bowler]['balls'] += 1

        self.personnel_stats_update(run)

        #over status update
        self.__update_over_status("out")
        self.sr_and_er_update()
        if run % 2 != 0:
            self.strike_change()

        self.match.save()

    def out_fielder_update(self,fielder):

        """
        This is the last commit for actions: catch_out, run_out,
        Match can end here, or innings can change
        """

        refresh_needed =False

        strike_batsman_data = self.match[self.current_batting_team]['batting'][self.match.strike_batsman]
        non_strike_batsman_data = self.match[self.current_batting_team]['batting'][self.match.non_strike_batsman]
        
        print(strike_batsman_data['status'])
        print(non_strike_batsman_data['status'])

        if strike_batsman_data['status'] == False:
            self.match[self.current_batting_team]['batting'][self.match.strike_batsman]['out_fielder'] = fielder
        elif non_strike_batsman_data['status'] == False:
            self.match[self.current_batting_team]['batting'][self.match.non_strike_batsman]['out_fielder'] = fielder

        did_not_bat = self.match[self.current_batting_team]['did_not_bat']
        
        if len(did_not_bat) == 0 or (self.match.ball_number == 6 and self.match.running_over+1 == self.match.total_overs):
            refresh_needed = True
            print("refresh_needed due to all out or overs complete")
            self.__innings_complete_doc_refresh()

        self.match["undo_count"] = 3
        self.match.save()

        if refresh_needed:
            if self.match.running_innings == 2:
                return {"type": "end"}
            return {"type": "change","response":"change"}
        return {"type": "ask_next_batsman", "response": Message.next_batsman_ask_payload()}

    def batsman_change(self,batsman):
        strike_batsman_data = self.match[self.current_batting_team]['batting'][self.match.strike_batsman]
        non_strike_batsman_data = self.match[self.current_batting_team]['batting'][self.match.non_strike_batsman]

        #live data update
        if strike_batsman_data['status']==False:
            self.match.strike_batsman = batsman
            
        elif non_strike_batsman_data["status"] == False:
            self.match.non_strike_batsman = batsman
           
        #team update
        self.match[self.current_batting_team]['batting_order'].append(batsman)

        #batsman update
        self.match[self.current_batting_team]['batting'].update({ batsman: {'4s': 0 }})
        self.match[self.current_batting_team]['batting'][batsman].update( {'6s': 0 })
        self.match[self.current_batting_team]['batting'][batsman].update( {'runs': 0 })
        self.match[self.current_batting_team]['batting'][batsman].update( {'balls': 0 })
        self.match[self.current_batting_team]['batting'][batsman].update( {'status': True })
        self.match[self.current_batting_team]['batting'][batsman].update( {'strike_rate': 0.0 })
        self.match[self.current_batting_team]['batting'][batsman].update( {'out_fielder': '' })

        # removing batsman from did_not_bat
        self.match[self.current_batting_team]['did_not_bat'].remove(batsman)

        self.match.save()

        if self.match.ball_number == 6 and self.match.running_over != -1:
            return {"type": "ask_next_bowler", "response": Message.next_bowler_ask_payload(self.current_batting_team, 
                                                           self.match.running_over, self.match.ball_number, 
                                                           self.match[self.current_batting_team]['runs_scored'], 
                                                           self.match[self.current_batting_team]['wickets_fallen'], 
                                                           self.match.strike_batsman, 
                                                           self.match.non_strike_batsman)}
        return {"type": "next", "response": Message.get_update_match_document_payload(self.current_batting_team, 
                                           self.match.running_over, self.match.ball_number,
                                           self.match[self.current_batting_team]['runs_scored'], 
                                           self.match.strike_batsman, self.match.non_strike_batsman, self.match.current_bowler)}


    @classmethod
    def link_users(cls,bot_user, platform_user, source):
        print("****** linking ******** "+bot_user+" with "+platform_user)
        try:
            user = db.players.insert_one(
                {"user_id": bot_user,"batting":{"runs": 0, "balls": 0,"strike_rate": 0, "avg": 0,"4s":0,"6s":0}})
            print(str(user))
            db.user_links.update_one(
                {}, {'$set': {source+"."+platform_user: bot_user}})
            return True
        except Exception as e:
            print(e)
            print("excpetion occurred")
            return False

    @classmethod
    def get_most_runs_user(cls):
        user_detail = db.players.find_one(sort=[("batting.runs", -1)])
        return user_detail
        
    @classmethod
    def update_match_id(cls,scorer_id, new_match_id):
        match = BotDatabase.get_match_document(scorer_id)
        db.matches.update_one({'_id': match['_id']}, {
                              '$set': {"match_id": new_match_id}})   
   
    @classmethod
    def userid_from_username(cls,username, source):
        # TODO fix user_links design
        source_users = db.user_links.distinct(source)
        user_id = None
        if username in source_users[0]:
            user_id = source_users[0][username]
        print("user_id that we got:"+str(user_id))
        return user_id

    @classmethod
    def user_stats(cls,user_id):
        print("*** searching user with id "+user_id)
        user = db.players.find_one({'user_id': user_id})
        return user

    @classmethod
    def push_history(cls,match_id, SESSION_ID, action, intent_name, user_text, response):
        match = BotDatabase.get_live_match_document(match_id)
        db.matches.update_one({'_id': match['_id'] }, 
                                                {'$push': 
                                                      {"txn": {
                                                                "SESSION_ID": SESSION_ID, 
                                                                "action": action, 
                                                                "intent_name": intent_name, 
                                                                "user_text": user_text, 
                                                                "response": response}
                                                      }
                                                })
    @classmethod
    def get_last_txn(cls,match_id):
        print("** In -->get_last_txn() **")
        match = db.matches.find_one({'$and': [{'$or': [{"status": "live"}, {"status": "pause"}]}, {
                                    "match_id": match_id}]}, {'txn': {'$slice': -1}})
        print(dumps(match))
        print("** Out -->get_last_txn() **")
        return match['txn'][0]

    def undo_match(self):
        undo_count = self.match["undo_count"]
        print("Running undo for " +str(undo_count) +" times")
        for i in range(undo_count):
            print(i)
            self.match.undo()

            
    
        




   


       