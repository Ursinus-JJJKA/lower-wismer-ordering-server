from fastapi import FastAPI

from contextlib import asynccontextmanager

from .crud import get_kitchennames, get_menunames
from .database import start_client, end_client
from .routers import menuitems, orders, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up database client")
    start_client()
    yield
    print("Shutting down database client")
    end_client()


app = FastAPI(lifespan=lifespan)

app.include_router(menuitems.router)
app.include_router(orders.router)
app.include_router(users.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}

@app.get("/menus", tags=["Menus"], response_model=list[str])
async def get_menus_handler():
    return await get_menunames()

@app.get("/kitchens", tags=["Kitchens"], response_model=list[str])
async def get_kitchens_handler():
    return await get_kitchennames()
