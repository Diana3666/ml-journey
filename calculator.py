print("=== Калькулятор ===")
n = float(input("Введи число n"))
m = float(input("Введи число m"))
op = input("Выбери операцию +,-,*,/")
if op == "+":
    result = n + m
elif op == "-":
    result = n - m
elif op == "*":
    result = n * m
elif op == "/":
    if m == 0:
        print("Ошибка: деление на ноль!")
        result = None
    else:
        result = n / m
else:
    print("Неизвестная операция:", op)
    result = None

# 3. Выводим результат (если он есть)
if result is not None:
    print(f"Результат: {n} {op} {m} = {result}")
    print(op)