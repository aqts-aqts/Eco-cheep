import os
from pymongo import MongoClient
from bcrypt import gensalt, hashpw, checkpw
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('MONGO_URI'))
db = client['ecocheep']
users = db['users']

def check_password(password: str, hashed_password: bytes) -> bool:
    return checkpw(password.encode(), hashed_password)

def hash_password(password: str) -> bytes:
    return hashpw(password.encode(), gensalt())

def get_user(username) -> dict:
    return users.find_one({'username': username})

def create_user(username: str, password: str) -> None:
    users.insert_one({
        'username': username, 
        'password': hash_password(password), 
        'quests': [], 
        'exp': 0, 
        'cheep_messages': [{'role': 'system', 'content': open('data/cheep.txt').read()}]
    })

def update_user_messages(username: str, messages: list[dict[str, str]]) -> None:
    users.update_one({'username': username}, {'$set': {'cheep_messages': messages}})

def update_user_quests(username: str, quests: list[dict[str, str | float]]) -> None:
    users.update_one({'username': username}, {'$set': {'quests': quests}})

def finish_quest(username: str, proof: str) -> None:
    user = get_user(username)
    quests = user['quests']
    exp = 0
    for quest in quests:
        if quest['proof'] == proof:
            exp = float(quest['exp'])
            quests.remove(quest)
            break
    users.update_one({'username': username}, {'$set': {'quests': quests}})
    users.update_one({'username': username}, {'$inc': {'exp': exp}})