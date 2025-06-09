# -*- coding: utf-8 -*-

"""
Este arquivo gera gráficos de análise do teste de limiar de densidade.

Motivação:
    - O arquivo "teste_limiar_densidade.csv" contém os resultados da sensibilidade do parâmetro 'limiar_densidade' nas heurísticas adaptativas.
    - Este script gera gráficos NMPA vs Limiar para cada heurística para auxiliar na escolha do limiar ótimo para uso no benchmark final.

Fluxo:
    - Lê o arquivo "resultados/teste_limiar_densidade.csv"
    - Gera um gráfico NMPA vs Limiar para cada instância (se desejar)
    - Gera um gráfico NMPA médio por limiar (média sobre as instâncias) para cada heurística
    - Salva os gráficos na pasta "resultados/"

Como rodar:
    python plot_teste_limiar.py

Notas:
    - Este script é complementar ao "teste_limiar_densidade.py".
    - Os gráficos ajudam a justificar a escolha do limiar no relatório.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_nmpa_vs_limiar(csv_path, salvar_em="resultados/plot_nmpa_vs_limiar.png"):
    """
    Gera um gráfico NMPA médio vs Limiar para as heurísticas adaptativas.

    Args:
        csv_path: Caminho para o CSV gerado pelo teste de limiar.
        salvar_em: Caminho onde o gráfico será salvo.
    """
    df = pd.read_csv(csv_path)

    # Agrupar por limiar e calcular média de NMPA por heurística
    df_grouped = df.groupby("Limiar_Densidade").mean(numeric_only=True).reset_index()

    # Plotar
    plt.figure(figsize=(10, 6))
    plt.plot(df_grouped["Limiar_Densidade"], df_grouped["NMPA_Hibrida"], marker='o', label="Híbrida")
    plt.plot(df_grouped["Limiar_Densidade"], df_grouped["NMPA_Comunidades"], marker='s', label="Comunidades")

    plt.title("NMPA médio vs Limiar de Densidade")
    plt.xlabel("Limiar de Densidade")
    plt.ylabel("Número Máximo de Pilhas Abertas (NMPA)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()

    os.makedirs(os.path.dirname(salvar_em), exist_ok=True)
    plt.savefig(salvar_em)
    print(f"Gráfico NMPA vs Limiar salvo em: {salvar_em}")
    plt.show()

if __name__ == "__main__":
    plot_nmpa_vs_limiar("resultados/teste_limiar_densidade.csv")