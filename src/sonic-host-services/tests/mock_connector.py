class RedisSingleton:
    "Introduced to verify the DB updates made by the scripts"
    __instance = None
    data = {}
    data["CONFIG_DB"] = {}
    data["STATE_DB"] = {}
    
    @staticmethod 
    def getInstance():
       """ Static access method. """
       if RedisSingleton.__instance == None:
          RedisSingleton()
       return RedisSingleton.__instance
    
    def __init__(self):
       if RedisSingleton.__instance != None:
          raise Exception("This class is a singleton!")
       else:
          RedisSingleton.__instance = self
          
class MockConnector(object):
    STATE_DB = None
    Redis = RedisSingleton.getInstance()

    def __init__(self, host):
        pass

    def connect(self, db_id):
        pass

    def get(self, db_id, key, field):
        return MockConnector.Redis.data.get(db_id, "").get(key, "").get(field, "")

    def keys(self, db_id, pattern):
        match = pattern.split('*')[0]
        ret = []
        for key in MockConnector.Redisdata.keys():
            if match in key:
                ret.append(key)
        return ret

    def get_all(self, db_id, key):
        return MockConnector.Redis.data.get(db_id, {}).get(key, {})
    
    def set(self, db_id, key, field, value, blocking=True):
        MockConnector.Redis.data[db_id][key][field] = value
    
    def hmset(self, db_id, key, hash):
        MockConnector.Redis.data[db_id][key] = hash
        
    def exists(self, db_id, key):
        if key in MockConnector.Redis.data[db_id]:
            return True
        else:
            return False


