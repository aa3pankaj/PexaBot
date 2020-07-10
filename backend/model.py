from jsondiff import diff
from bson.objectid import ObjectId
from bson.json_util import dumps
import json

class DiffHistoryModel(dict):
    """
    A simple model that wraps mongodb document, 
    Also creates a delta collection for document revision tracking
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    def __diff_update(self):
        print("******* ******************** in __diff_update ******************** ******")
        match_copy = self.collection.find_one({"_id": ObjectId(self._id)})
        print("\n")
        print(match_copy)
        print("\n")
        print(self)
        diff_object = diff(dumps(match_copy),dumps(self),load=True, dump=True)
        print("\n")
        print(diff_object)
        print("******* ******************** out __diff_update ******************** ******")
        return diff_object
        
    def save(self):
        #TODO add code to create new revision doc in _delta_collection
    
        if not self._id:
            self.collection.insert_one(self)
        else:
            diff = self.__diff_update()
            self.collection.update(
                { "_id": ObjectId(self._id) }, self)
            
            _delta_collection_name = "_delta"+"_"+self.name
            _delta_collection = self.db_object[_delta_collection_name]
            _delta_collection.insert_one({ "collection_name": self.name,
                                                "document_id" : self._id,
                                                "diff": diff,
                                                "_version": _delta_collection.count()+1,
                                                "reason":"update"
            }
            )
            print("done")

    def reload(self):
        if self._id:
            self.update(self.collection\
                    .find_one({"_id": ObjectId(self._id)}))

    def remove(self):
        if self._id:
            self.collection.remove({"_id": ObjectId(self._id)})
            self.clear()