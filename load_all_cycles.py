import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============================================================
# ЗАГРУЖАЕМ ВСЕ 5 ЦИКЛОВ
# ============================================================
files = {
    "cycle_45.xlsx": 45,
    "cycle_65.xlsx": 65,
    "cycle_85.xlsx": 85,
    "cycle_105.xlsx": 105,
    "cycle_120.xlsx": 120,
}

all_data = []

for filename, stress in files.items():
    try:
        df = pd.read_excel(filename)
        df.columns = df.columns.str.replace("\xa0", "", regex=False).str.strip()

        # Чистка данных
        for col in df.columns:
            cleaned = (df[col].astype(str)
                       .str.replace("\xa0", "", regex=False)
                       .str.replace(" ", "", regex=False)
                       .str.replace(",", ".", regex=False))
            df[col] = pd.to_numeric(cleaned, errors="coerce")

        df = df.dropna()

        # Добавляем столбцы: Напряжение (из имени файла), Цикл
        df["Напряжение_цикла"] = stress
        df["Цикл"] = filename.replace(".xlsx", "")

        # Угол
        df["Угол_град"] = df["Деформация"] * 360 / 500

        # Скорость (СГЛАЖЕННАЯ!)
        df["d_Д"] = df["Деформация"].diff()
        df["d_В"] = df["Время"].diff()
        df["Скорость_raw"] = df["d_Д"] / df["d_В"]
        df["Скорость"] = df["Скорость_raw"].rolling(30, min_periods=1).mean()

        # Логарифм времени (чтобы ловить «сжатие/растяжение»)
        df["log_Время"] = np.log1p(df["Время"])

        # Гомологическая температура
        df["T_гом"] = (df["Температура"] + 273.15) / 933

        df = df.fillna(0)

        all_data.append(df)
        print(f"✅ {filename}: {len(df)} строк, {stress} МПа")

    except FileNotFoundError:
        print(f"❌ {filename}: НЕ НАЙДЕН")
    except Exception as e:
        print(f"❌ {filename}: {e}")

# ============================================================
# ОБЪЕДИНЯЕМ
# ============================================================
df_all = pd.concat(all_data, ignore_index=True)

print(f"\n=== ОБЪЕДИНЕНО ===")
print(f"Всего строк: {len(df_all)}")
print(f"Циклов: {df_all['Цикл'].nunique()}")
print("\nСтатистика по циклам:")
print(df_all.groupby("Цикл")[["Температура", "Угол_град", "Скорость"]].agg(
    ["min", "max", "mean"]
).round(2))

# Сохраняем
df_all.to_csv("all_cycles.csv", index=False)
print("\n✅ Сохранено: all_cycles.csv")

# ============================================================
# ГРАФИКИ ПО ВСЕМ ЦИКЛАМ
# ============================================================
fig, axes = plt.subplots(3, 1, figsize=(14, 12))

for cycle in df_all["Цикл"].unique():
    subset = df_all[df_all["Цикл"] == cycle]
    axes[0].plot(subset["Время"], subset["Температура"], label=cycle, alpha=0.7)
    axes[1].plot(subset["Время"], subset["Угол_град"], label=cycle, alpha=0.7)
    axes[2].plot(subset["Время"], subset["Скорость"], label=cycle, alpha=0.7)

axes[0].set_ylabel("Температура (°C)")
axes[0].set_title("Температура — все циклы")
axes[0].legend()
axes[0].grid(True)

axes[1].set_ylabel("Угол (°)")
axes[1].set_title("Угол закручивания — все циклы")
axes[1].legend()
axes[1].grid(True)

axes[2].set_ylabel("Скорость деформации")
axes[2].set_xlabel("Время (сек)")
axes[2].set_title("СКОРОСТЬ ДЕФОРМАЦИИ — твоя гипотеза!")
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.savefig("all_cycles_plots.png", dpi=100)
print("✅ Графики: all_cycles_plots.png")