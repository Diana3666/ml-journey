import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# ============================================================
# 1. ЗАГРУЗКА
# ============================================================
df = pd.read_csv("all_cycles_final.csv")
df = df.dropna(subset=["Угол_град", "Скорость", "Время",
                        "Напряжение_цикла", "Температура"])

# Физические признаки
df["T_gom"] = (df["Температура"] + 273.15) / 933.0
df["log_Время"] = np.log1p(df["Время"])

feature_cols = ["Температура", "Время", "Скорость",
                "T_gom", "log_Время", "Напряжение_цикла"]

X = df[feature_cols]
y = df["Угол_град"]

# ============================================================
# 2. ФОРМУЛА (наша!)
# ============================================================
def our_formula(sigma, t, v):
    """угол = 0.097 * exp(0.13 * σ * (ln(t) - 5.45)) + 7.5 * v"""
    return 0.097 * np.exp(0.13 * sigma * (np.log1p(t) - 5.45)) + 7.5 * v

df["Угол_формула"] = our_formula(
    df["Напряжение_цикла"].values,
    df["Время"].values,
    df["Скорость"].values,
)

# ============================================================
# 3. ОБУЧАЕМ RANDOM FOREST (для важности признаков)
# ============================================================
rf = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
rf.fit(X, y)
df["Угол_RF"] = rf.predict(X)

# Метрики
r2_formula = r2_score(y, df["Угол_формула"])
mae_formula = mean_absolute_error(y, df["Угол_формула"])
r2_rf = r2_score(y, df["Угол_RF"])
mae_rf = mean_absolute_error(y, df["Угол_RF"])

print("=" * 60)
print("МЕТРИКИ ДЛЯ СТАТЬИ")
print("=" * 60)
print(f"Формула:      R² = {r2_formula:.4f}, MAE = {mae_formula:.2f}°")
print(f"Random Forest: R² = {r2_rf:.4f}, MAE = {mae_rf:.2f}°")

# ============================================================
# 4. СОБИРАЕМ ФИГУРУ (2 x 2)
# ============================================================
fig = plt.figure(figsize=(16, 12))
gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.25)

colors = {
    "cycle_45":  "#1f77b4",
    "cycle_65":  "#ff7f0e",
    "cycle_85":  "#2ca02c",
    "cycle_105": "#d62728",
    "cycle_120": "#9467bd",
}

# ------------------------------------------------------------
# ПАНЕЛЬ 1: Все циклы с формулой
# ------------------------------------------------------------
ax1 = fig.add_subplot(gs[0, :])

for cycle in df["Цикл"].unique():
    s = df[df["Цикл"] == cycle].sort_values("Время")
    color = colors.get(cycle, "gray")
    ax1.plot(s["Время"], s["Угол_град"], color=color, linewidth=1.5,
             alpha=0.9, label=f"{cycle} (эксперимент)")
    ax1.plot(s["Время"], s["Угол_формула"], color=color, linewidth=1.5,
             linestyle="--", alpha=0.7)

ax1.set_xlabel("Время (с)", fontsize=12)
ax1.set_ylabel("Угол закручивания (°)", fontsize=12)
ax1.set_title("(a) Эксперимент (сплошные) vs формула (пунктир)",
              fontsize=13, fontweight="bold")
ax1.grid(True, alpha=0.3)
ax1.legend(loc="upper left", fontsize=10, ncol=2)

# Аннотация
ax1.text(0.98, 0.05, f"R² = {r2_formula:.3f}, MAE = {mae_formula:.1f}°",
         transform=ax1.transAxes, fontsize=11, ha="right", va="bottom",
         bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7))

# ------------------------------------------------------------
# ПАНЕЛЬ 2: Важность признаков (RF)
# ------------------------------------------------------------
ax2 = fig.add_subplot(gs[1, 0])

importances = rf.feature_importances_
sorted_idx = np.argsort(importances)

# Красивые имена
nice_names = {
    "Температура": "Температура",
    "Время": "Время",
    "Скорость": "Скорость деформации",
    "T_gom": "T/T_пл",
    "log_Время": "log(Время)",
    "Напряжение_цикла": "Напряжение",
}

labels = [nice_names.get(feature_cols[i], feature_cols[i]) for i in sorted_idx]
values = importances[sorted_idx]

bars = ax2.barh(labels, values, color="#2ca02c", alpha=0.8)
ax2.set_xlabel("Важность признака", fontsize=12)
ax2.set_title("(b) Важность признаков (Random Forest)",
              fontsize=13, fontweight="bold")
ax2.grid(True, alpha=0.3, axis="x")

# Значения на барах
for bar, val in zip(bars, values):
    ax2.text(val + 0.01, bar.get_y() + bar.get_height() / 2,
             f"{val:.3f}", va="center", fontsize=10)

# ------------------------------------------------------------
# ПАНЕЛЬ 3: Предсказание vs реальность
# ------------------------------------------------------------
ax3 = fig.add_subplot(gs[1, 1])

ax3.scatter(y, df["Угол_формула"], alpha=0.3, s=8, color="#1f77b4",
            label="Формула")
ax3.scatter(y, df["Угол_RF"], alpha=0.2, s=8, color="#2ca02c",
            label="Random Forest")

