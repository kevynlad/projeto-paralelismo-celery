import streamlit as st
import requests
import time
import os

API_URL = os.getenv("API_URL", "http://localhost:8000") + "/calcular"

st.set_page_config(
    page_title="Monte Carlo Distribuído",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Simulador de Monte Carlo Distribuído")
st.write("Calcule o valor de **Pi (π)** utilizando processamento paralelo e distribuído na nuvem.")
st.markdown("---")

# ================================================
# CONFIGURAÇÕES DO EXPERIMENTO
# ================================================
st.subheader("⚙️ Configuração do Experimento")

col_cfg1, col_cfg2 = st.columns(2)

with col_cfg1:
    total_pontos = st.number_input(
        "Quantidade total de pontos (Iterações):",
        min_value=100_000,
        max_value=1_000_000_000,
        value=10_000_000,
        step=1_000_000,
        help="Quanto mais pontos, mais preciso e mais lento o cálculo."
    )

with col_cfg2:
    num_workers = st.selectbox(
        "Número de Workers:",
        options=[1, 2, 4, 8],
        index=2,
        help="Escolha 1 para sequencial ou 4+ para demonstrar o ganho de paralelismo."
    )

st.info(f"📋 Cada worker vai processar **{total_pontos // num_workers:,}** pontos em paralelo.")

# ================================================
# BENCHMARK AUTOMÁTICO: 1 vs 4 Workers
# ================================================
st.markdown("---")
st.subheader("📊 Benchmark de Performance")
run_benchmark = st.checkbox(
    "Executar benchmark automático (1 worker vs 4 workers)",
    value=False,
    help="Roda o mesmo cálculo com 1 e com 4 workers e compara os tempos."
)

# ================================================
# BOTÃO PRINCIPAL
# ================================================
st.markdown("---")

if st.button("🚀 Iniciar Processamento", type="primary"):

    if run_benchmark:
        # --- MODO BENCHMARK ---
        st.subheader("🏁 Resultado do Benchmark")
        resultados_benchmark = []

        for w in [1, 4]:
            with st.spinner(f"Rodando com {w} worker(s)..."):
                try:
                    payload = {"pontos": total_pontos, "num_workers": w}
                    resp = requests.post(API_URL, json=payload, timeout=300)
                    if resp.status_code == 200:
                        dados = resp.json()
                        resultados_benchmark.append({
                            "Workers": w,
                            "Pi Calculado": round(dados["pi"], 6),
                            "Tempo (s)": dados["tempo_segundos"],
                            "Erro vs Pi Real": round(abs(3.14159265 - dados["pi"]), 8),
                        })
                    else:
                        st.error(f"Erro com {w} worker(s): {resp.status_code}")
                except Exception as e:
                    st.error(f"Falha na conexão: {e}")

        if len(resultados_benchmark) == 2:
            speedup = resultados_benchmark[0]["Tempo (s)"] / resultados_benchmark[1]["Tempo (s)"]
            st.success(f"✅ Benchmark concluído! Speedup com 4 workers: **{speedup:.2f}x mais rápido**")
            st.table(resultados_benchmark)
            st.bar_chart(
                data={r["Workers"]: r["Tempo (s)"] for r in resultados_benchmark},
            )

    else:
        # --- MODO NORMAL ---
        with st.spinner(f"Enviando tarefas para {num_workers} worker(s) do Celery... Aguarde."):
            try:
                payload = {"pontos": total_pontos, "num_workers": num_workers}
                tempo_inicio_front = time.time()
                response = requests.post(API_URL, json=payload, timeout=300)
                tempo_fim_front = time.time()

                if response.status_code == 200:
                    dados = response.json()
                    pi_calculado = dados["pi"]
                    tempo_api = dados["tempo_segundos"]
                    workers_usados = dados["workers_utilizados"]

                    st.success("🎉 Processamento concluído com sucesso!")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("π Calculado", f"{pi_calculado:.6f}", f"Erro: {abs(3.14159265 - pi_calculado):.6f}")
                    col2.metric("Tempo de Execução", f"{tempo_api:.4f}s")
                    col3.metric("Workers Ativos", workers_usados)

                    st.subheader("📋 Resumo da Execução")
                    st.table({
                        "Métrica": [
                            "Pontos Processados",
                            "Pontos por Worker",
                            "Tempo Total (Front-end)",
                            "Diferença do Pi Real (3.14159265)",
                        ],
                        "Valor": [
                            f"{total_pontos:,}",
                            f"{dados.get('pontos_por_worker', 0):,}",
                            f"{tempo_fim_front - tempo_inicio_front:.4f}s",
                            f"{abs(3.14159265 - pi_calculado):.8f}",
                        ]
                    })

                else:
                    st.error(f"Erro na API: {response.status_code} — {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Não foi possível conectar à API. Verifique se o backend está rodando.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout! O cálculo demorou demais. Tente com menos pontos.")
            except Exception as e:
                st.error(f"Erro inesperado: {e}")

# ================================================
# RODAPÉ
# ================================================
st.markdown("---")
st.caption("Atividade Acadêmica — Cloud Computing | Arquitetura: Streamlit → FastAPI → Redis → Celery Workers")