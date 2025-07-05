import pandas as pd
from pymongo import MongoClient

class Sauvegarde:
    def __init__(self, data):
        self.df = pd.DataFrame(data)

    def to_csv(self, filename="books_data.csv"):
        self.df.to_csv(filename, index=False, encoding="utf-8")

    def to_mongo(self, db_name="tp_webscraping", collection="livres"):
        client = MongoClient("mongodb://localhost:27017/")
        db = client[db_name]
        db[collection].insert_many(self.df.to_dict("records"))
