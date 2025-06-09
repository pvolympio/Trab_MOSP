"""
Este arquivo gera um gráfico de barras a partir do CSV de resultados do benchmark.

Fluxo:
    - Lê o arquivo "resultados/benchmark_mosp.csv"
    - Gera um gráfico de comparação de NMPA por heurística
    - Salva o gráfico em "resultados/grafico_barras.png"

Como rodar:
    python gerar_grafico.py
"""

import os
import unicodedata
import pandas as pd
import matplotlib.pyplot as plt

def gerar_grafico_barras(csv_path, salvar_em="resultados/grafico_barras.png"):
    """
    Gera e salva um gráfico de barras a partir do CSV de resultados.

    Args:
        csv_path: Caminho para o arquivo CSV de benchmark.
        salvar_em: Caminho onde o gráfico será salvo.
    """
    df = pd.read_csv(csv_path, encoding='latin1')
    df.set_index("Instancia", inplace=True)

    # Normalizar nomes do índice para remover acentos
    df.index = df.index.map(lambda x: unicodedata.normalize('NFKD', x).encode('ASCII', 'ignore').decode('ASCII'))

    # Agora substituir 'Cenario 3' por 'Cen. 3'
    df.index = df.index.str.replace(r"^Cen.*? 3", "Cen. 3", regex=True)

    # Definir ordem das colunas e cores desejadas
    colunas = [
        "NMPA_BFS",
        "NMPA_DFS",
        "NMPA_Hibrida",
        "NMPA_Comunidades",
        "NMPA_Pico",
        "NMPA_Componentes",
        "NMPA_Aleatoria"
    ]

    cores = [
        "#ADD8E6", # Azul claro para BFS
        "#00008B", # Azul escuro para DFS
        "#FFC0CB", # Rosa para heurística híbrida
        "#FF69B4", # Rosa mais forte para heurística de comunidades
        "#32CD32", # Verde para heurística de pico
        "#FFFF00", # Amarelo para heurística por componentes
        "#A9A9A9"  # Cinza para heurística aleatória
    ]

    ax = df[colunas].plot(kind="bar", figsize=(16, 8), color=cores)

    plt.title("Comparação de NMPA por Heurística")
    plt.ylabel("Número Máximo de Pilhas Abertas (NMPA)")
    plt.xlabel("Instância")
    plt.xticks(rotation=60, ha='right')  # Melhor rotação + alinhamento à direita
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    plt.tight_layout()

    os.makedirs(os.path.dirname(salvar_em), exist_ok=True)
    plt.savefig(salvar_em)
    print(f"Gráfico de barras salvo em: {salvar_em}")
    plt.show()

if __name__ == "__main__":
    gerar_grafico_barras("resultados/benchmark_mosp.csv")