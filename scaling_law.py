import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("all_cycles_final.csv")
df = df.dropna(subset=["Угол_град", "Скорость"])

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

colors = {"cycle_45": "#1f77b4", "cycle_65": "#ff7f0e",
          "cycle_85": "#2ca02c", "cycle_105": "#d62728",
          "cycle_120": "#9467bd"}

# Панель 1: как есть
for cycle in df["Цикл"].unique():
    s = df[df["Цикл"] == cycle].sort_values("Угол_град")
    axes[0].plot(s["Угол_град"], s["Скорость"].abs(),
                 color=colors[cycle], alpha=0.7, label=cycle)

axes[0].set_xlabel("Угол (°)")
axes[0].set_ylabel("Скорость (штрих/сек)")
axes[0].set_title("Скорость vs Угол (как есть)")
axes[0].legend(); axes[0].grid(True)

# Панель 2: нормированные
for cycle in df["Цикл"].unique():
    s = df[df["Цикл"] == cycle].sort_values("Угол_град")
    # Нормируем угол: делим на характерный угол этого цикла
    theta_0 = s["Угол_град"].max()
    # Нормируем скорость: делим на характерную скорость
    v_0 = s["Скорость"].abs().max()
    
    axes[1].plot(s["Угол_град"] / theta_0, 
                 s["Скорость"].abs() / v_0,
                 color=colors[cycle], alpha=0.7, label=cycle)

axes[1].set_xlabel("Угол / θ_0 (нормированный)")
axes[1].set_ylabel("Скорость / v_0 (нормированная)")
axes[1].set_title("Scaling Law: все кривые ложатся в одну?")
axes[1].legend(); axes[1].grid(True)

plt.tight_layout()
plt.savefig("scaling_law.png", dpi=100)
print("✅ График: scaling_law.png")