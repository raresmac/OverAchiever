from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore
from sqlmodel import SQLModel

from app.config import settings  # type: ignore

# --- 1. The Engine ---
# This is the actual "connection pipe" to your PostgreSQL database.
# We use create_async_engine because FastAPI works better with asynchronous 
# database calls (it doesn't "block" the whole app while waiting for the DB).
engine = create_async_engine(
    settings.async_database_url,
    echo=True,       # Set to True to see the actual SQL commands in your terminal (great for learning!)
    future=True      # Uses the modern SQLAlchemy 2.0 style
)

# --- 2. The Session Factory ---
# Think of the Engine as the pipe, and the Session as a "bucket of work".
# You open a session, do your database tasks (like saving a game), and then 
# "commit" the bucket to save everything at once.
async_session_maker = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False  # Keeps objects usable even after we save/commit them
)


# --- 3. Database Initialization ---
async def init_db() -> None:
    """
    This function is our "table creator."
    It checks all our SQLModel classes and tells PostgreSQL to create them
    if they don't exist yet. We will call this when the app starts up.
    """
    async with engine.begin() as conn:
        # SQLModel.metadata holds the definitions of all our tables.
        # run_sync is used because SQLAlchemy's creation tool is technically 
        # synchronous, so we run it inside the async connection.
        await conn.run_sync(SQLModel.metadata.create_all)


# --- 4. The Session Dependency ---
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI uses this "Dependency" for our web routes.
    Every time a user makes a request, they get their own private 
    database session, and it automatically closes when they are done.
    """
    async with async_session_maker() as session:
        yield session
