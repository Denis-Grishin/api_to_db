from pydantic import BaseModel, EmailStr, conint
from datetime import datetime
from typing import Optional, List

#define schemas

class PostBase(BaseModel):
     title: str
     content: str
     published: bool = True

class PostCreate(PostBase):
     pass 

class UserCreate(BaseModel):
     email: EmailStr
     password: str

class UserOut(BaseModel):
     id: int
     email: EmailStr
     created_at: datetime

     class Config:
          orm_mode = True

class Post(PostBase):
     id: int
     created_at: datetime
     owner_id: int
     owner: UserOut

     class Config:
          orm_mode = True

class PostOut(BaseModel):
     Post: Post
     votes: int

     class Config:
          orm_mode = True

class UserLogin(BaseModel):
     email: EmailStr
     password: str

class Token(BaseModel):
     access_token: str
     token_type: str

class TokenData(BaseModel):
     id: Optional[str] = None

class Vote(BaseModel):
     post_id: int
     dir: conint(le=1)

class FixturesCreate(BaseModel):
     id: int
     fixture_id: int   
     referee = str
     timezone = str
     date = datetime
     timestamp = int
     venue_id = int
     venue_name = str
     venue_city = str
     league_id = int
     league_name = str
     league_country = str
     league_logo = str
     league_flag = str
     league_season = int
     league_round = str
     home_team_id = int
     home_team_name = str
     home_team_logo = str
     home_team_winner = bool
     away_team_id = int
     away_team_name = str
     away_team_logo = str
     away_team_winner = bool
     goals_home = int
     goals_away = int
     score_halftime_home = int
     score_halftime_away = int
     score_fulltime_home = int
     score_fulltime_away = int
     score_extratime_home = int
     score_extratime_away = int
     score_penalty_home = int
     score_penalty_away = int
     status_long = str
     status_short = str
     status_elapsed = int
     created_at = datetime
     updated_at = datetime


class InjuriesCreate(BaseModel):
    id: int
    player_id: int
    player_name: str
    player_photo: str
    injury_type: str
    injury_reason: str
    team_id: int
    team_name: str
    team_logo: str
    fixture_id: int
    fixture_timezone: str
    fixture_date: datetime
    fixture_timestamp: int
    league_id: int
    league_season: int
    league_name: str
    league_country: str
    league_logo: str
    league_flag: str
    created_at: datetime
    updated_at: datetime
