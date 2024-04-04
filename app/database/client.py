"""
from pymongo import MongoClient
from consts import DB_CONN_STRING

class MongoDBClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MongoDBClient, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, db_name=DB_NAME):
        self.connection_string = DB_CONN_STRING
        self.client = MongoClient(self.connection_string)
        #self.db = self.client[db_name]

    def get_db(self):
        return self.db
        """