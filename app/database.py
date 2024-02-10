from dotenv import dotenv_values
from motor.motor_asyncio import AsyncIOMotorClient

from urllib.parse import quote_plus

# See https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_motor_client.html

# Note: Clients and sessions are NOT the same thing. Do NOT create a new client for every transaction/operation

client = None

def start_client():
    CONFIG = dotenv_values("/code/app/.env")    
    global client
    if not client:
        auth = f"{quote_plus(CONFIG['MONGODB_USERNAME'])}:{quote_plus(CONFIG['MONGODB_PASSWORD'])}@" if ('MONGODB_USERNAME' in CONFIG and 'MONGODB_PASSWORD' in CONFIG) else ""
        DATABASE_URL = f"mongodb://{auth}lwo_db:{CONFIG.get('MONGODB_PORT','27017')}/{CONFIG.get('MONGODB_DB','db')}?authSource=admin"
        client = AsyncIOMotorClient(DATABASE_URL)
    else:
        raise RuntimeError("Client already exists")

def end_client():
    global client
    if client:
        client.close()
        client = None

def get_session():
    global client
    # Note: the session doesn't really start until this object is awaited
    # Thus this should be used like:
    #
    # async with await get_session() as s:
    #     await get_collection(COLLECTION_NAME).operation(ARGS, session=s)
    #     ...
    # (No end_session() needed because of the with clause)
    #
    # From the docs: Do not use the same session for multiple operations concurrently.
    return client.start_session()

def get_collection(collection_name):
    global client
    return client.get_default_database()[collection_name]
