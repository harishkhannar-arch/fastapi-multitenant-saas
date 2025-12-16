import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URI")

# The crucial fix for SSL errors
client = AsyncIOMotorClient(MONGO_URL, tlsCAFile=certifi.where())

master_db = client.master_db