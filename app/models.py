from sqlalchemy import Column, Integer, String, Boolean, DateTime, TIMESTAMP, ForeignKey, Double
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='True', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=str('now()'))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User")

class User(Base):
    __tablename__  = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=str('now()'))
    phone_number = Column(String, nullable=True)

class Vote(Base):
    __tablename__ = "votes"
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)


class Fixture(Base):
    __tablename__ = 'api_football_fixtures'
    id = Column(Integer, primary_key=True)
    fixture_id = Column(Integer, nullable=False, unique=True)        
    referee = Column(String)
    timezone = Column(String)
    date = Column(DateTime)
    timestamp = Column(Integer)
    venue_id = Column(Integer)
    venue_name = Column(String)
    venue_city = Column(String)
    league_id = Column(Integer)
    league_name = Column(String)
    league_country = Column(String)
    league_logo = Column(String)
    league_flag = Column(String)
    league_season = Column(Integer)
    league_round = Column(String)
    home_team_id = Column(Integer)
    home_team_name = Column(String)
    home_team_logo = Column(String)
    home_team_winner = Column(Boolean)
    away_team_id = Column(Integer)
    away_team_name = Column(String)
    away_team_logo = Column(String)
    away_team_winner = Column(Boolean)
    goals_home = Column(Integer)
    goals_away = Column(Integer)
    score_halftime_home = Column(Integer)
    score_halftime_away = Column(Integer)
    score_fulltime_home = Column(Integer)
    score_fulltime_away = Column(Integer)
    score_extratime_home = Column(Integer)
    score_extratime_away = Column(Integer)
    score_penalty_home = Column(Integer)
    score_penalty_away = Column(Integer)
    status_long = Column(String)
    status_short = Column(String)
    status_elapsed = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=str('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=str('now()'))

class Injuries(Base):
    __tablename__ = 'api_football_injuries'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, nullable=False) 
    player_name = Column(String) 
    player_photo = Column(String) 
    injury_type = Column(String) 
    injury_reason = Column(String) 
    team_id = Column(Integer) 
    team_name = Column(String) 
    team_logo = Column(String) 
    fixture_id = Column(Integer, nullable=False) 
    fixture_timezone = Column(String) 
    fixture_date = Column(DateTime) 
    fixture_timestamp = Column(Integer) 
    league_id = Column(Integer) 
    league_season = Column(Integer) 
    league_name = Column(String) 
    league_country = Column(String) 
    league_logo = Column(String) 
    league_flag = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=str('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=str('now()'))

class Predictions(Base):
    __tablename__ = 'api_football_predictions'
    id = Column(Integer, primary_key=True)
    fixture_id = Column(Integer, nullable=False)
    predictions_winner_id = Column(Integer)
    predictions_winner_comment = Column(String)
    predictions_win_or_draw = Column(Boolean)
    predictions_under_over = Column(Double)
    predictions_goals_home = Column(String)
    predictions_goals_away = Column(String)
    predictions_advice = Column(String)
    predictions_percent_draw = Column(String
    predictions_percent_away = Column(String)
    league_id = Column(Integer)
    league_name = Column(String)
    league_country = Column(String)
    league_logo = Column(String)
    league_flag = Column(String)
    league_season = Column(Integer)
    teams_home_id = Column(Integer)
    teams_home_name = Column(String)
    teams_home_logo = Column(String)
    teams_away_id = Column(Integer)
    teams_away_name = Column(String)
    teams_away_logo = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=str('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=str('now()'))

class Prediction_Comparisons(Base):
    __tablename__ = 'api_football_prediction_comparisons'
    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey("api_football_predictions.id", ondelete="CASCADE"), nullable=False)
    fixture_id = Column(Integer, nullable=False)
    prediction_comparison_team_name = Column(String)
    prediction_comparison_type = Column(String)
    prediction_comparison_value = Column(String)
    prediction = relationship("Predictions")