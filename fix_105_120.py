import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("all_cycles_clean.csv")

print("=== ДИАГНОСТИКА cycle_105 и cycle_120 ===\n")

for cycle_name in ["cycle_105", "cycle_120"]:
    print(f"\n{'='*60}")
    print(f"ЦИКЛ: {cycle_name}")
    print(f"{'='*60}")
    
    subset = df[df["Цикл"] == cycle_name].copy().reset_index(drop=True)
    
    print(f"\nПервые 5 строк:")
    print(subset[["Время", "Температура", "Деформация", "Угол_град"]].head())
    
    print(f"\nСтроки 50-55:")
    print(subset.iloc[50:55][["Время", "Температура", "Деформация", "Угол_град"]].to_string())
    
    print(f"\nСтроки 200-205:")
    print(subset.iloc[200:205][["Время", "Температура", "Деформация", "Угол_град"]].to_string())
    
    # Ищем, где угол резко улетает
    subset["d_angle"] = subset["Угол_град"].diff()
    big_jumps = subset[subset["d_angle"] > 100]
    
    print(f"\nРезкие скачки угла (>100°): {len(big_jumps)}")
    if len(big_jumps) > 0:
        print(f"Первый скачок на строке: {big_jumps.index[0]}")
        print(f"Значения до скачка:")
        print(subset.iloc[max(0, big_jumps.index[0]-2):big_jumps.index[0]+2][
            ["Время", "Температура", "Деформация", "Угол_град"]
        ].to_string())