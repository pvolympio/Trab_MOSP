"""
Este arquivo gera um gráfico de barras a partir do CSV de resultados do benchmark.

Fluxo:
    - Lê o arquivo "resultados/benchmark_mosp.csv"
    - Gera um gráfico de comparação de NMPA por heurística
    - Salva o gráfico em "resultados/grafico_barras.png"

Como rodar:
    python gerar_grafico.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

def gerar_grafico_barras(csv_path, salvar_em="resultados/grafico_barras.png"):
    """
    Gera e salva um gráfico de barras a partir do CSV de resultados.

    Args:
        csv_path: Caminho para o arquivo CSV de benchmark.
        salvar_em: Caminho onde o gráfico será salvo.
    """
    df = pd.read_csv(csv_path, encoding='latin1')
    df.set_index("Instancia", inplace=True)

    ax = df.plot(kind="bar", figsize=(12, 6), colormap="Set2")
    plt.title("Comparação de NMPA por Heurística")
    plt.ylabel("Número Máximo de Pilhas Abertas (NMPA)")
    plt.xlabel("Instância")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()

    os.makedirs(os.path.dirname(salvar_em), exist_ok=True)
    plt.savefig(salvar_em)
    print(f"Gráfico de barras salvo em: {salvar_em}")
    plt.show()

if __name__ == "__main__":
    gerar_grafico_barras("resultados/benchmark_mosp.csv")
