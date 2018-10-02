import pickle
import sys

targetFile = sys.argv[1]

with open(targetFile, 'rb') as databaseFile:
    database = pickle.load(databaseFile)

with open(targetFile+'.txt', 'wt', encoding='utf-8') as outputFile:
    outputFile.write(str(database))
