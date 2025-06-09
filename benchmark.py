# -*- coding: utf-8 -*-

"""
Este arquivo executa o benchmark completo para o problema MOSP.

Fluxo:
    - Lê cada instância da pasta "cenarios/"
    - Constrói o grafo padrão-padrão
    - Aplica cada estratégia:
        - BFS
        - DFS
        - Heurística híbrida (limiar 0.3)
        - Heurística comunidades (limiar 0.3)
        - Heurística baseada em pico de NMPA
        - Aleatória
    - Calcula o NMPA de cada ordem
    - Salva:
        - CSV com os NMPAs gerais (para todas as instâncias)
        - CSV de log da escolha de busca para cada heurística adaptativa (por instância)

Como rodar:
    python benchmark.py
"""

import os
import csv
import pandas as pd

from mosp.leitura_instancia import criar_matriz_padroes_pecas
from mosp.grafo import construir_grafo
from mosp.custo_nmpa import calcular_nmpa
from mosp.busca_bfs import bfs
from mosp.busca_dfs import dfs
from mosp.heuristicas import (
    heuristica_hibrida_adaptativa,
    heuristica_comunidades_adaptativa,
    heuristica_hibrida_adaptativa_pico,
    heuristica_hibrida_por_componente,
    aleatoria
)

def executar_benchmark(pasta_instancias, caminho_saida_csv, pasta_logs):
    """
    Executa o benchmark para todas as instâncias da pasta especificada.

    Args:
        pasta_instancias: Caminho da pasta onde estão os arquivos .txt das instâncias.
        caminho_saida_csv: Caminho do arquivo CSV de saída (para salvar os resultados gerais).
        pasta_logs: Pasta para salvar os logs de execução das heurísticas adaptativas.
    """
    resultados = []

    os.makedirs(pasta_logs, exist_ok=True)

    for arquivo in os.listdir(pasta_instancias):
        if arquivo.endswith(".txt"):
            nome_instancia = arquivo.replace(".txt", "")
            caminho_instancia = os.path.join(pasta_instancias, arquivo)

            print(f"Processando: {nome_instancia}")

            # 1. Ler a matriz padrão × peça
            matriz = criar_matriz_padroes_pecas(caminho_instancia)

            # 2. Construir o grafo padrão-padrão
            grafo = construir_grafo(matriz)

            # 3. Gerar lista de adjacência
            lista_adjacencia = {v: list(grafo.neighbors(v)) for v in grafo.nodes()}

            # 4. Aplicar estratégias
            ordem_bfs = bfs(lista_adjacencia, vertice_inicial=0)
            ordem_dfs = dfs(lista_adjacencia, vertice_inicial=0)

            ordem_hibrida, log_hibrida = heuristica_hibrida_adaptativa(grafo, limiar_densidade=0.3)
            ordem_comunidades, log_comunidades = heuristica_comunidades_adaptativa(grafo, limiar_densidade=0.3)
            ordem_pico, log_pico = heuristica_hibrida_adaptativa_pico(grafo, matriz)
            ordem_por_componente = heuristica_hibrida_por_componente(grafo,matriz)

            ordem_aleatoria = aleatoria(grafo)

            # 5. Calcular NMPA de cada ordem
            nmpa_bfs = calcular_nmpa(ordem_bfs, matriz)
            nmpa_dfs = calcular_nmpa(ordem_dfs, matriz)
            nmpa_hibrida = calcular_nmpa(ordem_hibrida, matriz)
            nmpa_comunidades = calcular_nmpa(ordem_comunidades, matriz)
            nmpa_pico = calcular_nmpa(ordem_pico, matriz)
            nmpa_por_componente =calcular_nmpa(ordem_por_componente,matriz)
            nmpa_aleatoria = calcular_nmpa(ordem_aleatoria, matriz)

            # 6. Armazenar resultados gerais
            resultados.append({
                "Instancia": nome_instancia,
                "NMPA_BFS": nmpa_bfs,
                "NMPA_DFS": nmpa_dfs,
                "NMPA_Hibrida": nmpa_hibrida,
                "NMPA_Comunidades": nmpa_comunidades,
                "NMPA_Pico": nmpa_pico,
                "NMPA_Componentes": nmpa_por_componente,
                "NMPA_Aleatoria": nmpa_aleatoria
            })

            # 7. Salvar logs de execução das heurísticas adaptativas
            df_log_hibrida = pd.DataFrame(log_hibrida)
            df_log_hibrida.to_csv(os.path.join(pasta_logs, f"log_hibrida_{nome_instancia}.csv"), index=False)

            df_log_comunidades = pd.DataFrame(log_comunidades)
            df_log_comunidades.to_csv(os.path.join(pasta_logs, f"log_comunidades_{nome_instancia}.csv"), index=False)

            df_log_pico = pd.DataFrame(log_pico)
            df_log_pico.to_csv(os.path.join(pasta_logs, f"log_hibrida_pico_{nome_instancia}.csv"), index=False)

    # 8. Escrever resultados gerais no CSV
    os.makedirs(os.path.dirname(caminho_saida_csv), exist_ok=True)
    with open(caminho_saida_csv, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Instancia", "NMPA_BFS", "NMPA_DFS", "NMPA_Hibrida", "NMPA_Comunidades", "NMPA_Pico","NMPA_Componentes", "NMPA_Aleatoria"
        ])
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\nResultados salvos em: {caminho_saida_csv}")
    print(f"Logs detalhados salvos em: {pasta_logs}")

if __name__ == "__main__":
    executar_benchmark(
        pasta_instancias="cenarios",
        caminho_saida_csv="resultados/benchmark_mosp.csv",
        pasta_logs="resultados/logs"
    )