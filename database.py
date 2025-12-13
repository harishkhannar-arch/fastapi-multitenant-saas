import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Get URL from .env file
MONGO_URL = os.getenv("MONGO_URI")

# Create the connection
client = AsyncIOMotorClient(MONGO_URL)

# This is our "Master Database" [cite: 64]
master_db = client.master_db