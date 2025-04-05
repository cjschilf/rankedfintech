from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pprint

# MongoDB connection
uri = "mongodb+srv://colinschilf2025:SuA1Cw1uBUOMCcZq@rankedfintech.veidnzl.mongodb.net/?appName=RankedFintech"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["rankedfintech"]
users_collection = db["users"]

def get_random_user():
    """Retrieve a random user from the users collection"""
    random_user = list(users_collection.aggregate([
        {"$sample": {"size": 1}}
    ]))
    
    return random_user[0] if random_user else None

try:
    # Get total count of users
    total_users = users_collection.count_documents({})
    print(f"Total users in database: {total_users}")
    
    if total_users == 0:
        print("No users found in the database.")
    else:
        # Get a random user
        random_user = get_random_user()
        
        if random_user:
            print("\nRandom User Selected:")
            print(f"Username: {random_user.get('username', 'N/A')}")
            print(f"ELO Rating: {random_user.get('elo', 'N/A')}")
            print(f"Email: {random_user.get('email', 'N/A')}")
            print(f"Joined Date: {random_user.get('joined_date', 'N/A')}")
            
            # Print all fields (in case there are additional ones)
            print("\nComplete user document:")
            pprint.pprint(random_user)
        else:
            print("Error retrieving random user.")
            
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the connection
    client.close()