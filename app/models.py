from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel  # type: ignore


# =============================================================================
# 1. ENUMS (Restricted Choices)
# =============================================================================

class GameStatus(str, Enum):
    PLAYING = "Playing"
    ON_HOLD = "On-Hold"
    PLAN_TO_PLAY = "Plan to Play"
    COMPLETED = "Completed"
    DROPPED = "Dropped"


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Ownership(str, Enum):
    STEAM = "Steam"
    GOG = "GOG"
    GAME_PASS = "Game Pass"
    EPIC = "Epic"
    AMAZON = "Amazon"
    OTHER = "Other"

class Difficulty(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class SessionType(str, Enum):
    LIVE = "LIVE"
    RETRO = "RETRO"


# =============================================================================
# 2. LINK TABLES (The "Connectors")
# =============================================================================

class GameTagLink(SQLModel, table=True):
    """
    Many-to-Many bridge between Games and Tags.
    One game can have many genres (RPG, Action), and one genre belongs to many games.
    """
    __tablename__ = "game_tags_link"
    game_id: int = Field(foreign_key="games.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)


# =============================================================================
# 3. GLOBAL METADATA (Shared Knowledge)
# =============================================================================

class Tag(SQLModel, table=True):
    """
    Genres or descriptors like 'Soulslike', 'Open World', 'RPG'.
    """
    __tablename__ = "tags"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    # Relationships: This tells SQLModel how to find games using this tag.
    games: List["Game"] = Relationship(back_populates="tags", link_model=GameTagLink)


class Game(SQLModel, table=True):
    """
    Physical data about a video game.
    The 'id' here is the official Steam AppID (e.g., 400 for Portal).
    """
    __tablename__ = "games"
    id: int = Field(primary_key=True) # Official Steam ID
    title: str = Field(index=True)
    developer: Optional[str] = None
    publisher: Optional[str] = None
    release_date: Optional[date] = None
    description: Optional[str] = None
    header_image: Optional[str] = None
    review_score: Optional[int] = Field(default=None, ge=0, le=100)
    steamos_support: bool = Field(default=False)
    
    # How Long To Beat (HLTB) Data
    hltb_main: Optional[float] = None # Time to finish story
    hltb_extra: Optional[float] = None # Story + Side quests
    hltb_comp: Optional[float] = None # 100% Completion

    # Relationships
    tags: List[Tag] = Relationship(back_populates="games", link_model=GameTagLink)
    achievements: List["AchievementSchema"] = Relationship(back_populates="game")


class AchievementSchema(SQLModel, table=True):
    """
    Global definition of an achievement (Name, Description, Icon).
    """
    __tablename__ = "achievements_schema"
    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="games.id", index=True)
    api_name: str # The internal Steam ID (e.g., 'ACH_001')
    display_name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    icon_gray_url: Optional[str] = None
    is_hidden: bool = Field(default=False)
    rarity: float = Field(default=0.0)

    # Relationships
    game: Game = Relationship(back_populates="achievements")


# =============================================================================
# 4. USER DATA (Personal Quest Log)
# =============================================================================

class UserGameProgress(SQLModel, table=True):
    """
    The heart of your library. Tracks YOUR progress in a specific game.
    """
    __tablename__ = "user_game_progress"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    game_id: int = Field(foreign_key="games.id", index=True)
    
    status: GameStatus = Field(default=GameStatus.PLAN_TO_PLAY)
    priority: Priority = Field(default=Priority.MEDIUM)
    ownership: Ownership = Field(default=Ownership.STEAM)
    rating: Optional[int] = Field(default=None, ge=1, le=10)
    difficulty: Difficulty = Field(default=Difficulty.MEDIUM)
    
    total_hours: float = Field(default=0.0) # Total time you've played this
    
    # Milestone Dates
    start_date: Optional[date] = None
    story_date: Optional[date] = None
    comp_date: Optional[date] = None


class Session(SQLModel, table=True):
    """
    A single play session.
    """
    __tablename__ = "sessions"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_game_id: int = Field(foreign_key="user_game_progress.id", index=True)
    
    session_type: SessionType = Field(default=SessionType.LIVE)
    duration: int # Minutes played
    played_at: datetime = Field(default_factory=datetime.utcnow)
    story_flag: bool = Field(default=False) # Did you finish the story this session?


class UserAchievement(SQLModel, table=True):
    """
    Bridge table: Which achievement did YOU unlock and WHEN.
    """
    __tablename__ = "user_achievements"
    user_id: int = Field(primary_key=True)
    achievement_id: int = Field(foreign_key="achievements_schema.id", primary_key=True)
    unlocked_at: datetime = Field(default_factory=datetime.utcnow)


class UserTagMastery(SQLModel, table=True):
    """
    Tracks your "Experience Points" in a specific genre (Tag).
    Level = sqrt(XP) * 0.5
    """
    __tablename__ = "user_tag_mastery"
    user_id: int = Field(primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
    
    total_xp: float = Field(default=0.0)
    current_level: int = Field(default=1)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
