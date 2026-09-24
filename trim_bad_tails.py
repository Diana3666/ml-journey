import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("all_cycles_clean.csv")

print("=== ДО ОБРЕЗКИ ===")
print(df.groupby("Цикл").agg({
    "Время": "max",
    "Температура": "max",
    "Угол_град": "max",
    "Скорость": "max"
}).round(2))

# ============================================================
# ОБРЕЗКА
# ============================================================
trims = {
    "cycle_105": 415,   # до скачка времени
    # cycle_120 — определим ниже
}

# Узнаём, где заканчивается cycle_120 физически
# Ищем момент, когда d_angle/dt становится невозможным
print("\n=== Поиск аномалии в cycle_120 ===")
c120 = df[df["Цикл"] == "cycle_120"].copy().reset_index(drop=True)
c120["d_angle"] = c120["Угол_град"].diff()
c120["d_time"] = c120["Время"].diff()
c120["rate"] = c120["d_angle"] / c120["d_time"]

# Смотрим топ-10 по скорости роста
print("\nТоп-10 скачков угла у cycle_120:")
print(c120.nlargest(10, "d_angle")[["Время", "Температура", "Деформация", "Угол_град", "d_angle"]])

# ============================================================
# ПРИМЕНЯЕМ ОБРЕЗКУ
# ============================================================
df_trimmed = df.copy()

for cycle, max_time in trims.items():
    mask = df_trimmed["Цикл"] == cycle
    before = mask.sum()
    df_trimmed = df_trimmed[~mask | (df_trimmed["Время"] <= max_time)]
    after = (df_trimmed["Цикл"] == cycle).sum()
    print(f"\n{cycle}: {before} → {after} строк (обрезано до {max_time} сек)")

print("\n=== ПОСЛЕ ОБРЕЗКИ ===")
print(df_trimmed.groupby("Цикл").agg({
    "Время": "max",
    "Температура": "max",
    "Угол_град": "max",
    "Скорость": "max"
}).round(2))

# Сохраняем
df_trimmed.to_csv("all_cycles_trimmed.csv", index=False)
print("\n✅ Сохранено: all_cycles_trimmed.csv")

# ============================================================
# ГРАФИКИ ПОСЛЕ ОБРЕЗКИ
# ============================================================
fig, axes = plt.subplots(4, 1, figsize=(14, 14))

for cycle in df_trimmed["Цикл"].unique():
    s = df_trimmed[df_trimmed["Цикл"] == cycle]
    axes[0].plot(s["Время"], s["Температура"], label=cycle, alpha=0.7)
    axes[1].plot(s["Время"], s["Угол_град"], label=cycle, alpha=0.7)
    axes[2].plot(s["Время"], s["Скорость"], label=cycle, alpha=0.7)
    axes[3].plot(s["Температура"], s["Угол_град"], label=cycle, alpha=0.7)

axes[0].set_ylabel("Температура (°C)")
axes[0].set_title("Температура — после обрезки")
axes[0].legend(); axes[0].grid(True)

axes[1].set_ylabel("Угол (°)")
axes[1].set_title("Угол — после обрезки")
axes[1].legend(); axes[1].grid(True)

axes[2].set_ylabel("Скорость (штрих/сек)")
axes[2].set_xlabel("Время (сек)")
axes[2].set_title("Скорость — после обрезки")
axes[2].legend(); axes[2].grid(True)

axes[3].set_ylabel("Угол (°)")
axes[3].set_xlabel("Температура (°C)")
axes[3].set_title("Угол vs Температура — после обрезки")
axes[3].legend(); axes[3].grid(True)

plt.tight_layout()
plt.savefig("all_cycles_trimmed.png", dpi=100)
print(" Графики: all_cycles_trimmed.png")