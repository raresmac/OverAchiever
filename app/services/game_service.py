from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlmodel import select  # type: ignore

# We use absolute imports which resolve correctly when app/__init__.py is present
from app.models import Game  # type: ignore
from app.schemas import GameCreate  # type: ignore
from app.services.steam_service import steam_service  # type: ignore


# =============================================================================
# THE SERVICE LAYER
# =============================================================================
# Why have a service layer? 
# It keeps our API routes clean. The route handles the "Web" stuff (URLs, status codes)
# while this file handles the "Business" stuff (Database queries, calculations).
# =============================================================================


async def create_game(session: AsyncSession, game_data: GameCreate) -> Game:
    """
    Creates a new game in the database.
    """
    # 1. We create a new 'Game' database object using the data from the schema
    new_game = Game.model_validate(game_data)
    
    # 2. We add it to the session "bucket"
    session.add(new_game)
    
    # 3. We save it to the database
    await session.commit()
    
    # 4. We "refresh" the object to get any data the database might have 
    # generated (like timestamps or IDs if they were automatic)
    await session.refresh(new_game)
    
    return new_game


async def get_game(session: AsyncSession, game_id: int) -> Optional[Game]:
    """
    Retrieves a single game by its ID (Steam AppID).
    """
    # session.get is the cleanest way to fetch a single object by its primary key
    return await session.get(Game, game_id)


async def list_games(session: AsyncSession, offset: int = 0, limit: int = 100) -> List[Game]:
    """
    Retrieves a list of games with pagination.
    """
    query = select(Game).offset(offset).limit(limit)
    result = await session.execute(query)
    
    # We use .scalars().all() to get the actual list of Game objects
    return result.scalars().all()

async def search_and_add_game(session: AsyncSession, query: str) -> Optional[Game]:
    """
    Search for a game by name, pick the top result, and save it with full metadata.
    """
    # 1. Search Steam for the query
    search_results = await steam_service.search_games(query)
    if not search_results:
        return None
        
    # 2. Pick the first (best) match
    top_result = search_results[0]
    appid = top_result.id
    
    # Check if we already have this game in our DB
    existing_game = get_game(session, appid)
    if existing_game:
        return existing_game
        
    # 3. Fetch full details for this AppID
    details = await steam_service.get_app_details(appid)
    if not details:
        return None
        
    # 4. Map Steam's data to our SQLModel 'Game'
    # Steam data can be messy, so we use .get() to avoid errors
    new_game = Game(
        id=appid,
        title=details.get("name", top_result.title),
        developer=", ".join(details.get("developers", [])),
        publisher=", ".join(details.get("publishers", [])),
        description=details.get("short_description", ""),
        header_image=details.get("header_image", ""),
        review_score=details.get("metacritic", {}).get("score"),
        steamos_support=details.get("platforms", {}).get("linux", False)
    )
    
    # 5. Save to database
    session.add(new_game)
    await session.commit()
    await session.refresh(new_game)
    
    return new_game
