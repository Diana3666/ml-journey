import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============================================================
# 1. ЗАГРУЗКА И ПОДГОТОВКА (как в train_model.py)
# ============================================================
df = pd.read_csv("all_cycles_final.csv")

# Очистка (если нужно)
df = df.dropna(subset=["Угол_град", "Скорость", "Время", "Напряжение_цикла", "Температура"])

# Создаём физические признаки
df["T_gom"] = (df["Температура"] + 273.15) / 933.0
df["log_Время"] = np.log1p(df["Время"])

# ============================================================
# 2. ВЫБИРАЕМ ПРИЗНАКИ ДЛЯ ПОИСКА
# ============================================================
# Начнём с САМЫХ ВАЖНЫХ (по результатам RF)
feature_names = ["Скорость", "log_Время", "Напряжение_цикла", "T_gom"]
X = df[feature_names].values
y = df["Угол_град"].values

print("Данные для поиска формулы:")
print(f"  Признаки: {feature_names}")
print(f"  Цель: Угол_град")
print(f"  Примеров: {len(X)}")

# ============================================================
# 3. ЗАПУСКАЕМ PYSR
# ============================================================
from pysr import PySRRegressor

print("\n🔍 PySR начинает поиск формулы... (это может занять 5-15 минут)")



model = PySRRegressor(
    niterations=200,                    # ← было 40, стало 200
    populations=30,                     # ← было 15
    population_size=50,
    
    binary_operators=["+", "-", "*", "/"],
    unary_operators=["exp", "log", "sqrt"],   # ← убрал sin, cos
    
    maxsize=25,                         # ← было 20
    
    # --- НОВОЕ: настройки для лучшего поиска ---
    parsimony=0.001,                    # ← штраф за сложность
    constraints={"sqrt": 5, "log": 5, "exp": 5},  # ← ограничения
    
    model_selection="best",
    progress=True,
    verbosity=1,
    temp_equation_file=True,
    random_state=42,
    
    # Ускорение
    procs=0,                            # ← все ядра CPU
)

model.fit(X, y)
# ============================================================
# 4. ВЫВОД РЕЗУЛЬТАТОВ
# ============================================================
print("\n" + "="*60)
print("НАЙДЕННЫЕ ФОРМУЛЫ (от простых к сложным)")
print("="*60)

print(model)

# ============================================================
# 5. ЛУЧШАЯ ФОРМУЛА
# ============================================================
best_idx = model.equations_.index[model.equations_["score"].idxmax()]
best_eq = model.equations_.iloc[best_idx]

print("\n" + "="*60)
print("🏆 ЛУЧШАЯ ФОРМУЛА")
print("="*60)
print(f"Сложность: {best_eq['complexity']}")
print(f"Loss (MSE): {best_eq['loss']:.4f}")
print(f"R²: {1 - best_eq['loss'] / np.var(y):.4f}")
print(f"\nФормула:\n{best_eq['equation']}")

# ============================================================
# 6. ГРАФИК СРАВНЕНИЯ
# ============================================================
y_pred = model.predict(X)

plt.figure(figsize=(8, 8))
plt.scatter(y, y_pred, alpha=0.3, s=10, label="Предсказание PySR")
plt.plot([0, y.max()], [0, y.max()], "r--", label="Идеальное")
plt.xlabel("Реальный угол (°)")
plt.ylabel("Предсказанный угол (°)")
plt.title(f"PySR: R² = {1 - best_eq['loss'] / np.var(y):.4f}")
plt.legend()
plt.grid(True)
plt.savefig("pysr_result.png", dpi=100)
print("\n✅ График сохранён: pysr_result.png")

# Сохраняем все найденные формулы
model.equations_.to_csv("found_formulas.csv", index=False)
print("✅ Все формулы сохранены: found_formulas.csv")