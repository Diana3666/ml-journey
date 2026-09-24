import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("all_cycles_final.csv")
df = df.dropna(subset=["Угол_град", "Скорость"])

# Параметры образца
r = 2.0    # мм
L = 40.0   # мм

# Пересчёт угла в деформацию сдвига
# γ = (φ[рад] · r) / L
df["gamma_rad"] = df["Угол_град"] * np.pi / 180
df["gamma_percent"] = (df["gamma_rad"] * r / L) * 100

# Скорость деформации
df["gamma_dot"] = df["Скорость"] * np.pi / 180 * r / L * 100  # %/сек

print("=== ДЕФОРМАЦИЯ В % ===")
print(df.groupby("Цикл")["gamma_percent"].agg(["min", "max", "mean"]).round(2))

print("\n=== СКОРОСТЬ ДЕФОРМАЦИИ (%/сек) ===")
print(df.groupby("Цикл")["gamma_dot"].agg(["min", "max", "mean"]).round(3))

# Графики
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

colors = {"cycle_45": "#1f77b4", "cycle_65": "#ff7f0e",
          "cycle_85": "#2ca02c", "cycle_105": "#d62728",
          "cycle_120": "#9467bd"}

for cycle in df["Цикл"].unique():
    s = df[df["Цикл"] == cycle].sort_values("Время")
    axes[0].plot(s["Время"], s["gamma_percent"], 
                 color=colors[cycle], alpha=0.7, label=cycle)
    axes[1].plot(s["gamma_percent"], s["gamma_dot"].abs(),
                 color=colors[cycle], alpha=0.7, label=cycle)

axes[0].set_xlabel("Время (с)")
axes[0].set_ylabel("Деформация сдвига γ (%)")
axes[0].set_title(f"Деформация сдвига (r={r} мм, L={L} мм)")
axes[0].legend()
axes[0].grid(True)

axes[1].set_xlabel("γ (%)")
axes[1].set_ylabel("Скорость γ̇ (%/сек)")
axes[1].set_title("Скорость деформации vs деформация")
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig("deformation_recalc.png", dpi=100)
print("\n✅ Графики: deformation_recalc.png")