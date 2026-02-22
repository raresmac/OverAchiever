from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict  # type: ignore


# =============================================================================
# 1. THE DIFFERENCE BETWEEN MODELS AND SCHEMAS
# =============================================================================
# Models (in models.py) describe your DATABASE TABLES.
# Schemas (here) describe your API DATA (JSON).
# We separate them so we can hide internal info or add extra fields for the UI.
# =============================================================================


class GameBase(BaseModel):
    """
    Common fields shared by all Game schemas.
    """
    id: int # The Steam AppID
    title: str
    developer: Optional[str] = None
    publisher: Optional[str] = None
    release_date: Optional[date] = None
    description: Optional[str] = None
    header_image: Optional[str] = None
    review_score: Optional[int] = None
    steamos_support: bool = False
    
    # HLTB times
    hltb_main: Optional[float] = None
    hltb_extra: Optional[float] = None
    hltb_comp: Optional[float] = None


class GameCreate(GameBase):
    """
    Schema for CREATING a game.
    At this stage, we'll just send the Steam AppID and maybe the title,
    but we keep the full metadata optional so our scrapers can fill it later.
    """
    pass


class GameRead(GameBase):
    """
    Schema for READING a game (what the API sends back).
    This includes everything in GameBase.
    
    Config: from_attributes=True allows Pydantic to read data 
    directly from our SQLModel database objects.
    """
    model_config = ConfigDict(from_attributes=True)


class TagBase(BaseModel):
    name: str

class TagRead(TagBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# STEAM SEARCH SCHEMAS
# =============================================================================

class SteamGameResult(BaseModel):
    """
    Individual search result from Steam.
    """
    id: int # Steam AppID
    title: str
    icon_url: str = ""

class SteamSearchResponse(BaseModel):
    """
    A list of matching games.
    """
    results: List[SteamGameResult]
