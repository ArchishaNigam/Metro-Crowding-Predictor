from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import stations, timetable_patterns, public_holidays, journey_predictions, saved_prediction_results

app = FastAPI(title="Delhi Metro Crowding Predictor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

app.include_router(stations.router)
app.include_router(timetable_patterns.router)
app.include_router(public_holidays.router)
app.include_router(journey_predictions.router)
app.include_router(saved_prediction_results.router)