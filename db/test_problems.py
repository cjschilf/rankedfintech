from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pprint

# MongoDB connection (TEMP PASSWORD)
uri = "mongodb+srv://colinschilf2025:SuA1Cw1uBUOMCcZq@rankedfintech.veidnzl.mongodb.net/?appName=RankedFintech"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["rankedfintech"]
problems_collection = db["problems"]

# Get 5 random problems using $sample 
random_problems = list(problems_collection.aggregate([
    {"$sample": {"size": 5}}
]))

# Print the problems
print(f"Retrieved {len(random_problems)} random problems:\n")

for i, problem in enumerate(random_problems, 1):
    print(f"Problem {i}:")
    print(f"Question: {problem.get('question', 'N/A')}")
    print(f"Answer: {problem.get('answer', 'N/A')}")
    print(f"Time Limit: {problem.get('time', 'N/A')} seconds")
    print("-" * 50)

client.close()