"""
Arquivo para testar uma única instância do problema MOSP.

Fluxo:
    - Lê uma instância específica
    - Constrói o grafo padrão-padrão
    - Aplica uma heurística ou busca selecionada
    - Calcula o NMPA
    - Exibe os resultados no console
    - Salva log da escolha de busca em CSV

Como rodar:
    python main.py
"""

import os
import pandas as pd
from mosp.leitura_instancia import criar_matriz_padroes_pecas
from mosp.grafo import construir_grafo
from mosp.custo_nmpa import calcular_nmpa
from mosp.heuristicas import (
    heuristica_hibrida_adaptativa,
    heuristica_comunidades_adaptativa,
    heuristica_hibrida_adaptativa_pico,
    heuristica_hibrida_por_componente
)
from mosp.busca_bfs import bfs
from mosp.busca_dfs import dfs

def main():
    # Nome da instância (sem .txt)
    nome_instancia = "cenario1"
    caminho_instancia = f"cenarios/{nome_instancia}.txt"

    # 1. Ler a matriz padrão × peça
    matriz = criar_matriz_padroes_pecas(caminho_instancia)

    # 2. Construir o grafo padrão-padrão
    grafo = construir_grafo(matriz)
    lista_adjacencia = {v: list(grafo.neighbors(v)) for v in grafo.nodes()}

    # 3. SELECIONE A HEURÍSTICA OU BUSCA AQUI
    heuristica = "pico"  # "hibrida", "comunidades", "pico", "bfs", "dfs", "componentes"

    if heuristica == "hibrida":
        ordem, log_execucao = heuristica_hibrida_adaptativa(grafo, limiar_densidade=0.3)
        nome_arquivo_log = f"log_hibrida_{nome_instancia}.csv"

    elif heuristica == "componentes":
        ordem, log_execucao = heuristica_hibrida_por_componente(grafo,matriz)
        nome_arquivo_log =  f"log_componentes_{nome_instancia}.csv"

    elif heuristica == "comunidades":
        ordem, log_execucao = heuristica_comunidades_adaptativa(grafo, limiar_densidade=0.3)
        nome_arquivo_log = f"log_comunidades_{nome_instancia}.csv"

    elif heuristica == "pico":
        ordem, log_execucao = heuristica_hibrida_adaptativa_pico(grafo, matriz)
        nome_arquivo_log = f"log_hibrida_pico_{nome_instancia}.csv"

    elif heuristica == "bfs":
        ordem = bfs(lista_adjacencia, vertice_inicial=0)
        # Criar log simples
        log_execucao = [{"Padrao": v, "Busca": "BFS"} for v in ordem]
        nome_arquivo_log = f"log_bfs_{nome_instancia}.csv"

    elif heuristica == "dfs":
        ordem = dfs(lista_adjacencia, vertice_inicial=0)
        # Criar log simples
        log_execucao = [{"Padrao": v, "Busca": "DFS"} for v in ordem]
        nome_arquivo_log = f"log_dfs_{nome_instancia}.csv"

    else:
        raise ValueError("Heurística inválida! Escolha entre: 'hibrida', 'comunidades', 'pico', 'bfs' ou 'dfs'.")

    # 4. Calcular NMPA
    nmpa = calcular_nmpa(ordem, matriz)

    # 5. Exibir resultados
    print("-" * 40)
    print(f"Instância: {nome_instancia}")
    print(f"Heurística / Busca utilizada: {heuristica}")
    print(f"Ordem gerada: {ordem}")
    print(f"NMPA (Número Máximo de Pilhas Abertas): {nmpa}")
    print("-" * 40)

    # 6. Salvar log da execução na pasta resultados/resultados_main/
    pasta_saida = "resultados/resultados_main"
    os.makedirs(pasta_saida, exist_ok=True)

    df_log = pd.DataFrame(log_execucao)
    df_log.to_csv(os.path.join(pasta_saida, nome_arquivo_log), index=False)

    print(f"Log salvo em: {pasta_saida}/{nome_arquivo_log}")

if __name__ == "__main__":
    main()