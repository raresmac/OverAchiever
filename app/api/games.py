from typing import List
from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

# Import our database session tool
from app.database import get_session  # type: ignore
# Import our API schemas (the JSON shapes)
from app.schemas import GameCreate, GameRead  # type: ignore
# Import our business logic (the services)
from app.services.game_service import create_game, get_game, list_games, search_and_add_game  # type: ignore

# --- 1. The Router ---
# We use APIRouter to group these endpoints together. 
# We'll later plug this "mini-app" into the main app.
router = APIRouter(
    prefix="/games",
    tags=["Games"] # This groups them under "Games" in the /docs page
)


# --- 2. Smart Search & Add ---
@router.post("/search-and-add", response_model=GameRead, status_code=status.HTTP_201_CREATED)
async def api_search_and_add(
    q: str, 
    session: AsyncSession = Depends(get_session)
):
    """
    The magic button: Type a name, and we'll find the best match on Steam 
    and add it to your library with all its metadata automatically.
    """
    game = await search_and_add_game(session, q)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find a matching game for '{q}' on Steam."
        )
    return game


# --- 2.1 Create a Game (Manual) ---
@router.post("/", response_model=GameRead, status_code=status.HTTP_201_CREATED)
async def api_create_game(
    game: GameCreate, 
    session: AsyncSession = Depends(get_session)
):
    """
    Adds a new game to the tracker.
    """
    # Check if the game already exists
    existing = await get_game(session, game.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Game with AppID {game.id} already exists in the library."
        )
    
    return await create_game(session, game)


# --- 3. List all Games ---
@router.get("/", response_model=List[GameRead])
async def api_list_games(
    offset: int = 0, 
    limit: int = 100, 
    session: AsyncSession = Depends(get_session)
):
    """
    Gets a list of all games in your library.
    """
    return await list_games(session, offset, limit)


# --- 4. Get a specific Game ---
@router.get("/{game_id}", response_model=GameRead)
async def api_get_game(
    game_id: int, 
    session: AsyncSession = Depends(get_session)
):
    """
    Gets detailed information about a single game using its Steam AppID.
    """
    game = await get_game(session, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found."
        )
    return game
