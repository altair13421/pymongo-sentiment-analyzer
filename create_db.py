import pymongo

def createDB():
    db_name='register_users'
    # test_client = pymongo.MongoClient('mongodb://localhost:27017/')
    client = pymongo.MongoClient("mongodb+srv://admin:AYiafjctmADP7Vot@cluster0.lmml9uf.mongodb.net/?retryWrites=true&w=majority")
    # shanadb = test_client[db_name]
    # db = client.test
    shanadb = client[db_name]

    