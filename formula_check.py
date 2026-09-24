import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("all_cycles_final.csv")
df = df.dropna(subset=["Угол_град", "Скорость", "Время", "Напряжение_цикла"])

df["log_Время"] = np.log1p(df["Время"])

# ============================================================
# ФОРМУЛА (наша!)
# ============================================================
def our_formula(sigma, t, v):
    """
    угол = 0.097 * exp(0.13 * sigma * (ln(t) - 5.45)) + 7.5 * v
    
    sigma: напряжение (МПа)
    t: время (сек)
    v: скорость деформации (штрих/сек)
    """
    return 0.097 * np.exp(0.13 * sigma * (np.log(t) - 5.45)) + 7.5 * v

# Применяем
df["Угол_формула"] = our_formula(
    df["Напряжение_цикла"].values,
    df["Время"].values,
    df["Скорость"].values,
)

# Метрики
from sklearn.metrics import r2_score, mean_absolute_error

r2 = r2_score(df["Угол_град"], df["Угол_формула"])
mae = mean_absolute_error(df["Угол_град"], df["Угол_формула"])

print("="*60)
print("ПРОВЕРКА ФОРМУЛЫ")
print("="*60)
print(f"R² = {r2:.4f}")
print(f"MAE = {mae:.2f}°")
print()
print("По циклам:")
for cycle in df["Цикл"].unique():
    sub = df[df["Цикл"] == cycle]
    r2_c = r2_score(sub["Угол_град"], sub["Угол_формула"])
    mae_c = mean_absolute_error(sub["Угол_град"], sub["Угол_формула"])
    print(f"  {cycle}: R² = {r2_c:.3f}, MAE = {mae_c:.2f}°")

# График по циклам
fig, axes = plt.subplots(5, 1, figsize=(14, 20))
for ax, cycle in zip(axes, df["Цикл"].unique()):
    sub = df[df["Цикл"] == cycle]
    ax.plot(sub["Время"], sub["Угол_град"], label="Реальность", alpha=0.7)
    ax.plot(sub["Время"], sub["Угол_формула"], label="Формула", alpha=0.7)
    ax.set_ylabel("Угол (°)")
    ax.set_title(f"{cycle}")
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.savefig("formula_check.png", dpi=100)
print("\n График: formula_check.png")

# Сохраняем коэффициенты
coeffs = pd.DataFrame({
    "Параметр": ["A", "B", "C", "D"],
    "Значение": [0.097, 0.71, 0.13, 7.5],
    "Смысл": [
        "Масштаб (амплитуда)",
        "Затухание от напряжения",
        "Показатель степени времени",
        "Вклад скорости",
    ],
})
coeffs.to_csv("formula_coefficients.csv", index=False)
print(" Коэффициенты: formula_coefficients.csv")