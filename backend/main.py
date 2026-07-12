import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import db.database as db

from backend.routers import users, preferences, matches, live, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup, create the database pool
    await db.create_pool()
    yield
    # Runs on shutdown, close the database pool
    await db.close_pool()


app = FastAPI(
    title="Disqueue API",
    description="REST API for the Disqueue matchmaking bot",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(preferences.router)
app.include_router(matches.router)
app.include_router(live.router)