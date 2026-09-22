import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_excel("cycle_45.xlsx")   # ← ПОСТАВЬ ИМЯ ФАЙЛА УДАЧНОГО ЦИКЛА

df.columns = df.columns.str.replace("\xa0", "", regex=False).str.strip()

for col in df.columns:
    cleaned = (df[col].astype(str)
               .str.replace("\xa0", "", regex=False)
               .str.replace(" ", "", regex=False)
               .str.replace("\t", "", regex=False)
               .str.replace(",", ".", regex=False))
    df[col] = pd.to_numeric(cleaned, errors="coerce")

df = df.dropna()

# --- Переводим штрихи в угол ---
STRIPES_PER_TURN = 500
DEG_PER_STRIPE = 360 / STRIPES_PER_TURN
df["Угол_град"] = df["Деформация"] * DEG_PER_STRIPE

# --- НОВОЕ: вычисляем скорость деформации ---
df["d_Деформация"] = df["Деформация"].diff()   # изменение штрихов
df["d_Время"] = df["Время"].diff()             # изменение времени
df["Скорость_деф"] = df["d_Деформация"] / df["d_Время"]  # штрихи в секунду

print("=== СТАТИСТИКА СКОРОСТИ ===")
print(df["Скорость_деф"].describe())

# --- Строим 5 графиков ---
fig, axes = plt.subplots(5, 1, figsize=(12, 14), sharex=True)

axes[0].plot(df["Время"], df["Температура"], color="orange")
axes[0].set_ylabel("Температура (°C)")
axes[0].set_title("Температура")
axes[0].grid(True)

axes[1].plot(df["Время"], df["Напряжение"], color="red")
axes[1].set_ylabel("Напряжение (МПа)")
axes[1].set_title("Напряжение")
axes[1].grid(True)

axes[2].plot(df["Время"], df["Угол_град"], color="blue")
axes[2].set_ylabel("Угол (°)")
axes[2].set_title("Угол закручивания")
axes[2].grid(True)

axes[3].plot(df["Время"], df["Скорость_деф"], color="purple")
axes[3].set_ylabel("Скорость (штрих/сек)")
axes[3].set_title("Скорость деформации — ключевой признак!")
axes[3].grid(True)

# Общий график: температура + деформация
ax5 = axes[4]
ax5.plot(df["Время"], df["Температура"], color="orange", label="Температура")
ax5.set_ylabel("Температура (°C)", color="orange")
ax5.tick_params(axis="y", labelcolor="orange")
ax5.grid(True)

ax5_twin = ax5.twinx()
ax5_twin.plot(df["Время"], df["Угол_град"], color="blue", label="Угол")
ax5_twin.set_ylabel("Угол (°)", color="blue")
ax5_twin.tick_params(axis="y", labelcolor="blue")

axes[4].set_xlabel("Время (сек)")
axes[4].set_title("Температура vs Угол (связь!)")

plt.tight_layout()
plt.savefig("cycle_45_plots.png", dpi=100)
print("\n✅ Графики сохранены: cycle_XX_plots.png")

# --- Сохраняем обработанные данные в CSV ---
df.to_csv("cycle_45_processed.csv", index=False)
print("✅ Данные сохранены: cycle_XX_processed.csv")