lims = [0, max(y.max(), df["Угол_формула"].max()) * 1.05]
ax3.plot(lims, lims, "r--", linewidth=2, label="Идеальное")

ax3.set_xlim(lims)
ax3.set_ylim(lims)
ax3.set_xlabel("Реальный угол (°)", fontsize=12)
ax3.set_ylabel("Предсказанный угол (°)", fontsize=12)
ax3.set_title("(c) Предсказание vs эксперимент",
              fontsize=13, fontweight="bold")
ax3.legend(loc="upper left", fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_aspect("equal")

# ------------------------------------------------------------
# ПАНЕЛЬ 4: Остатки
# ------------------------------------------------------------
# Создаём 4-ю ось вручную поверх грида
ax4 = fig.add_subplot(gs[1, :])
ax4.remove()  # убираем — переделаем сетку

# Пересобираем фигуру с 3 строками
fig.clear()
gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.25,
              height_ratios=[1, 1, 1])

# Панель 1 — на всю ширину
ax1 = fig.add_subplot(gs[0, :])
for cycle in df["Цикл"].unique():
    s = df[df["Цикл"] == cycle].sort_values("Время")
    color = colors.get(cycle, "gray")
    ax1.plot(s["Время"], s["Угол_град"], color=color, linewidth=1.5,
             alpha=0.9, label=f"{cycle}")
    ax1.plot(s["Время"], s["Угол_формула"], color=color, linewidth=1.5,
             linestyle="--", alpha=0.7)

ax1.set_xlabel("Время (с)", fontsize=12)
ax1.set_ylabel("Угол (°)", fontsize=12)
ax1.set_title("(a) Эксперимент (сплошные) vs формула (пунктир)",
              fontsize=13, fontweight="bold")
ax1.grid(True, alpha=0.3)
ax1.legend(loc="upper left", fontsize=9, ncol=5)
ax1.text(0.98, 0.05, f"R² = {r2_formula:.3f}, MAE = {mae_formula:.1f}°",
         transform=ax1.transAxes, fontsize=11, ha="right", va="bottom",
         bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7))

# Панель 2 — важность признаков
ax2 = fig.add_subplot(gs[1, 0])
bars = ax2.barh(labels, values, color="#2ca02c", alpha=0.8)
ax2.set_xlabel("Важность", fontsize=12)
ax2.set_title("(b) Важность признаков (RF)", fontsize=13, fontweight="bold")
ax2.grid(True, alpha=0.3, axis="x")
for bar, val in zip(bars, values):
    ax2.text(val + 0.01, bar.get_y() + bar.get_height() / 2,
             f"{val:.3f}", va="center", fontsize=10)

# Панель 3 — предсказание vs реальность
ax3 = fig.add_subplot(gs[1, 1])
ax3.scatter(y, df["Угол_формула"], alpha=0.3, s=8, color="#1f77b4",
            label="Формула")
ax3.scatter(y, df["Угол_RF"], alpha=0.2, s=8, color="#2ca02c",
            label="Random Forest")
lims = [0, max(y.max(), df["Угол_формула"].max()) * 1.05]
ax3.plot(lims, lims, "r--", linewidth=2, label="Идеальное")
ax3.set_xlim(lims); ax3.set_ylim(lims)
ax3.set_xlabel("Реальный угол (°)", fontsize=12)
ax3.set_ylabel("Предсказанный (°)", fontsize=12)
ax3.set_title("(c) Предсказание vs эксперимент", fontsize=13, fontweight="bold")
ax3.legend(loc="upper left", fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_aspect("equal")

# Панель 4 — остатки
ax4 = fig.add_subplot(gs[2, :])

for cycle in df["Цикл"].unique():
    s = df[df["Цикл"] == cycle].sort_values("Время")
    color = colors.get(cycle, "gray")
    residuals = s["Угол_град"] - s["Угол_формула"]
    ax4.plot(s["Время"], residuals, color=color, linewidth=1,
             alpha=0.8, label=cycle)

ax4.axhline(0, color="black", linewidth=1.5, linestyle="-")
ax4.fill_between(df["Время"].sort_values(),
                 -mae_formula, mae_formula,
                 color="gray", alpha=0.15, label=f"±MAE ({mae_formula:.1f}°)")

ax4.set_xlabel("Время (с)", fontsize=12)
ax4.set_ylabel("Остаток (эксп. − формула), °", fontsize=12)
ax4.set_title("(d) Остатки модели", fontsize=13, fontweight="bold")
ax4.grid(True, alpha=0.3)
ax4.legend(loc="upper right", fontsize=9, ncol=2)

# Сохраняем
plt.savefig("final_report.png", dpi=150, bbox_inches="tight",
            facecolor="white")
print("\n✅ Финальный отчёт: final_report.png")

# Дополнительно — статистика остатков
residuals_all = y - df["Угол_формула"]
print("\n=== СТАТИСТИКА ОСТАТКОВ ===")
print(f"Средний остаток: {residuals_all.mean():.2f}° (должен быть ~0)")
print(f"Стд. отклонение: {residuals_all.std():.2f}°")
print(f"Макс. переоценка: {residuals_all.min():.2f}°")
print(f"Макс. недооценка: {residuals_all.max():.2f}°")