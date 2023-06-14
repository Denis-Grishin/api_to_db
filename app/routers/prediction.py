import asyncio
import datetime
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
import httpx
import schedule
import time
from sqlalchemy.orm import Session
from sqlalchemy import exists, insert 
from .. import models, schemas, utils
from ..database import get_db
from ..config import settings
import traceback

router = APIRouter(
    prefix="/predictions", 
    tags=["Predictions"]
)

@router.get("/{fixture_id}")
async def create_prediction(fixture_id: int, db: Session = Depends(get_db)):
    url = f"https://v3.football.api-sports.io/predictions/"
    params = {
        "fixture": fixture_id
    }
    headers = {
        "x-apisports-key": f"{settings.api_football_key}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)

    data = response.json()
    prediction = data['response'][0]

    if db.query(exists().where(models.Predictions.fixture_id == fixture_id)).scalar():
        # Skip if prediction already exists in the database
        print(f"Prediction with fixture_id {fixture_id} already exists.")
        return {"message": f"Prediction with fixture_id {fixture_id} already exists."}

    home_team_name = prediction['teams']['home']['name']
    away_team_name = prediction['teams']['away']['name']

    pred_row = {
        'fixture_id': fixture_id,
        'predictions_winner_id': prediction['predictions']['winner']['id'],
        'predictions_winner_name': prediction['predictions']['winner']['name'],
        'predictions_winner_comment': prediction['predictions']['winner']['comment'],
        'predictions_win_or_draw': prediction['predictions']['win_or_draw'],
        'predictions_under_over': prediction['predictions']['under_over'],
        'predictions_goals_home': prediction['predictions']['goals']['home'],
        'predictions_goals_away': prediction['predictions']['goals']['away'],
        'predictions_advice': prediction['predictions']['advice'],
        'predictions_percent_home': prediction['predictions']['percent']['home'],
        'predictions_percent_draw': prediction['predictions']['percent']['draw'],
        'predictions_percent_away': prediction['predictions']['percent']['away'],
        'league_id': prediction['league']['id'],
        'league_name': prediction['league']['name'],
        'league_country': prediction['league']['country'],
        'league_logo': prediction['league']['logo'],
        'league_flag': prediction['league']['flag'],
        'league_season': prediction['league']['season'],
        'teams_home_id': prediction['teams']['home']['id'],
        'teams_home_name': prediction['teams']['home']['name'],
        'teams_home_logo': prediction['teams']['home']['logo'],
        'teams_away_id': prediction['teams']['away']['id'],
        'teams_away_name': prediction['teams']['away']['name'],
        'teams_away_logo': prediction['teams']['away']['logo']
    }

    prediction_id = db.execute(insert(models.Predictions).values(**pred_row).returning(models.Predictions.id)).scalar_one()
    print(f"Inserted a row with prediction_id: {prediction_id} and fixture_id: {fixture_id} into Predictions table.")

    comp_rows = []
    for comparison_type, comparison_values in prediction['comparison'].items():
        for team, value in comparison_values.items():
            comp_row = {
                'prediction_id': prediction_id,
                'fixture_id': fixture_id,
                'prediction_comparison_team_name': home_team_name if team == "home" else away_team_name,
                'prediction_comparison_type': comparison_type,
                'prediction_comparison_value': value
            }
            comp_rows.append(comp_row)

    team_stats = ['wins', 'draws', 'loses', 'goals_for_totals', 'goals_against_totals']

    for team_stat in team_stats:
        for team in ['home', 'away']:
            team_name = prediction['teams'][team]['name']
            if team_stat in ['wins', 'draws', 'loses']:
                comp_row = {
                    'prediction_id': prediction_id,
                    'fixture_id': fixture_id,
                    'prediction_comparison_team_name': team_name,
                    'prediction_comparison_type': team_stat + '_totals',
                    'prediction_comparison_value': prediction['teams'][team]['league']['fixtures'][team_stat]['total']
                }
                comp_rows.append(comp_row)
            elif team_stat in ['goals_for_totals', 'goals_against_totals']:
                direction = 'for' if 'for' in team_stat else 'against'
                comp_row = {
                    'prediction_id': prediction_id,
                    'fixture_id': fixture_id,
                    'prediction_comparison_team_name': team_name,
                    'prediction_comparison_type': team_stat,
                    'prediction_comparison_value': prediction['teams'][team]['league']['goals'][direction]['total']['total']
                }
                comp_rows.append(comp_row)

    db.execute(insert(models.PredictionComparisons).values(comp_rows))

    db.commit()
    print(f"Inserted {len(comp_rows)} rows with prediction_id: {prediction_id} and fixture_id: {fixture_id} into PredictionComparisons table.")
    return {"message": "Prediction created successfully!"}

@router.get("/uploadpredictions/{league_id}")
async def update_all_predictions(league_id: int, db: Session = Depends(get_db)):
    # First we get all the fixture_ids
    print(f"Getting all fixture_ids for league_id: {league_id}")
    fixtures_url = "https://v3.football.api-sports.io/fixtures"
    fixtures_params = {
        "league": league_id,
        "season": "2022"
    }
    fixtures_headers = {
        "x-apisports-key": f"{settings.api_football_key}"
    }

    async with httpx.AsyncClient() as client:
        fixtures_response = await client.get(fixtures_url, params=fixtures_params, headers=fixtures_headers)

    fixtures_data = fixtures_response.json()
    fixtures = fixtures_data.get('response', [])

    # Then for each fixture_id, we call the create_prediction function
    for fixture in fixtures:
        try:
            fixture_id = int(fixture['fixture']['id'])
            print(f"Processing fixture_id: {fixture_id}")
            await asyncio.sleep(2)  # Add this line to introduce a 1-second delay
            await create_prediction(fixture_id, db)
        except ValueError as e:
           print(f"Could not convert fixture_id to an integer: {fixture['fixture']['id']}")
            #traceback.print_exc()

    return {"message": "Updated all predictions."}
