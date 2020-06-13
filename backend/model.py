
import pymongo
import json
from message import Message
from bson.objectid import ObjectId
from bson.json_util import dumps
import os
MONGO_KEY = os.getenv('MONGO_KEY')
client = pymongo.MongoClient(MONGO_KEY)
db = client["cric"]

class BotDatabase:

    def get_match_document(match_id)
        match = db.matches.find_one(
            {'$and': [{'$or': [{"status": "live"}, {"status": "pause"}]}, {"match_id": match_id}]})
        return match

    def __init__(self,match_id): 
        self.match = self.get_match_document(match_id)
        self.current_batting_team = match.current_batting_team
        self.ball_number = match.ball_number
        self.current_batting_team = match.current_batting_team
        self.current_bowling_team = match.current_bowling_team
        self.runs_scored = match[self.current_batting_team].runs_scored
        self.running_over = match.running_over
        self.strike_batsman = match.strike_batsman
        self.non_strike_batsman = match.non_strike_batsman
        self.current_bowler = match.current_bowler
        self.refresh_required = False
        self.over_status = None

    def get_live_match_info(self):
        
        if "over_status" in self.match[self.current_batting_team]:
            print(self.match[self.current_batting_team]['over_status'])

            if str(self.running_over) in self.match[self.current_batting_team]['over_status']:
                self.over_status = self.match[self.current_batting_team]['over_status'][str(self.running_over)]

        return {
               "current_batting_team":self.current_batting_team,
               "runs_scored":self.runs_scored,
               "running_over":self.running_over,
               "ball_number":self.ball_number,
               "strike_batsman":self.strike_batsman,
               "non_strike_batsman":self.non_strike_batsman,
               "over_status":self.over_status 
               }


    def update_teams(team1, team2, decision, toss_team, overs, start_date):
      
        print(str(team1)+" "+str(team2)+" "+str(decision)+" " +
              str(toss_team)+" "+str(overs)+" "+str(start_date)+" "+str(match_id))

        if decision == 'batting':
            self.current_batting_team = toss_team
            self.innings1_team = toss_team
            self.current_bowling_team = team1 if team1 != toss_team else team2
            self.innings2_team = self.current_bowling_team
        else:
            self.current_bowling_team = toss_team
            self.innings2_team = toss_team
            self.current_batting_team = team1 if team1 != toss_team else team2
            self.innings1_team = self.current_batting_team

        _id = db.matches.insert({'match_id': match_id, "match_number": db.matches.count()+1, 
                                                       "ball_number": 0,
                                                        "running_over": -1, 
                                                        "total_overs": overs, 
                                                        "running_innings": 0, 
                                                        "status": "live", 
                                                        "start_date": start_date, 
                                                        team1: {"players": [], "runs_scored": 0, "balls_faced": 0, "wickets_fallen": 0},
                                                        team2: {"players": [], "runs_scored": 0, "balls_faced": 0, "wickets_fallen": 0}, 
                                                        "current_bowling_team": self.current_bowling_team, 
                                                        "current_batting_team": self.current_batting_team, 
                                                        "innings1_team": self.innings1_team, 
                                                        "innings2_team": self.innings2_team, 
                                                        "toss": [toss_team, decision]})
        return _id

       