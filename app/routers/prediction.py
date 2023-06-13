import datetime
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
import httpx
import schedule
import time
from sqlalchemy.orm import Session
from sqlalchemy import exists, insert 
from .. import models, schemas, utils
from ..database import get_db

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
        "x-apisports-key": "6a2ebf0bfe57befbe03765041d991643"
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

    db.bulk_insert_mappings(models.Prediction_Comparisons, comp_rows)
    db.commit()

    num_rows = len(comp_rows) + 1  # +1 for the prediction row
    print(f"Inserted {num_rows} rows into the database.")

    return {"message": f"Inserted {num_rows} rows into the database."}


@router.get("/update_all")
async def update_all_predictions(db: Session = Depends(get_db)):
    # First we get all the fixture_ids
    fixtures_url = "https://v3.football.api-sports.io/fixtures"
    fixtures_params = {
        "league": "39",
        "season": "2022",
        "date": "2023-05-28"
    }
    fixtures_headers = {
        "x-apisports-key": "6a2ebf0bfe57befbe03765041d991643"
    }

    async with httpx.AsyncClient() as client:
        fixtures_response = await client.get(fixtures_url, params=fixtures_params, headers=fixtures_headers)

    fixtures_data = fixtures_response.json()
    fixtures = fixtures_data['response']

    # Then for each fixture_id, we call the create_prediction function
    for fixture in fixtures:
        try:
            fixture_id = int(fixture['fixture']['id'])
            print(f"Processing fixture_id: {fixture_id}")
            await create_prediction(fixture_id, db)
        except ValueError:
            print(f"Could not convert {fixture['fixture']['id']} to an integer.")

    return {"message": "Updated all predictions."}