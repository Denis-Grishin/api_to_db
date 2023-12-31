import asyncio
import datetime
from fastapi import FastAPI, Query, Response, status, HTTPException, Depends, APIRouter
import httpx
import schedule
import time
from sqlalchemy.orm import Session
from sqlalchemy import exists 
from .. import models, schemas, utils
from ..database import get_db
from ..config import settings

router = APIRouter(
    prefix="/fixtures", 
    tags=["Fixtures"]
)

#add fuxtires to DB
@router.get("/{league_id}")
async def create_fixture(league_id: int, db: Session = Depends(get_db)):
    url = "https://v3.football.api-sports.io/fixtures"
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
    fixtures = data['response']

    num_rows_inserted = 0
    num_rows_updated = 0

    for fixture in fixtures:
        fixture_id = fixture['fixture']['id']

        db_fixture = db.query(models.Fixture).filter(models.Fixture.fixture_id == fixture_id).first()
        
        referee = fixture['fixture']['referee']
        timezone = fixture['fixture']['timezone']
        date = fixture['fixture']['date']
        timestamp = fixture['fixture']['timestamp']
        venue = fixture['fixture']['venue']
        status = fixture['fixture']['status']
        league = fixture['league']
        teams = fixture['teams']
        goals = fixture['goals']
        score = fixture['score']

        row = {
            'fixture_id': fixture_id,
            'referee': referee,
            'timezone': timezone,
            'date': date,
            'timestamp': timestamp,
            'venue_id': venue['id'],
            'venue_name': venue['name'],
            'venue_city': venue['city'],
            'league_id': league['id'],
            'league_name': league['name'],
            'league_country': league['country'],
            'league_logo': league['logo'],
            'league_flag': league['flag'],
            'league_season': league['season'],
            'league_round': league['round'],
            'home_team_id': teams['home']['id'],
            'home_team_name': teams['home']['name'],
            'home_team_logo': teams['home']['logo'],
            'home_team_winner': teams['home']['winner'],
            'away_team_id': teams['away']['id'],
            'away_team_name': teams['away']['name'],
            'away_team_logo': teams['away']['logo'],
            'away_team_winner': teams['away']['winner'],
            'goals_home': goals['home'],
            'goals_away': goals['away'],
            'score_halftime_home': score['halftime']['home'],
            'score_halftime_away': score['halftime']['away'],
            'score_fulltime_home': score['fulltime']['home'],
            'score_fulltime_away': score['fulltime']['away'],
            'score_extratime_home': score['extratime']['home'],
            'score_extratime_away': score['extratime']['away'],
            'score_penalty_home': score['penalty']['home'],
            'score_penalty_away': score['penalty']['away'],
            'status_long': status['long'],
            'status_short': status['short'],
            'status_elapsed': status['elapsed']
        }

        if db_fixture:
            # Fixture already exists in the database
            if db_fixture.status_short != status['short']:
                # Status has changed, so update the record
                db.query(models.Fixture).filter(models.Fixture.fixture_id == fixture_id).update(row)
                db.commit()
                num_rows_updated += 1
                print(f"Updated fixture with fixture_id {fixture_id}.")
            else:
                # Status has not changed, so skip this fixture
                print(f"Skipped fixture with fixture_id {fixture_id} - no status change.")
                continue
        else:
            # Fixture does not exist in the database, so insert new record
            db.add(models.Fixture(**row))
            db.commit()
            num_rows_inserted += 1
            print(f"Inserted new fixture with fixture_id {fixture_id}.")

    print(f"Inserted {num_rows_inserted} new rows into the database.")
    print(f"Updated {num_rows_updated} existing rows in the database.")

    return {"message": f"Inserted {num_rows_inserted} new rows and updated {num_rows_updated} existing rows in the database."}



