from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError

class MongoDBClient:
    def __init__(self, connection_string, database_name):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self._connect()

    def _connect(self):
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database_name]
            self.client.admin.command('ismaster')
            print(f"Successfully connected to MongoDB database: {self.database_name}")
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise
        except ServerSelectionTimeoutError as e:
            print(f"Server selection timeout error: {e}")
            raise

    def insert_document(self, collection_name, document):
        if self.db is None:
            raise ConnectionError("Not connected to MongoDB.")
        try:
            collection = self.db[collection_name]
            collection.insert_one(document)
            print(f"Document inserted into collection '{collection_name}'")
        except OperationFailure as e:
            print(f"Failed to insert document: {e}")
            raise

    def close_connection(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed")