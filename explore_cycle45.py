import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

# ============================================================
# 1. ЗАГРУЗКА И ЧИСТКА
# ============================================================
df = pd.read_excel("cycle_45.xlsx")
df.columns = df.columns.str.replace("\xa0", "", regex=False).str.strip()

for col in df.columns:
    cleaned = (df[col].astype(str)
               .str.replace("\xa0", "", regex=False)
               .str.replace(" ", "", regex=False)
               .str.replace(",", ".", regex=False))
    df[col] = pd.to_numeric(cleaned, errors="coerce")

df = df.dropna()

# ============================================================
# 2. FEATURE ENGINEERING
# ============================================================
df["Угол_град"] = df["Деформация"] * 360 / 500

# Скорость деформации (сглаженная в окне 10 точек)
df["d_Д"] = df["Деформация"].diff()
df["d_В"] = df["Время"].diff()
df["Скорость"] = (df["d_Д"] / df["d_В"]).rolling(10, min_periods=1).mean()

# Гомологическая температура
df["T_гом"] = (df["Температура"] + 273.15) / 933

df = df.fillna(0)
df = df[df["Время"] > 5]   # убираем первые секунды

print("=== ДАННЫЕ ГОТОВЫ ===")
print(f"Строк: {len(df)}")
print(df[["Температура", "Время", "Напряжение", "Угол_град", "Скорость"]].describe())

# ============================================================
# 3. X и y
# ============================================================
feature_cols = ["Температура", "Время", "Напряжение", "Скорость"]
X = df[feature_cols]
y = df["Угол_град"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nОбучающих примеров: {len(X_train)}")
print(f"Тестовых примеров: {len(X_test)}")

# ============================================================
# 4. МОДЕЛЬ 1: Линейная регрессия (baseline)
# ============================================================
print("\n=== LINEAR REGRESSION ===")
lr = LinearRegression()
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)

print(f"R² = {r2_score(y_test, y_pred_lr):.4f}")
print(f"MAE = {mean_absolute_error(y_test, y_pred_lr):.2f}°")
print("\nКоэффициенты (что важнее):")
for name, coef in zip(feature_cols, lr.coef_):
    print(f"  {name}: {coef:+.4f}")

# ============================================================
# 5. МОДЕЛЬ 2: Random Forest
# ============================================================
print("\n=== RANDOM FOREST ===")
rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)

print(f"R² = {r2_score(y_test, y_pred_rf):.4f}")
print(f"MAE = {mean_absolute_error(y_test, y_pred_rf):.2f}°")
print("\nВажность признаков:")
for name, imp in sorted(zip(feature_cols, rf.feature_importances_),
                         key=lambda x: -x[1]):
    print(f"  {name}: {imp:.4f}")

# ============================================================
# 6. ГРАФИК ПРЕДСКАЗАНИЙ
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].scatter(y_test, y_pred_lr, alpha=0.3, color="blue")
axes[0].plot([0, 160], [0, 160], "r--", label="Идеальное предсказание")
axes[0].set_xlabel("Реальный угол (°)")
axes[0].set_ylabel("Предсказанный угол (°)")
axes[0].set_title(f"Linear Regression (R²={r2_score(y_test, y_pred_lr):.3f})")
axes[0].legend()
axes[0].grid(True)

axes[1].scatter(y_test, y_pred_rf, alpha=0.3, color="green")
axes[1].plot([0, 160], [0, 160], "r--", label="Идеальное предсказание")
axes[1].set_xlabel("Реальный угол (°)")
axes[1].set_ylabel("Предсказанный угол (°)")
axes[1].set_title(f"Random Forest (R²={r2_score(y_test, y_pred_rf):.3f})")
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig("first_model.png", dpi=100)
print("\n График сохранён: first_model.png")