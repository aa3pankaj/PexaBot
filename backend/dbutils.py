
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
    

   
                
