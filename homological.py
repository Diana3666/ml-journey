def homological_temperature(t_celsius, t_melt_kelvin=933):
    """
    Гомологическая температура = T_рабочая / T_плавления (в Кельвинах).
    Для алюминия T_плавления = 933 K.
    """
    t_kelvin = t_celsius + 273.15
    return t_kelvin / t_melt_kelvin


# Проверка для разных режимов деформации алюминия
print(f"Комнатная (25°C):      T/Tпл = {homological_temperature(25):.3f}")
print(f"Тёплая (200°C):        T/Tпл = {homological_temperature(200):.3f}")
print(f"Горячая (400°C):       T/Tпл = {homological_temperature(400):.3f}")
print(f"Очень горячая (500°C): T/Tпл = {homological_temperature(500):.3f}")