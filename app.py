import streamlit as st
import requests
import time

# URL da API do Dev 2 (quando estiver rodando no Docker, mudaremos isso)
API_URL = "http://localhost:8000/calcular"

# 1. Configuração do título da página
st.set_page_config(page_title="Processamento Distribuído", page_icon="🎯")
st.title("🎯 Simulador de Monte Carlo Distribuído")
st.write("Calcule o valor de Pi utilizando processamento paralelo e distribuído na nuvem.")

st.markdown("---")

# 2. Área de Input do Usuário
st.subheader("⚙️ Configuração do Experimento")
# O usuário escolhe quantos pontos quer gerar (quanto mais pontos, mais pesado o cálculo)
total_pontos = st.number_input(
    "Quantidade total de pontos (Iterações):", 
    min_value=100000, 
    max_value=1000000000, 
    value=10000000, 
    step=100000
)

# 3. Botão para disparar o cálculo
if st.button("🚀 Iniciar Processamento Pesado"):
    
    # Criamos um "spinner" de carregamento bonito
    with st.spinner("Enviando tarefas para os workers do Celery... Aguarde."):
        try:
            # Enviando o dado para a API do Dev 2
            payload = {"pontos": total_pontos}
            
            # Registra o tempo de início no front-end por segurança
            tempo_inicio = time.time() 
            
            response = requests.post(API_URL, json=payload, timeout=60)
            tempo_fim = time.time()

            if response.status_code == 200:
                dados_resposta = response.json()
                
                # Pegando as respostas vindas da API
                pi_calculado = dados_resposta.get("pi")
                tempo_execucao_api = dados_resposta.get("tempo_segundos")
                qtd_workers = dados_resposta.get("workers_utilizados", 4) # Exemplo

                # 4. Exibindo os Resultados de forma bonita
                st.success("🎉 Processamento concluído com sucesso!")
                
                # Criando colunas para os cards de métricas
                col1, col2, col3 = st.columns(3)
                col1.metric(label="Valor de Pi Calculado", value=f"{pi_calculado:.6f}")
                col2.metric(label="Tempo de Execução (API)", value=f"{tempo_execucao_api:.4f}s")
                col3.metric(label="Workers Ativos", value=qtd_workers)
                
                # Gráfico ou tabela simples para o relatório
                st.subheader("📊 Resumo da Execução")
                st.table({
                    "Métrica": ["Pontos Processados", "Tempo Total (Front-end)", "Diferença do Pi Real"],
                    "Valor": [f"{total_pontos:,}", f"{tempo_fim - tempo_inicio:.4f}s", f"{abs(3.141592 - pi_calculado):.6f}"]
                })

            else:
                st.error(f"Erro na API: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Não foi possível conectar à API. O Dev 2 já ligou o servidor backend?")