#add one fixture statistics to DB
@router.get("/statistics/{fixture_id}")
async def create_fixture_statistics(fixture_id: int, db: Session = Depends(get_db)):
    url = f"https://v3.football.api-sports.io/fixtures/statistics"
    params = {
        "fixture": fixture_id
    }
    headers = {
        "x-apisports-key": f"{settings.api_football_key}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)

    data = response.json()
    response_data = data['response']

    rows = []

    for team_stats in response_data:
        team_name = team_stats['team']['name']
        statistics = team_stats['statistics']

        for stat in statistics:
            stat_type = stat['type']
            stat_value = stat['value']

            row = {
                'fixture_id': fixture_id,
                'statistics_team_name': team_name,
                'statistics_type': stat_type,
                'statistics_value': str(stat_value)
            }

            # Checking if the record already exists in the database
            existing_record = db.query(models.FixtureStatistics).filter_by(fixture_id=row['fixture_id'], 
                                                                           statistics_team_name=row['statistics_team_name'], 
                                                                           statistics_type=row['statistics_type']).first()
            if existing_record is None:
                rows.append(row)

    if rows:  # If rows is not empty, i.e., there are new records
        db.bulk_insert_mappings(models.FixtureStatistics, rows)
        db.commit()

    num_rows = len(rows)
    print(f"Inserted {num_rows} rows into Fixture Stastic table.")

    return {"message": f"Inserted {num_rows} rows into Fixture Stastic table"}

#####

@router.get("/uploadstatistics/{league_id}")
async def update_all_statistics(league_id: int, db: Session = Depends(get_db)):
    # First we get all the fixture_ids
    print(f"Getting all fixture_ids for league_id: {league_id}")
    fixtures_url = "https://v3.football.api-sports.io/fixtures"
    fixtures_params = {
        "league": league_id,
        "season": "2023"
    }
    fixtures_headers = {
        "x-apisports-key": f"{settings.api_football_key}"
    }

    async with httpx.AsyncClient() as client:
        fixtures_response = await client.get(fixtures_url, params=fixtures_params, headers=fixtures_headers)

    fixtures_data = fixtures_response.json()
    fixtures = fixtures_data.get('response', [])

    total_rows = len(fixtures)
    print(f"Total rows to be processed: {total_rows}")

    # Then for each fixture_id, we call the create_prediction function
    for i, fixture in enumerate(fixtures):
        try:
            fixture_id = int(fixture['fixture']['id'])
            print(f"Processing fixture_id: {fixture_id}")
            await asyncio.sleep(1)  # Add this line to introduce a 1-second delay
            await create_fixture_statistics(fixture_id, db)
            print(f"Processed rows: {i+1}/{total_rows}")
        except ValueError as e:
            print(f"Could not convert fixture_id to an integer: {fixture['fixture']['id']}")

    return {"message": f"Updated all statistis for league: {league_id}."}



#update fixtures table with in progress fixtures data
@router.get("/update_fixtures")
async def update_fixtures(db: Session = Depends(get_db)):
    url = "https://v3.football.api-sports.io/fixtures"
    params = {
        "league": "188",
        "season": "2022"
    }
    headers = {
        "x-apisports-key": f"{settings.api_football_key}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)

    data = response.json()
    fixtures = data['response']

    updated_fixtures = []

    for fixture in fixtures:
        fixture_id = fixture['fixture']['id']
        status = fixture['fixture']['status']

        if status in ['NS', 'TBD', '1H']:
            updated_fixtures.append(fixture)

    rows = []

    for fixture in updated_fixtures:
        fixture_id = fixture['fixture']['id']
        referee = fixture['fixture']['referee']
        timezone = fixture['fixture']['timezone']
        date = fixture['fixture']['date']
        timestamp = fixture['fixture']['timestamp']
        venue = fixture['fixture']['venue']
        status = fixture['fixture']['status']
        league = fixture['league']
        teams = fixture['teams']
        goals = fixture['goals']
        score = fixture['score']

        row = {
            'fixture_id': fixture_id,
            'referee': referee,
            'timezone': timezone,
            'date': date,
            'timestamp': timestamp,
            'venue_id': venue['id'],
            'venue_name': venue['name'],
            'venue_city': venue['city'],
            'league_id': league['id'],
            'league_name': league['name'],
            'league_country': league['country'],
            'league_logo': league['logo'],
            'league_flag': league['flag'],
            'league_season': league['season'],
            'league_round': league['round'],
            'home_team_id': teams['home']['id'],
            'home_team_name': teams['home']['name'],
            'home_team_logo': teams['home']['logo'],
            'home_team_winner': teams['home']['winner'],
            'away_team_id': teams['away']['id'],
            'away_team_name': teams['away']['name'],
            'away_team_logo': teams['away']['logo'],
            'away_team_winner': teams['away']['winner'],
            'goals_home': goals['home'],
            'goals_away': goals['away'],
            'score_halftime_home': score['halftime']['home'],
            'score_halftime_away': score['halftime']['away'],
            'score_fulltime_home': score['fulltime']['home'],
            'score_fulltime_away': score['fulltime']['away'],
            'score_extratime_home': score['extratime']['home'],
            'score_extratime_away': score['extratime']['away'],
            'score_penalty_home': score['penalty']['home'],
            'score_penalty_away': score['penalty']['away'],
            'status_long': status['long'],
            'status_short': status['short'],
            'status_elapsed': status['elapsed']
        }

        rows.append(row)

    if rows:
        db.bulk_update_mappings(models.Fixture, rows)
        db.commit()
        print(f"Updated {len(rows)} fixtures in the database.")

    return {"message": f"Updated {len(rows)} fixtures in the database."}



