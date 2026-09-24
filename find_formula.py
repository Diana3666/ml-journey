import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pysr import PySRRegressor

# ============================================================
# 1. ЗАГРУЗКА
# ============================================================
df = pd.read_csv("all_cycles_final.csv")
df = df.dropna(subset=["Угол_град", "Скорость", "Время", "Напряжение_цикла", "Температура"])

df["T_gom"] = (df["Температура"] + 273.15) / 933.0
df["log_Время"] = np.log1p(df["Время"])

# ============================================================
# 2. ПРИЗНАКИ
# ============================================================
feature_names = ["Скорость", "log_Время", "Напряжение_цикла", "T_gom"]
X = df[feature_names].values
y = df["Угол_град"].values

print(f"Признаки: {feature_names}")
print(f"Примеров: {len(X)}")

# ============================================================
# 3. ЗАПУСК
# ============================================================
model = PySRRegressor(
    niterations=100,
    populations=20,
    population_size=40,
    binary_operators=["+", "-", "*", "/"],
    unary_operators=["exp", "log", "sqrt"],
    maxsize=25,
    parsimony=0.001,
    model_selection="best",
    progress=True,
    verbosity=0,
    random_state=42,
    procs=0,
)

print("\n🔍 PySR ищет формулы... (~10 минут)\n")
model.fit(X, y)

# ============================================================
# 4. ВСЕ ФОРМУЛЫ
# ============================================================
print("\n" + "="*70)
print("ВСЕ НАЙДЕННЫЕ ФОРМУЛЫ")
print("="*70)
eqs = model.equations_
print(eqs.to_string())

# ============================================================
# 5. ЛУЧШАЯ ФОРМУЛА — ПРАВИЛЬНЫЙ ВЫБОР
# ============================================================
# Выбираем по минимальному loss (без экстремальной сложности)
# Убираем самую последнюю строку, если она "залипла"
eqs_filtered = eqs[eqs["complexity"] >= 5]  # убираем слишком простые
best_idx = eqs_filtered["loss"].idxmin()
best_eq = eqs_filtered.loc[best_idx]

print("\n" + "="*70)
print("🏆 ЛУЧШАЯ ФОРМУЛА (по минимальному loss)")
print("="*70)
print(f"Сложность: {best_eq['complexity']}")
print(f"Loss (MSE): {best_eq['loss']:.4f}")
print(f"R²: {1 - best_eq['loss'] / np.var(y):.4f}")
print(f"\nФормула (PySR):\n{best_eq['equation']}")

# Переводим в читаемый вид
try:
    from sympy import sympify, symbols
    x0, x1, x2, x3 = symbols("x0 x1 x2 x3")
    eq_str = best_eq["equation"]
    print(f"\nПодставляем переменные:")
    print(f"  x0 = Скорость деформации")
    print(f"  x1 = log(Время)")
    print(f"  x2 = Напряжение (МПа)")
    print(f"  x3 = Гомологическая температура")
    
    # Простая замена
    readable = eq_str
    for old, new in [("x0", "Скорость"), ("x1", "log_Время"), 
                     ("x2", "Напряжение"), ("x3", "T_гом")]:
        readable = readable.replace(old, new)
    print(f"\nЧитаемая формула:\n{readable}")
except Exception as e:
    print(f"(не удалось конвертировать: {e})")

# ============================================================
# 6. ПРОВЕРКА И ГРАФИК
# ============================================================
y_pred = model.predict(X)
r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - y.mean())**2)

plt.figure(figsize=(10, 10))
plt.scatter(y, y_pred, alpha=0.3, s=10)
plt.plot([0, y.max()], [0, y.max()], "r--", linewidth=2, label="Идеальное")
plt.xlabel("Реальный угол (°)")
plt.ylabel("Предсказанный угол (°)")
plt.title(f"PySR: R² = {r2:.4f} (лучшая формула, сложность {best_eq['complexity']})")
plt.legend()
plt.grid(True)
plt.savefig("pysr_best.png", dpi=100)
print(f"\n✅ График: pysr_best.png")
print(f"✅ Финальный R²: {r2:.4f}")

# Сохраняем формулы
eqs.to_csv("all_formulas.csv", index=False)
print("✅ Все формулы: all_formulas.csv")