from dotenv import get_key
from motor.motor_asyncio import AsyncIOMotorClient

# See https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_motor_client.html

# Note: Clients and sessions are NOT the same thing. Do NOT create a new client for every transaction/operation

client = None

def start_client():
    global client
    if not client:
        client = AsyncIOMotorClient(get_key("/code/app/.env","DATABASE_URL"))
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
