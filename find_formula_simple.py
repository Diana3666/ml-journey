import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pysr import PySRRegressor

df = pd.read_csv("all_cycles_final.csv")
df = df.dropna(subset=["Угол_град", "Скорость", "Время"])

# ТОЛЬКО 3 ГЛАВНЫХ ПРИЗНАКА
df["T_gom"] = (df["Температура"] + 273.15) / 933.0
df["log_Время"] = np.log1p(df["Время"])

feature_names = ["Скорость", "log_Время", "Напряжение_цикла"]
X = df[feature_names].values
y = df["Угол_град"].values

print(f"Признаки: {feature_names}")
print(f"Примеров: {len(X)}")

model = PySRRegressor(
    niterations=150,
    populations=25,
    population_size=40,
    binary_operators=["+", "-", "*", "/"],
    unary_operators=["exp", "log", "sqrt"],   # без sin/cos
    maxsize=15,                              # ← ОГРАНИЧИВАЕМ сложность!
    parsimony=0.01,                          # ← сильно штрафуем сложность
    model_selection="best",
    progress=True,
    verbosity=0,
    random_state=42,
    procs=0,
)

print("\n🔍 PySR ищет ПРОСТУЮ формулу (~10 минут)\n")
model.fit(X, y)

eqs = model.equations_
print("\n=== ВСЕ ФОРМУЛЫ ===")
print(eqs.to_string())

# Берём формулу со сложностью 8-12
eqs_simple = eqs[(eqs["complexity"] >= 6) & (eqs["complexity"] <= 14)]
if len(eqs_simple) > 0:
    best_idx = eqs_simple["loss"].idxmin()
    best = eqs_simple.loc[best_idx]
    
    print("\n" + "="*70)
    print(f"🏆 ПРОСТАЯ ФОРМУЛА (сложность {best['complexity']})")
    print("="*70)
    print(f"Loss: {best['loss']:.4f}")
    print(f"R²: {1 - best['loss'] / np.var(y):.4f}")
    print(f"\n{best['equation']}")
    
    # Читаемый вид
    readable = best["equation"]
    for old, new in [("x0", "Скорость"), ("x1", "log_Время"), ("x2", "Напряжение")]:
        readable = readable.replace(old, new)
    print(f"\nЧитаемая:\n{readable}")
    
    # График
    y_pred = model.predict(X)
    r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - y.mean())**2)
    
    plt.figure(figsize=(10, 10))
    plt.scatter(y, y_pred, alpha=0.3, s=10)
    plt.plot([0, y.max()], [0, y.max()], "r--", linewidth=2, label="Идеальное")
    plt.xlabel("Реальный угол (°)")
    plt.ylabel("Предсказанный угол (°)")
    plt.title(f"PySR простой: R² = {r2:.4f} (сложность {best['complexity']})")
    plt.legend(); plt.grid(True)
    plt.savefig("pysr_simple.png", dpi=100)
    print("\n✅ График: pysr_simple.png")