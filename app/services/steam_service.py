import httpx  # type: ignore
from typing import List, Dict, Any
from app.schemas import SteamGameResult  # type: ignore

# =============================================================================
# STEAM SEARCH SERVICE
# =============================================================================
# This service talks to Steam's official Store API.
# It allows us to find games by name so the user doesn't have to look up 
# Steam AppIDs manually.
# =============================================================================

class SteamService:
    def __init__(self):
        # The base URL for Steam's internal search API (used by the web store)
        self.search_url = "https://store.steampowered.com/api/storesearch/"

    async def search_games(self, query: str) -> List[SteamGameResult]:
        """
        Searches Steam for games matching the query string.
        Returns a list of SteamGameResult objects.
        """
        results = []
        
        try:
            # We use 'httpx' because it's asynchronous and works perfectly with FastAPI
            async with httpx.AsyncClient() as client:
                params = {
                    "term": query,
                    "l": "english",
                    "cc": "US"  # Returns prices in USD and helps with localization
                }
                
                # We make the request to Steam
                response = await client.get(self.search_url, params=params)
                response.raise_for_status() # Raises an error if the site is down
                
                data = response.json()
                
                # Steam returns data in a 'items' list
                items = data.get("items", [])
                
                for item in items:
                    # We convert Steam's data into our 'SteamGameResult' schema
                    results.append(SteamGameResult(
                        id=item.get("id"),
                        title=item.get("name"),
                        icon_url=item.get("tiny_image") # Small thumbnail
                    ))
        
        except Exception as e:
            # If something goes wrong (no internet, Steam is down), 
            # we print the error.
            print(f"Error searching Steam: {e}")
        
        # We always return results, even if empty
        return results

    async def get_app_details(self, appid: int) -> Dict[str, Any]:
        """
        Fetches full details for a specific Steam AppID.
        """
        url = "https://store.steampowered.com/api/appdetails"
        app_details = {} # Default empty dict to ensure we always return something
        
        try:
            async with httpx.AsyncClient() as client:
                params = {"appids": appid, "l": "english"}
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Steam returns data keyed by the AppID string
                app_data = data.get(str(appid), {})
                if app_data.get("success"):
                    app_details = app_data.get("data", {})
        except Exception as e:
            # If Steam is down or the AppID is invalid, we log it but don't crash
            print(f"Error fetching Steam details for {appid}: {e}")
            
        # We always return results, even if empty
        return app_details

# Create a single instance of the service to be used across the app
steam_service = SteamService()
