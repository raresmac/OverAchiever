from fastapi import APIRouter  # type: ignore
from app.services.steam_service import steam_service  # type: ignore
from app.schemas import SteamSearchResponse, SteamGameResult  # type: ignore

# --- 1. The Router ---
router = APIRouter(
    prefix="/steam",
    tags=["Steam"]
)

# --- 2. The Search Endpoint ---
@router.get("/search", response_model=SteamSearchResponse)
async def api_search_steam(q: str):
    """
    Search for games on the Steam Store by name.
    """
    # We call our service logic
    results = await steam_service.search_games(q)
    
    # We wrap the list in our response schema
    return SteamSearchResponse(results=results)
