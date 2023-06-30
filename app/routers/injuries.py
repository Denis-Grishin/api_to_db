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

    existing_fixture_ids = set(db.query(models.Injuries.fixture_id).all())
    rows = []

    for injury in injuries:
        fixture_id = injury['fixture']['id']

        if db.query(exists().where(models.Injuries.fixture_id == fixture_id)).scalar():
            # Skip if fixture already exists in the database
            print(f"Injurie with fixture_id {fixture_id} already exists.")
            continue

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

        row = {
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

        rows.append(row)

    db.bulk_insert_mappings(models.Injuries, rows)
    db.commit()

    num_rows = len(rows)
    print(f"Inserted {num_rows} rows into the database.")

    return {"message": f"Inserted {num_rows} rows into the database."}

