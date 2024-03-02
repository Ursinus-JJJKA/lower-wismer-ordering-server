from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pymongo.errors import OperationFailure

from contextlib import asynccontextmanager
from logging import getLogger

from .crud import get_kitchennames, get_menunames
from .database import start_client, end_client
from .routers import menuitems, orders, users

#TODO see if there is a better way to be logging
logger = getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting up database client")
    start_client()
    yield
    logger.debug("Shutting down database client")
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


@app.exception_handler(OperationFailure)
async def pymongo_write_error(request: Request, exc: OperationFailure):
    logger.info(exc)
    logger.debug(request)
    return JSONResponse(
        status_code=409,
        content={"detail": "Database operation error"}
    )
