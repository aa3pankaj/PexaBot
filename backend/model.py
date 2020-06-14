
import pymongo
import json
from message import Message
from bson.objectid import ObjectId
from bson.json_util import dumps
import os
from message import Message
MONGO_KEY = os.getenv('MONGO_KEY')
client = pymongo.MongoClient(MONGO_KEY)
db = client["cric"]

from bson import ObjectId



class Model(dict):
    """
    A simple model that wraps mongodb document
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    def save(self):
        if not self._id:
            self.collection.insert_one(self)
        else:
            self.collection.update(
                { "_id": ObjectId(self._id) }, self)

    def reload(self):
        if self._id:
            self.update(self.collection\
                    .find_one({"_id": ObjectId(self._id)}))

    def remove(self):
        if self._id:
            self.collection.remove({"_id": ObjectId(self._id)})
            self.clear()

class Match(Model):
    collection = db.matches
class Player(Model):
    collection = db.players


class BotDatabase:

    def __get_match_document_id(self,match_id):
        doc = db.matches.find_one(
            {'$and': [{'$or': [{"status": "live"}, {"status": "pause"}]}, {"match_id": match_id}]})
        return doc['_id']

    def __update_over_status(self,score_type, run):
       if str(self.match.running_over) not in self.match[self.current_batting_team]['over_status']:
           self.match[self.current_batting_team]['over_status'].update({str(self.match.running_over):[]})
       self.match[self.current_batting_team]['over_status'][str(self.match.running_over)].append({score_type: run})

    def __innings_complete_doc_refresh(self):

        self.match.running_innings += 1

        if self.match.running_innings != 2:
         
            self.match.current_batting_team , self.match.current_bowling_team =  self.match.current_bowling_team , self.match.current_batting_team 
            self.match.running_over = -1
            self.match.ball_number = 0
            self.match.non_strike_batsman = ""
            self.match.strike_batsman = ""
            self.match.current_bowler = ""

    def __init__(self,match_id):
        self.match_id = match_id
        self.match = Match({"_id":self.__get_match_document_id(match_id)})
        self.match.reload()
        self.current_batting_team = self.match.current_batting_team
        self.current_bowling_team = self.match.current_bowling_team

    def get_live_match_info(self):
        # if "over_status" in self.match[self.current_batting_team]:
            # if str(self.match.running_over) in self.match[self.current_batting_team]['over_status']:
            #     self.match.over_status = self.match[self.current_batting_team]['over_status'][str(self.match.running_over)]

        runs_scored = self.match[self.current_batting_team]['runs_scored']
        over_status = {}
        if "over_status" in self.match[self.current_batting_team] and str(self.match.running_over) in self.match[self.current_batting_team]["over_status"]:
            over_status = self.match[self.current_batting_team]['over_status'][str(self.match.running_over)]

        return {
               "current_batting_team":self.current_batting_team,
               "runs_scored":runs_scored,
               "running_over":self.match.running_over,
               "ball_number":self.match.ball_number,
               "strike_batsman":self.match.strike_batsman,
               "non_strike_batsman":self.match.non_strike_batsman,
               "over_status":over_status
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
        
        if self.match.ball_number == 0 or self.match.ball_number == 6:
            self.match.running_over += 1
        current_bowling_team = self.match.current_bowling_team
        if self.match.current_bowler not in self.match[current_bowling_team]['bowling']:
            print(self.match[current_bowling_team]['bowling'])
            self.match[current_bowling_team]['bowling'].update( {current_bowler: {
                    "runs":0,
                    "balls":0,
                    "wickets":0,
                    "wides":0,
                    "noballs":0,
                    "economy_rate":0.0
                    }
                    } )

        self.match.save()
                                                       
    def strike_change(self):
        self.match.non_strike_batsman,self.match.strike_batsman = self.match.strike_batsman,self.match.non_strike_batsman
        self.match.save()

    def sr_and_er_update(self,type= None):
        
        batsman_runs = self.match[self.match.current_batting_team]['batting'][self.match.strike_batsman]['runs'] 
        batsman_balls = self.match[self.match.current_batting_team]['batting'][self.match.strike_batsman]['balls']
        strike_rate = (batsman_runs/batsman_balls)*100
        strike_rate = str(round(strike_rate, 2))

        self.match[self.match.current_batting_team]['batting'][self.match.strike_batsman]['strike_rate'] = strike_rate

        # update overs in the formula instead of balls
        bowler_runs_conceded = self.match[self.match.current_bowling_team]['bowling'][self.match.current_bowler]['runs']
        bowler_balls = self.match[self.match.current_bowling_team]['bowling'][self.match.current_bowler]['balls']

        economy_rate = (bowler_runs_conceded/bowler_balls)*6
        economy_rate = str(round(economy_rate, 2))

        self.match[self.match.current_bowling_team]['bowling'][self.match.current_bowler]['economy_rate'] = economy_rate
        
    def user_already_exist(self,bot_user):
        #user = db.players.find( { bot_user : { '$exists' : 1 } } )
        print("searching... " + bot_user)
        user = db.players.find_one({"user_id": bot_user})
        if user:
            print("Found user!")
            return True
        else:
            return False

    def on_strike_batsmen_update(self,opening_batsmen_list):
        self.match[self.current_batting_team]['batting_order'].append(opening_batsmen_list[0])
        self.match[self.current_batting_team]['batting_order'].append(opening_batsmen_list[1])
        self.match.strike_batsman = opening_batsmen_list[0]
        self.match.non_strike_batsman = opening_batsmen_list[1]

        self.match[self.current_batting_team]['batting'].update({ opening_batsmen_list[0]: {'4s': 0 }})
        self.match[self.current_batting_team]['batting'][opening_batsmen_list[0]].update( {'6s': 0 })
        self.match[self.current_batting_team]['batting'][opening_batsmen_list[0]].update( {'runs': 0 })
        self.match[self.current_batting_team]['batting'][opening_batsmen_list[0]].update( {'balls': 0 })
        self.match[self.current_batting_team]['batting'][opening_batsmen_list[0]].update( {'status': False })
        self.match[self.current_batting_team]['batting'][opening_batsmen_list[0]].update( {'strike_rate': 0.0 })

        self.match[self.current_batting_team]['batting'].update({ opening_batsmen_list[1]: {'4s': 0 }})
        self.match[self.current_batting_team]['batting'][opening_batsmen_list[1]].update( {'6s': 0 })
        self.match[self.current_batting_team]['batting'][opening_batsmen_list[1]].update( {'runs': 0 })
        self.match[self.current_batting_team]['batting'][opening_batsmen_list[1]].update( {'balls': 0 })
        self.match[self.current_batting_team]['batting'][opening_batsmen_list[1]].update( {'status': False })
        self.match[self.current_batting_team]['batting'][opening_batsmen_list[1]].update( {'strike_rate': 0.0 })


        # removing opening batsmen from match.team_name.did_not_bat
        self.match[self.current_batting_team]['did_not_bat'].remove(opening_batsmen_list[0])
        self.match[self.current_batting_team]['did_not_bat'].remove(opening_batsmen_list[1])
        self.match.save()

    def personnel_stats_update(self,run):
        if self.user_already_exist(self.match.strike_batsman):
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

        self.sr_and_er_update(run)
        self.personnel_stats_update(run)

        self.match.save()


    def match_document_update(self,run):
        refresh_needed = False
        if self.match.ball_number == 6:
            self.match.ball_number = 1
        else:
            self.match.ball_number += 1

        #updating for this.over 
        self.__update_over_status("run", run)

        self.match[self.current_batting_team]['runs_scored'] += int(run)
        self.match[self.current_batting_team]['balls_faced'] += 1

        #refresh common variables in doc like current_ball_number,Strike_batsman if innings over
        if self.match.ball_number == 6:
            if self.match.running_over+1 == self.match.total_overs:
                refresh_needed = True
                self.__innings_complete_doc_refresh()

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
                                                                self.match.strike_batsman, 
                                                                self.match.non_strike_batsman)}

        return {"type":"next","response":Message.get_update_match_document_payload(self.current_batting_team, 
                                                        self.match.running_over, self.match.ball_number, 
                                                         self.match[self.current_batting_team]['runs_scored'], self.match.strike_batsman, 
                                                        self.match.non_strike_batsman, self.match.current_bowler)}


    def get_available_bowlers(self):
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

if __name__ == '__main__':
    
    bot = BotDatabase('@pankaj')
    # bot.update_teams('pankaj','ankur','batting','pankaj','3',234344)

    # bot.add_players('pankaj',['pankaj','tee','pratik'])

    # bot.update_match_document(3)
    # bot.update_current_bowler('pola')

    # _id = BotDatabase.update_teams('pankaj','ankur','batting','pankaj','3',234344,'@pankaj')
    # print (_id) 
    # bot.add_players('pankaj',['lola','pols','hela'])
    # bot.update_current_bowler("hola")
    # print(bot.get_available_bowlers())

    # bot.strike_change()
    # bot.on_strike_batsmen_update(['pankaj','pratik'])
    # bot.players_stats_update(3)

    # print(bot.get_live_match_info())
    bot.match_document_update(3)


   


       