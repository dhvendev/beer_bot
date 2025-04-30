import random


# Генерация рандома с заданным шансом
def generate_random_number(chance: int) -> float:
    if random.random() < chance / 100 or chance >= 100:
        return round(random.uniform(0.1, 5.0), 1)
    return round(random.uniform(-2.0, -0.1), 1)




