import numpy as np
import networkx as nx
import DFS
from calculoPilhas import criaMatPadraoPeca, NMPA, construir_grafo,heuristica_hibrida_completa
import BFS

def main():
    # Nome da instância (sem .txt)
    nome_instancia = "cenarios\Cenário 3 - 10 - Random-400-400-4-1"

    # 1. Ler a matriz padrões x peças
    matPaPe = criaMatPadraoPeca(nome_instancia)

    G = construir_grafo(matPaPe)
    LP = heuristica_hibrida_completa(G, matPaPe)


    # 4. Calcular o NMPA
    resultado = NMPA(LP, matPaPe)

    # 5. Exibir os resultados
    print("-" * 50)
    print(f"Instância: {nome_instancia}")
    print(f"Sequência de padrões (LP): {LP}")
    print(f"NMPA (Número Máximo de Pilhas Abertas): {resultado}")
    print("-" * 50)

    
if __name__ == "__main__":
    main()