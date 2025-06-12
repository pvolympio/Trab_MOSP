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
import time
import os
import csv
import pandas as pd
import re

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
def extrair_numero(nome):
    numeros = re.findall(r'\d+', nome)
    return int(numeros[1]) if len(numeros) > 1 else int(numeros[0])

def executar_benchmark(pasta_instancias, caminho_saida_csv, pasta_logs, caminho_tempo_csv):
    """
    Executa o benchmark para todas as instâncias da pasta especificada.

    Args:
        pasta_instancias: Caminho da pasta onde estão os arquivos .txt das instâncias.
        caminho_saida_csv: Caminho do arquivo CSV de saída (resultados NMPA).
        pasta_logs: Pasta para salvar os logs de execução das heurísticas adaptativas.
        caminho_tempo_csv: Caminho do arquivo CSV para salvar os tempos de execução.
    """
   
    resultados = []
    tempos = []

    os.makedirs(pasta_logs, exist_ok=True)

    for arquivo in sorted(os.listdir(pasta_instancias),key=extrair_numero):
        if arquivo.endswith(".txt"):
            nome_instancia = arquivo.replace(".txt", "")
            caminho_instancia = os.path.join(pasta_instancias, arquivo)

            print(f"Processando: {nome_instancia}")

            matriz = criar_matriz_padroes_pecas(caminho_instancia)
            grafo = construir_grafo(matriz)
            lista_adjacencia = {v: list(grafo.neighbors(v)) for v in grafo.nodes()}

            inicio = time.perf_counter()
            ordem_bfs = bfs(lista_adjacencia, vertice_inicial=0)
            tempo_bfs = round(time.perf_counter() - inicio, 4)

            inicio = time.perf_counter()
            ordem_dfs = dfs(lista_adjacencia, vertice_inicial=0)
            tempo_dfs = round(time.perf_counter() - inicio, 4)

            inicio = time.perf_counter()
            ordem_hibrida, log_hibrida = heuristica_hibrida_adaptativa(grafo, limiar_densidade=0.3)
            tempo_hibrida = round(time.perf_counter() - inicio, 4)

            inicio = time.perf_counter()
            ordem_comunidades, log_comunidades = heuristica_comunidades_adaptativa(grafo, limiar_densidade=0.3)
            tempo_comunidades = round(time.perf_counter() - inicio, 4)

            inicio = time.perf_counter()
            ordem_pico, log_pico = heuristica_hibrida_adaptativa_pico(grafo, matriz)
            tempo_pico = round(time.perf_counter() - inicio, 4)

            inicio = time.perf_counter()
            ordem_por_componente,log_componentes = heuristica_hibrida_por_componente(grafo, matriz)
            tempo_componentes = round(time.perf_counter() - inicio, 4)

            inicio = time.perf_counter()
            ordem_aleatoria = aleatoria(grafo)
            tempo_aleatoria = round(time.perf_counter() - inicio, 4)

            nmpa_bfs = calcular_nmpa(ordem_bfs, matriz)
            nmpa_dfs = calcular_nmpa(ordem_dfs, matriz)
            nmpa_hibrida = calcular_nmpa(ordem_hibrida, matriz)
            nmpa_comunidades = calcular_nmpa(ordem_comunidades, matriz)
            nmpa_pico = calcular_nmpa(ordem_pico, matriz)
            nmpa_por_componente = calcular_nmpa(ordem_por_componente, matriz)
            nmpa_aleatoria = calcular_nmpa(ordem_aleatoria, matriz)

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

            tempos.append({
                "Instancia": nome_instancia,
                "Tempo_BFS (s)": tempo_bfs,
                "Tempo_DFS (s)": tempo_dfs,
                "Tempo_Hibrida (s)": tempo_hibrida,
                "Tempo_Comunidades (s)": tempo_comunidades,
                "Tempo_Pico (s)": tempo_pico,
                "Tempo_Componentes (s)": tempo_componentes,
                "Tempo_Aleatoria (s)": tempo_aleatoria
            })

            df_log_hibrida = pd.DataFrame(log_hibrida)
            df_log_hibrida.to_csv(os.path.join(pasta_logs, f"log_hibrida_{nome_instancia}.csv"), index=False)

            df_log_comunidades = pd.DataFrame(log_comunidades)
            df_log_comunidades.to_csv(os.path.join(pasta_logs, f"log_comunidades_{nome_instancia}.csv"), index=False)

            df_log_pico = pd.DataFrame(log_pico)
            df_log_pico.to_csv(os.path.join(pasta_logs, f"log_hibrida_pico_{nome_instancia}.csv"), index=False)

            df_log_componentes = pd.DataFrame(log_componentes)
            df_log_componentes.to_csv(os.path.join(pasta_logs, f"log_hibrida_componentes_{nome_instancia}.csv"), index=False)

    os.makedirs(os.path.dirname(caminho_saida_csv), exist_ok=True)
    with open(caminho_saida_csv, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Instancia", "NMPA_BFS", "NMPA_DFS", "NMPA_Hibrida", "NMPA_Comunidades", "NMPA_Pico", "NMPA_Componentes", "NMPA_Aleatoria"
        ])
        writer.writeheader()
        writer.writerows(resultados)

    os.makedirs(os.path.dirname(caminho_tempo_csv), exist_ok=True)
    with open(caminho_tempo_csv, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Instancia", "Tempo_BFS (s)", "Tempo_DFS (s)", "Tempo_Hibrida (s)", "Tempo_Comunidades (s)", "Tempo_Pico (s)", "Tempo_Componentes (s)", "Tempo_Aleatoria (s)"
        ])
        writer.writeheader()
        writer.writerows(tempos)

    print(f"\nResultados salvos em: {caminho_saida_csv}")
    print(f"Tempos salvos em: {caminho_tempo_csv}")
    print(f"Logs detalhados salvos em: {pasta_logs}")


if __name__ == "__main__":
    executar_benchmark(
        pasta_instancias="cenarios",
        caminho_saida_csv="resultados/benchmark_mosp.csv",
        pasta_logs="resultados/logs",
        caminho_tempo_csv="resultados/tempos_mosp.csv"
    )
