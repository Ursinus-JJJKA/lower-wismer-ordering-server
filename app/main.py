from fastapi import FastAPI

from contextlib import asynccontextmanager

from .database import start_client, end_client
from .routers import items, menus, orders, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up database client")
    start_client()
    yield
    print("Shutting down database client")
    end_client()


app = FastAPI(lifespan=lifespan)

app.include_router(items.router)
app.include_router(menus.router)
app.include_router(orders.router)
app.include_router(users.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}
