from fastapi import FastAPI

#from . import crud, models, schemas
from .database import start_client, end_client
#from .dependencies import get_query_token, get_token_header
from .routers import items#, menus, orders, users

app = FastAPI()

@app.on_event("startup")
def startup_db_client():
    print("Starting client hook")
    start_client()

@app.on_event("shutdown")
def shutdown_db_client():
    print("Shutdown client hook")
    end_client()

app.include_router(items.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}
