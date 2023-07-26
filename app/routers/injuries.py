import datetime
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
import httpx
import schedule
import time
from sqlalchemy.orm import Session
from sqlalchemy import exists 
from .. import models, schemas, utils
from ..database import get_db
from ..config import settings

router = APIRouter(
    prefix="/injuries", 
    tags=["Injuries"]
)

@router.get("/{league_id}")
async def create_injury(league_id: int, db: Session = Depends(get_db)):
    url = "https://v3.football.api-sports.io/injuries"
    params = {
        "league": league_id,
        "season": "2023"
    }
    headers = {
        "x-apisports-key": f"{settings.api_football_key}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)

    data = response.json()
    injuries = data['response']

    for injury in injuries:
        fixture_id = injury['fixture']['id']
        player_id = injury['player']['id']
        player_name = injury['player']['name']
        player_photo = injury['player']['photo']
        injury_type = injury['player']['type']
        injury_reason = injury['player']['reason']
        team = injury['team']
        league = injury['league']
        fixture_date = injury['fixture']['date']
        fixture_timestamp = injury['fixture']['timestamp']
        fixture_timezone = injury['fixture']['timezone']

        injury_data = {
            'player_id': player_id,
            'player_name': player_name,
            'player_photo': player_photo,
            'injury_type': injury_type,
            'injury_reason': injury_reason,
            'team_id': team['id'],
            'team_name': team['name'],
            'team_logo': team['logo'],
            'fixture_id': fixture_id,
            'fixture_date': fixture_date,
            'fixture_timestamp': fixture_timestamp,
            'fixture_timezone': fixture_timezone,
            'league_id': league['id'],
            'league_name': league['name'],
            'league_country': league['country'],
            'league_logo': league['logo'],
            'league_flag': league['flag'],
            'league_season': league['season'],
        }

        # Check if fixture already exists in the database
        injury_in_db = db.query(models.Injuries).filter(models.Injuries.fixture_id == fixture_id).first()

        if injury_in_db:
            # Update the existing injury
            for key, value in injury_data.items():
                setattr(injury_in_db, key, value)
            print(f"Updated injury with fixture_id {fixture_id}.")
        else:
            # Insert the new injury
            db.add(models.Injuries(**injury_data))
            print(f"Inserted injury with fixture_id {fixture_id}.")

    db.commit()

    return {"message": "Successfully updated and inserted injuries into the database."}
