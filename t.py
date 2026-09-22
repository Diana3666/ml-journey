def calculate(a, b, op="+"):
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "*":
        return a * b
    elif op == "/":
        if b == 0:
            return None
        return a / b
    else:
        return None

# Проверки (без отступа!)
print(calculate(5, 3))         # 8
print(calculate(5, 3, "-"))    # 2
print(calculate(5, 3, "*"))    # 15
print(calculate(10, 2, "/"))   # 5.0
print(calculate(5, 0, "/"))    # None
print(calculate(5, 3, "%"))    # None