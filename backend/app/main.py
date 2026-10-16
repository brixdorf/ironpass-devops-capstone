import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import engine
from app.metrics import MetricsMiddleware
from app.routers import checkins, members, plans, stats, system

log = logging.getLogger("ironpass")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tables are NOT created here. They come from Alembic only:
    #   alembic upgrade head
    log.info("IronPass API is starting")
    yield
    engine.dispose()
    log.info("IronPass API stopped, database connections closed")


app = FastAPI(title="IronPass API", version="1.1.0", lifespan=lifespan)
app.add_middleware(MetricsMiddleware)

app.include_router(system.router)
app.include_router(plans.router)
app.include_router(members.router)
app.include_router(checkins.router)
app.include_router(stats.router)
