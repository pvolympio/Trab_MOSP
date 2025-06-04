import numpy as np
import networkx as nx
from DFS import DFS
from BFS import BFS
from calculoPilhas import calcular_maximo_pilhas_usando_padrao_padrao, carregar_matriz_padrao_peca, construir_grafo_por_pecas_em_comum, heuristica_hibrida_por_densidade

def main():
    # Nome da instância (sem .txt)
    nome_instancia = "Cenário 3 - 1 - exemplo"

    # 1. Carregar a matriz padrão x peça
    matriz_padrao_peca = carregar_matriz_padrao_peca(nome_instancia)

    # 2. Construir o grafo padrão x padrão com base nas peças compartilhadas
    grafo = construir_grafo_por_pecas_em_comum(matriz_padrao_peca)

    # 3. Obter a ordem dos padrões usando a heurística híbrida adaptativa
    ordem_padroes = heuristica_hibrida_por_densidade(grafo, limiar=0.3)

    # 4. Calcular o número máximo de pilhas abertas
    max_pilhas = calcular_maximo_pilhas_usando_padrao_padrao(ordem_padroes, matriz_padrao_peca)

    # 5. Exibir os resultados
    print("-" * 50)
    print(f"Instância: {nome_instancia}")
    print(f"Sequência de padrões: {ordem_padroes}")
    print(f"NMPA (Número Máximo de Pilhas Abertas): {max_pilhas}")
    print("-" * 50)

if __name__ == "__main__":
    main()
