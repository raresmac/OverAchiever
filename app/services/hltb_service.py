import asyncio
from typing import Optional, Dict
from howlongtobeatpy import HowLongToBeat  # type: ignore

# =============================================================================
# HOW LONG TO BEAT SERVICE
# =============================================================================
# Uses the 'howlongtobeatpy' library to fetch game completion times.
# We use the synchronous .search() wrapped in asyncio.to_thread()
# because the async version has known reliability issues on some platforms.
# =============================================================================

class HLTBService:

    async def get_game_times(self, game_name: str) -> Dict[str, Optional[float]]:
        """
        Searches HLTB for a game and returns Main, Extra, and Completionist hours.
        """
        clean_name = game_name.replace("&quot;", '"').replace("&amp;", "&")
        empty = {"main": None, "extra": None, "comp": None}

        try:
            # Create a fresh instance per call and run sync search in a thread
            results = await asyncio.to_thread(HowLongToBeat().search, clean_name)

            if not results:
                print(f"HLTB: No results for '{clean_name}'")
                return empty

            best = results[0]
            print(f"HLTB: Found '{best.game_name}' (similarity={best.similarity})")

            return {
                "main": best.main_story if best.main_story and best.main_story > 0 else None,
                "extra": best.main_extra if best.main_extra and best.main_extra > 0 else None,
                "comp": best.completionist if best.completionist and best.completionist > 0 else None,
            }

        except Exception as e:
            print(f"HLTB error for '{clean_name}': {e}")
            return empty


hltb_service = HLTBService()
