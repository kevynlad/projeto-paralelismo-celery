import random
import os
from celery import Celery

# O Dev 3 vai usar o Docker, então configuramos para ler do ambiente.
# Se não estiver no Docker, ele usa o 'localhost' (para testes locais).
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Inicializa o Celery configurando o Redis como o intermediário (Broker e Backend)
celery_app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task
def simular_monte_carlo_parcial(pontos_parciais):
    """
    Esta função roda dentro de UM worker.
    Ela calcula apenas uma fração do total de pontos.
    """
    dentro_do_circulo = 0
    for _ in range(pontos_parciais):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        # Equação do círculo: x² + y² <= r² (no caso, raio = 1)
        if x**2 + y**2 <= 1:
            dentro_do_circulo += 1
            
    return dentro_do_circulo