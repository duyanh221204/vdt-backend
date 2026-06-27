from contextlib import asynccontextmanager

from fastapi import FastAPI

from configuration.app_init import init
from configuration.database import async_engine
from exception.global_exception_handler import add_exception_handlers
from router import auth_router, student_router, user_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init()
    yield
    await async_engine.dispose()

app = FastAPI(lifespan=lifespan)

add_exception_handlers(app=app)


@app.get('/', tags=['Root'])
async def root():
    return {'message': 'Hello Viettel Digital Talent 2026!'}

app.include_router(auth_router.router)
app.include_router(student_router.router)
app.include_router(user_router.router)
