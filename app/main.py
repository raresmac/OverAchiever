from contextlib import asynccontextmanager

from fastapi import FastAPI  # type: ignore

# We import our database initialization function
from app.database import init_db  # type: ignore
# We import our settings to give the app its name and version
from app.config import settings  # type: ignore


# --- 1. The Lifespan Event ---
# This is a special function that runs when the app starts and shuts down.
# It is the perfect place to set up the database.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and Shutdown logic for the OverAchiever API.
    """
    # Everything before 'yield' runs when the app STARTS
    print(f"--- Starting up {settings.PROJECT_NAME} ---")
    
    # We call our table creator here. 
    # This is why your tables will appear in pgAdmin automatically!
    await init_db()
    
    yield  # The app stays running here
    
    # Everything after 'yield' runs when the app STOPS
    print(f"--- Shutting down {settings.PROJECT_NAME} ---")


# --- 2. The App Instance ---
# We create the main FastAPI object. 
# We tell it to use our 'lifespan' function we defined above.
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## OverAchiever API
    Welcome to the backbone of your game tracking empire. This API handles:
    * **Steam Search**: Find any game on the Steam store without knowing its ID.
    * **Library Management**: Add games to your collection, track status, and set priorities.
    * **Progress Tracking**: Log play sessions and achievements (Coming soon!).
    """,
    lifespan=lifespan
)

# --- 2.1 Include Routers ---
# We import our routers and 'include' them in the main app.
from app.api.games import router as games_router # type: ignore
from app.api.steam import router as steam_router # type: ignore

app.include_router(games_router)
app.include_router(steam_router)


# --- 3. The Health Check Route ---
# This is a standard route used to verify the API is alive.
# Think of it like a "heartbeat."
@app.get("/health")
async def health_check():
    """
    Proof of life endpoint.
    Returns the project name and current version.
    """
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# --- 4. The Welcome Route ---
# Just a simple greeting for when you visit the base URL (http://localhost:8000/).
@app.get("/")
async def root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API!",
        "docs": "/docs"  # This reminds you that FastAPI generates automatic documentation!
    }
