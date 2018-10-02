import pickle

DATABASE_PATH = ['./.database/database.pickle', './.database/database_selfharm_account.pickle'] #현재까지 수집한 전체 데이터베이스 (누적)

for i, databasePath in enumerate(DATABASE_PATH):
    with open(databasePath, 'wb') as databaseFile:
        dataNull = {}
        pickle.dump(dataNull,databaseFile)