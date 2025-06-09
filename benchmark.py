# -*- coding: utf-8 -*-

"""
Este arquivo executa o benchmark completo para o problema MOSP.

Fluxo:
    - Lê cada instância da pasta "cenarios/"
    - Constrói o grafo padrão-padrão
    - Aplica cada estratégia:
        - BFS
        - DFS
        - Heurística híbrida
        - Aleatória
    - Calcula o NMPA de cada ordem
    - Salva os resultados em um arquivo CSV na pasta "resultados/"

Como rodar:
    python benchmark.py
"""

import os
import csv

from mosp.leitura_instancia import criar_matriz_padroes_pecas
from mosp.grafo import construir_grafo
from mosp.custo_nmpa import calcular_nmpa
from mosp.busca_bfs import bfs
from mosp.busca_dfs import dfs
from mosp.heuristicas import heuristica_hibrida_adaptativa, aleatoria

def executar_benchmark(pasta_instancias, caminho_saida_csv):
    """
    Executa o benchmark para todas as instâncias da pasta especificada.

    Args:
        pasta_instancias: Caminho da pasta onde estão os arquivos .txt das instâncias.
        caminho_saida_csv: Caminho do arquivo CSV de saída (para salvar os resultados).
    """
    resultados = []

    for arquivo in os.listdir(pasta_instancias):
        if arquivo.endswith(".txt"):
            nome_instancia = arquivo.replace(".txt", "")
            caminho_instancia = os.path.join(pasta_instancias, arquivo)

            print(f">>> Processando: {nome_instancia}")

            # 1. Ler a matriz padrão × peça
            matriz = criar_matriz_padroes_pecas(caminho_instancia)

            # 2. Construir o grafo padrão-padrão
            grafo = construir_grafo(matriz)

            # 3. Gerar lista de adjacência
            lista_adjacencia = {v: list(grafo.neighbors(v)) for v in grafo.nodes()}

            # 4. Aplicar estratégias
            ordem_bfs = bfs(lista_adjacencia, vertice_inicial=0)
            ordem_dfs = dfs(lista_adjacencia, vertice_inicial=0)
            ordem_hibrida = heuristica_hibrida_adaptativa(grafo,matriz)
            ordem_aleatoria = aleatoria(grafo)

            # 5. Calcular NMPA de cada ordem
            nmpa_bfs = calcular_nmpa(ordem_bfs, matriz)
            nmpa_dfs = calcular_nmpa(ordem_dfs, matriz)
            nmpa_hibrida = calcular_nmpa(ordem_hibrida, matriz)
            nmpa_aleatoria = calcular_nmpa(ordem_aleatoria, matriz)

            # 6. Armazenar resultados
            resultados.append({
                "Instancia": nome_instancia,
                "NMPA_BFS": nmpa_bfs,
                "NMPA_DFS": nmpa_dfs,
                "NMPA_Hibrida": nmpa_hibrida,
                "NMPA_Aleatoria": nmpa_aleatoria
            })

    # 7. Escrever resultados no CSV
    os.makedirs(os.path.dirname(caminho_saida_csv), exist_ok=True)
    with open(caminho_saida_csv, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Instancia", "NMPA_BFS", "NMPA_DFS", "NMPA_Hibrida", "NMPA_Aleatoria"])
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\nBenchmark finalizado. Resultados salvos em: {caminho_saida_csv}")

if __name__ == "__main__":
    executar_benchmark(
        pasta_instancias="cenarios",
        caminho_saida_csv="resultados/benchmark_mosp.csv"
    )