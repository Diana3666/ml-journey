import pandas as pd
import numpy as np
import joblib
import os
os.makedirs("models", exist_ok=True)
from sklearn.ensemble import RandomForestRegressor

# Загрузка и подготовка (как в train_model.py)
df = pd.read_csv("all_cycles_final.csv")
df["T_gom"] = (df["Температура"] + 273.15) / 933.0
df["log_Время"] = np.log1p(df["Время"])

feature_cols = ["Температура", "Время", "Скорость",
                "T_gom", "log_Время", "Напряжение_цикла"]

X = df[feature_cols]
y = df["Угол_град"]

# Обучение на ВСЕХ данных
model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X, y)

# Сохранение
joblib.dump(model, "models/model.pkl")
print("✅ Модель сохранена: models/model.pkl")

# Сохраняем список признаков — важно!
joblib.dump(feature_cols, "models/feature_cols.pkl")