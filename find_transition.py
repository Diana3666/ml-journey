import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("all_cycles_final.csv")
df = df.dropna(subset=["Угол_град", "Скорость"])

fig, axes = plt.subplots(2, 1, figsize=(14, 10))

colors = {"cycle_45": "#1f77b4", "cycle_65": "#ff7f0e",
          "cycle_85": "#2ca02c", "cycle_105": "#d62728",
          "cycle_120": "#9467bd"}

# Панель 1: скорость vs угол
for cycle in df["Цикл"].unique():
    s = df[df["Цикл"] == cycle].sort_values("Угол_град")
    axes[0].plot(s["Угол_град"], s["Скорость"].abs(),
                 color=colors.get(cycle), alpha=0.7, label=cycle)

axes[0].set_xlabel("Угол (°)")
axes[0].set_ylabel("Скорость деформации")
axes[0].set_title("Скорость деформации vs угол — где перегиб?")
axes[0].legend()
axes[0].grid(True)

# Панель 2: log(скорость) vs угол (для наглядности)
for cycle in df["Цикл"].unique():
    s = df[df["Цикл"] == cycle].sort_values("Угол_град")
    speed = s["Скорость"].abs()
    speed = speed[speed > 0.01]  # убираем нули для log
    axes[1].plot(s.loc[speed.index, "Угол_град"], np.log(speed),
                 color=colors.get(cycle), alpha=0.7, label=cycle)

axes[1].set_xlabel("Угол (°)")
axes[1].set_ylabel("log(Скорость)")
axes[1].set_title("log(Скорость) vs угол — линейные участки видны чётче")
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig("find_transition.png", dpi=100)
print("✅ График: find_transition.png")