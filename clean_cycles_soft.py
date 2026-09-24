import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("all_cycles.csv")

print("=== ДО ОЧИСТКИ ===")
print(f"Строк: {len(df)}")
print(f"Отрицательных углов: {(df['Угол_град'] < 0).sum()}")
print(f"Скорость > 50: {(df['Скорость'].abs() > 50).sum()}")

# --- МЯГКАЯ ОЧИСТКА ---
# 1. Убираем отрицательные углы (глюк датчика)
df_clean = df[df["Угол_град"] >= 0].copy()

# 2. Убираем нефизическую скорость (>50 штрих/сек)
df_clean = df_clean[df_clean["Скорость"].abs() <= 50]

# 3. Убираем первые 5 секунд
df_clean = df_clean[df_clean["Время"] > 5]

print("\n=== ПОСЛЕ ОЧИСТКИ ===")
print(f"Строк: {len(df_clean)}")
print(f"Удалено: {len(df) - len(df_clean)} ({(1 - len(df_clean)/len(df))*100:.1f}%)")

print("\n=== СТАТИСТИКА ПО ЦИКЛАМ ===")
print("\nУгол (в градусах):")
print(df_clean.groupby("Цикл")["Угол_град"].agg(["min", "max", "mean"]).round(2))

print("\nУгол (в оборотах, штрихи/500):")
df_clean["Угол_штрих"] = df_clean["Угол_град"] / 0.72
print(df_clean.groupby("Цикл")["Угол_штрих"].agg(["min", "max"]).round(1))

print("\nСкорость (штрих/сек):")
print(df_clean.groupby("Цикл")["Скорость"].agg(["min", "max", "mean"]).round(2))

print("\nМаксимальная температура по циклам:")
print(df_clean.groupby("Цикл")["Температура"].max().round(1))

# Сохраняем
df_clean.to_csv("all_cycles_clean.csv", index=False)
print("\n✅ Сохранено: all_cycles_clean.csv")

# --- ГРАФИКИ ---
fig, axes = plt.subplots(4, 1, figsize=(14, 14))

for cycle in df_clean["Цикл"].unique():
    s = df_clean[df_clean["Цикл"] == cycle]
    axes[0].plot(s["Время"], s["Температура"], label=cycle, alpha=0.7)
    axes[1].plot(s["Время"], s["Угол_град"], label=cycle, alpha=0.7)
    axes[2].plot(s["Время"], s["Скорость"], label=cycle, alpha=0.7)
    axes[3].plot(s["Температура"], s["Угол_град"], label=cycle, alpha=0.7)

axes[0].set_ylabel("Температура (°C)")
axes[0].set_title("Температура — все циклы")
axes[0].legend(); axes[0].grid(True)

axes[1].set_ylabel("Угол (°)")
axes[1].set_title("Угол — все циклы")
axes[1].legend(); axes[1].grid(True)

axes[2].set_ylabel("Скорость (штрих/сек)")
axes[2].set_xlabel("Время (сек)")
axes[2].set_title("Скорость деформации — твоя гипотеза!")
axes[2].legend(); axes[2].grid(True)

axes[3].set_ylabel("Угол (°)")
axes[3].set_xlabel("Температура (°C)")
axes[3].set_title("Угол vs Температура — ключевая зависимость!")
axes[3].legend(); axes[3].grid(True)

plt.tight_layout()
plt.savefig("all_cycles_clean.png", dpi=100)
print("✅ Графики: all_cycles_clean.png")