from fastapi import FastAPI

from . import crud, models, schemas
#from .dependencies import get_query_token, get_token_header
from .routers import items, users


app = FastAPI()

app.include_router(users.router)
app.include_router(items.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}