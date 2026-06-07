from fastapi import FastAPI
from pydantic import BaseModel
from celery import group
import time

# Importa o app do Celery e a task que criamos no Passo 2
from tasks import celery_app, simular_monte_carlo_parcial

app = FastAPI()

# Define o formato do dado que a API espera receber (JSON)
class RequisicaoPi(BaseModel):
    pontos: int

@app.post("/calcular")
def calcular_pi(dados: RequisicaoPi):
    tempo_inicio = time.time()
    
    total_pontos = dados.pontos
    num_workers = 4  # Requisito do trabalho: comparar com 4 ou mais workers
    
    # Divisão do trabalho: divide o total de pontos igualmente entre os 4 workers
    pontos_por_worker = total_pontos // num_workers
    
    # Criamos um "grupo" de tarefas no Celery para rodarem em paralelo
    tarefas_em_paralelo = group(
        simular_monte_carlo_parcial.s(pontos_por_worker) for _ in range(num_workers)
    )
    
    # Envia o grupo de tarefas para a fila do Redis
    resultado_prometido = tarefas_em_paralelo.apply_async()
    
    # Bloqueia a API temporariamente esperando os workers terminarem.
    # O método .get() junta as respostas de todos os workers em uma lista.
    resultados_workers = resultado_prometido.get() 
    
    # Soma quantos pontos caíram dentro do círculo no total de todos os workers
    total_dentro = sum(resultados_workers)
    
    # Fórmula final do algoritmo de Monte Carlo para Pi
    pi_calculado = 4 * (total_dentro / total_pontos)
    
    tempo_fim = time.time()
    tempo_total = tempo_fim - tempo_inicio
    
    # Retorna exatamente o JSON que o seu Front-end (Streamlit) está esperando!
    return {
        "pi": pi_calculado,
        "tempo_segundos": tempo_total,
        "workers_utilizados": num_workers
    }