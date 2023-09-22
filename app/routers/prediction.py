import asyncio
import datetime
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
import httpx
import schedule
import time
from sqlalchemy.orm import Session
from sqlalchemy import exists, insert, update, delete
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

    try:
        async with httpx.AsyncClient(timeout=10.0) as client: # Set a timeout
            response = await client.get(url, params=params, headers=headers)
    except httpx.TimeoutException:
        print(f"Timeout error while fetching data for fixture_id: {fixture_id}")
        return {"error": "Timeout error occurred while fetching prediction data"}


    data = response.json()
    prediction = data['response'][0]

    print(f"Retrieved prediction data for fixture_id: {fixture_id}")

    if db.query(exists().where(models.Predictions.fixture_id == fixture_id)).scalar():
        # Update prediction if it already exists in the database
        print(f"Prediction with fixture_id {fixture_id} already exists. Updating...")

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

        db.query(models.Predictions).filter(models.Predictions.fixture_id == fixture_id).update(pred_row)

        print(f"Updated prediction with fixture_id: {fixture_id}")
    else:
        print(f"No prediction found for fixture_id {fixture_id}. Creating new record...")
        
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

    # Now, for the comparisons, we need to update or create new rows
    # First, get the prediction_id whether it was updated or created
    prediction_id = db.query(models.Predictions.id).filter(models.Predictions.fixture_id == fixture_id).scalar()

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

    # Delete existing comparisons for this prediction
    db.query(models.PredictionComparisons).filter(models.PredictionComparisons.prediction_id == prediction_id).delete()

    # Insert new comparisons
    db.execute(insert(models.PredictionComparisons).values(comp_rows))

    db.commit()
    print(f"Inserted/Updated {len(comp_rows)} rows with prediction_id: {prediction_id} and fixture_id: {fixture_id} into PredictionComparisons table.")
    return {"message": "Prediction and comparisons created/updated successfully!"}

@router.get("/uploadpredictions/{league_id}")
async def update_all_predictions(league_id: int, db: Session = Depends(get_db)):
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

    try:
        async with httpx.AsyncClient(timeout=10.0) as client: # Set a timeout
            fixtures_response = await client.get(fixtures_url, params=fixtures_params, headers=fixtures_headers)
    except httpx.TimeoutException:
        print(f"Timeout error while fetching fixtures for league_id: {league_id}")
        return {"error": "Timeout error occurred while fetching fixtures data"}

    fixtures_data = fixtures_response.json()
    fixtures = fixtures_data.get('response', [])

    print(f"Retrieved {len(fixtures)} fixtures for league_id: {league_id}")

    # Then for each fixture_id, we call the create_prediction function
    for i, fixture in enumerate(fixtures, 1):
        try:
            fixture_id = int(fixture['fixture']['id'])
            fixture_status = fixture['fixture']['status']['short']
            
            if fixture_status != 'FT':  # Skip fixtures with a status of "FT" (Full Time)
                print(f"Processing fixture_id: {fixture_id} ({i} of {len(fixtures)})")
                await asyncio.sleep(2)  # Add this line to introduce a 2-second delay
                await create_prediction(fixture_id, db)
                print(f"Finished processing fixture_id: {fixture_id}")
            else:
                print(f"Skipping fixture_id: {fixture_id} due to status 'FT'")
        except ValueError as e:
            print(f"Could not convert fixture_id to an integer: {fixture['fixture']['id']}")
            #traceback.print_exc()

    print("Finished updating all predictions.")
    
    return {"message": "Updated all predictions."}