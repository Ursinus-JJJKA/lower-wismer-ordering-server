from contextlib import asynccontextmanager
from logging import getLogger
logger = getLogger("uvicorn")

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pymongo.errors import OperationFailure

from .database import start_client, end_client
from .routers import account, demo, kitchens, menus, menuitems, orders, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting up database client")
    start_client()
    yield
    logger.debug("Shutting down database client")
    end_client()


app = FastAPI(lifespan=lifespan)

app.include_router(account.router)
app.include_router(demo.router)
app.include_router(kitchens.router)
app.include_router(menus.router)
app.include_router(menuitems.router)
app.include_router(orders.router)
app.include_router(users.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}


@app.exception_handler(OperationFailure)
async def pymongo_write_error(request: Request, exc: OperationFailure):
    logger.info(exc)
    logger.debug(request)
    return JSONResponse(
        status_code=409,
        content={"detail": "Database operation error"}
    )
