from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd

# Загружаем модель при старте сервера
model = joblib.load("models/model.pkl")
feature_cols = joblib.load("models/feature_cols.pkl")

app = FastAPI(
    title="AMg6 Deformation Predictor",
    description="API для предсказания деформации алюминиевого сплава АМг6",
    version="1.0"
)


# ===== СХЕМА ВХОДА =====
class PredictRequest(BaseModel):
    temperature: float      # °C
    time: float             # сек
    speed: float            # штрих/сек
    stress: float           # МПа


# ===== СХЕМА ВЫХОДА =====
class PredictResponse(BaseModel):
    angle_degrees: float
    angle_radians: float
    gamma_percent: float


# ===== ЭНДПОИНТЫ =====
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AMg6 Deformation Predictor API",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # Feature engineering — как при обучении
    T_gom = (req.temperature + 273.15) / 933.0
    log_t = np.log1p(req.time)

    # Формируем признаки как DataFrame — с именами колонок
    X = pd.DataFrame(
        [[
            req.temperature,
            req.time,
            req.speed,
            T_gom,
            log_t,
            req.stress
        ]],
        columns=feature_cols
    )

    # Предсказание
    angle_deg = float(model.predict(X)[0])
    angle_rad = angle_deg * np.pi / 180
    gamma_pct = angle_rad * 2 / 40 * 100   # r=2, L=40

    return PredictResponse(
        angle_degrees=round(angle_deg, 2),
        angle_radians=round(angle_rad, 4),
        gamma_percent=round(gamma_pct, 2)
    )