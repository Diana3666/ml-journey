import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("all_cycles_clean.csv")

print("=== ИЩЕМ ГЛЮКИ ВО ВСЕХ ЦИКЛАХ ===\n")

# Автоматический поиск момента, где угол начинает "залипать"
# Признак: много подряд одинаковых значений угла ИЛИ резкий скачок

def find_bad_start(subset, angle_col="Угол_град", threshold=200):
    """Ищем момент, где угол резко скакнул (>threshold градусов за 1 шаг)."""
    subset = subset.reset_index(drop=True)
    subset["d_angle"] = subset[angle_col].diff()
    jumps = subset[subset["d_angle"] > threshold]
    if len(jumps) > 0:
        return jumps.index[0], jumps.iloc[0]["Время"]
    return None, None

for cycle in df["Цикл"].unique():
    subset = df[df["Цикл"] == cycle]
    idx, time = find_bad_start(subset)
    if idx is not None:
        print(f"{cycle}: скачок на строке {idx}, время {time:.1f} сек")
    else:
        print(f"{cycle}: скачков >200° не найдено")

# ============================================================
# РУЧНАЯ ОБРЕЗКА (после диагностики)
# ============================================================
trims = {
    "cycle_85": None,   # определим вручную после вывода
    "cycle_105": 415,   # уже знаем
}

print("\n=== Диагностика cycle_85 ===")
c85 = df[df["Цикл"] == "cycle_85"].copy().reset_index(drop=True)
c85["d_angle"] = c85["Угол_град"].diff()
print("Топ-5 скачков угла у cycle_85:")
print(c85.nlargest(5, "d_angle")[["Время", "Температура", "Деформация", "Угол_град", "d_angle"]])