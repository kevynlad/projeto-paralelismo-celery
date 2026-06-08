from fastapi import FastAPI
from pydantic import BaseModel
from celery import group
import time

from tasks import celery_app, simular_monte_carlo_parcial

app = FastAPI(title="Monte Carlo Distribuído", version="1.0.0")


class RequisicaoPi(BaseModel):
    pontos: int
    num_workers: int = 4  # Padrão 4, mas o front pode enviar 1 para o benchmark


@app.get("/")
def health_check():
    return {"status": "online", "servico": "API Monte Carlo Distribuído"}


@app.post("/calcular")
def calcular_pi(dados: RequisicaoPi):
    tempo_inicio = time.time()

    total_pontos = dados.pontos
    num_workers = max(1, dados.num_workers)  # Garante mínimo de 1 worker

    # Divisão do trabalho: divide os pontos igualmente entre os workers
    pontos_por_worker = total_pontos // num_workers

    # Cria um grupo de tarefas Celery para rodar em paralelo
    tarefas_em_paralelo = group(
        simular_monte_carlo_parcial.s(pontos_por_worker) for _ in range(num_workers)
    )

    # Envia as tarefas para a fila do Redis e aguarda os resultados
    resultado_prometido = tarefas_em_paralelo.apply_async()
    resultados_workers = resultado_prometido.get(timeout=300)

    # Soma os pontos dentro do círculo de todos os workers
    total_dentro = sum(resultados_workers)

    # Fórmula de Monte Carlo: Pi ≈ 4 * (pontos dentro / total de pontos)
    pi_calculado = 4 * (total_dentro / total_pontos)

    tempo_fim = time.time()
    tempo_total = tempo_fim - tempo_inicio

    return {
        "pi": pi_calculado,
        "tempo_segundos": round(tempo_total, 4),
        "workers_utilizados": num_workers,
        "pontos_processados": total_pontos,
        "pontos_por_worker": pontos_por_worker,
    }