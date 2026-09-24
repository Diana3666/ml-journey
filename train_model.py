import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# ============================================================
# 1. ЗАГРУЗКА
# ============================================================
df = pd.read_csv("all_cycles_clean.csv")

# ============================================================
# 2. ОБРЕЗКА ГЛЮКОВ
# ============================================================
trims = {
    "cycle_85": 452,     # обрезаем до глюка (465.6 сек)
    "cycle_105": 415,    # обрезаем до глюка (431.2 сек)
}

for cycle, max_time in trims.items():
    mask = df["Цикл"] == cycle
    df = df[~mask | (df["Время"] <= max_time)]

print("=== ПОСЛЕ ОБРЕЗКИ ===")
print(df.groupby("Цикл").agg({
    "Время": "max",
    "Температура": "max",
    "Угол_град": "max",
    "Скорость": ["max", "mean"]
}).round(2))

# ============================================================
# 3. ПРИЗНАКИ
# ============================================================
# Используем ВСЕ физические признаки
df["T_гом"] = (df["Температура"] + 273.15) / 933
df["log_Время"] = np.log1p(df["Время"])

feature_cols = [
    "Температура",
    "Время",
    "Скорость",
    "T_гом",
    "log_Время",
    "Напряжение_цикла",
]

# Убираем NaN
df = df.dropna(subset=feature_cols + ["Угол_град"])

# ============================================================
# 4. ЧЕСТНОЕ РАЗДЕЛЕНИЕ: train = 4 цикла, test = 1 цикл
# ============================================================
print("\n=== СТРАТЕГИЯ РАЗДЕЛЕНИЯ ===")
print("Train: cycle_45, cycle_65, cycle_85, cycle_105")
print("Test:  cycle_120 (модель НЕ видела этот цикл)")

train_cycles = ["cycle_45", "cycle_65", "cycle_85", "cycle_105"]
test_cycle = "cycle_120"

df_train = df[df["Цикл"].isin(train_cycles)]
df_test = df[df["Цикл"] == test_cycle]

X_train = df_train[feature_cols]
y_train = df_train["Угол_град"]
X_test = df_test[feature_cols]
y_test = df_test["Угол_град"]

print(f"\nОбучающих: {len(X_train)} строк")
print(f"Тестовых:  {len(X_test)} строк")

# ============================================================
# 5. МОДЕЛИ
# ============================================================
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, random_state=42),
}

print("\n" + "="*60)
print("РЕЗУЛЬТАТЫ НА ТЕСТОВОМ ЦИКЛЕ 120 МПа")
print("="*60)

results = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    results[name] = {"R²": r2, "MAE": mae, "model": model, "y_pred": y_pred}
    
    print(f"\n{name}:")
    print(f"  R²  = {r2:.4f}")
    print(f"  MAE = {mae:.2f}°")

# ============================================================
# 6. ВАЖНОСТЬ ПРИЗНАКОВ
# ============================================================
best_model = results["Random Forest"]["model"]
print("\n=== ВАЖНОСТЬ ПРИЗНАКОВ (Random Forest) ===")
for name, imp in sorted(zip(feature_cols, best_model.feature_importances_), 
                         key=lambda x: -x[1]):
    print(f"  {name}: {imp:.4f}")

# ============================================================
# 7. ГРАФИКИ
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for ax, (name, res) in zip(axes, results.items()):
    y_pred = res["y_pred"]
    ax.scatter(y_test, y_pred, alpha=0.3, s=10)
    ax.plot([0, y_test.max()], [0, y_test.max()], "r--", label="Идеальное")
    ax.set_xlabel("Реальный угол (°)")
    ax.set_ylabel("Предсказанный угол (°)")
    ax.set_title(f"{name}\nR²={res['R²']:.3f}, MAE={res['MAE']:.1f}°")
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.savefig("model_compare.png", dpi=100)
print("\n✅ График сохранён: model_compare.png")

# Сохраняем финальный датасет
df.to_csv("all_cycles_final.csv", index=False)
print("✅ Финальные данные: all_cycles_final.csv")