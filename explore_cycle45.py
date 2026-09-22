import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_excel("cycle_45.xlsx")

df.columns = df.columns.str.replace("\xa0", "", regex=False).str.strip()

for col in df.columns:
    cleaned = (df[col].astype(str)
               .str.replace("\xa0", "", regex=False)
               .str.replace(" ", "", regex=False)
               .str.replace("\t", "", regex=False)
               .str.replace(",", ".", regex=False))
    df[col] = pd.to_numeric(cleaned, errors="coerce")

df = df.dropna()

print("=== РАЗМЕР ===")
print(df.shape)
print("\n=== СТАТИСТИКА ===")
print(df.describe())

STRIPES_PER_TURN = 500
DEG_PER_STRIPE = 360 / STRIPES_PER_TURN
df["Угол_град"] = df["Деформация"] * DEG_PER_STRIPE

print(f"\nМаксимум штрихов: {df['Деформация'].max()}")
print(f"Максимальный угол: {df['Угол_град'].max():.2f}°")

fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

axes[0].plot(df["Время"], df["Напряжение"], color="red", linewidth=0.8)
axes[0].set_ylabel("Напряжение (МПа)")
axes[0].set_title("Напряжение от времени")
axes[0].grid(True)

axes[1].plot(df["Время"], df["Температура"], color="orange", linewidth=0.8)
axes[1].set_ylabel("Температура (°C)")
axes[1].set_title("Температура от времени")
axes[1].grid(True)

axes[2].plot(df["Время"], df["Деформация"], color="green",
             drawstyle="steps-post", linewidth=0.8)
axes[2].set_ylabel("Деформация (штрихи)")
axes[2].set_title("Деформация (накопленная)")
axes[2].grid(True)

axes[3].plot(df["Время"], df["Угол_град"], color="blue", linewidth=0.8)
axes[3].set_ylabel("Угол (°)")
axes[3].set_xlabel("Время (сек)")
axes[3].set_title("Угол закручивания")
axes[3].grid(True)

plt.tight_layout()
plt.savefig("cycle45_plots.png", dpi=100)
print("\n✅ Графики сохранены в файл: cycle45_plots.png")
