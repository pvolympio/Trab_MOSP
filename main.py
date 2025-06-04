import numpy as np
import networkx as nx
import DFS
from calculoPilhas import criaMatPadraoPeca, NMPA, construir_grafo,heuristica_hibrida_adaptativa
import BFS

def main():
    # Nome da instância (sem .txt)
    nome_instancia = "cenarios\Cenário 3 - 1 - exemplo"

    # 1. Ler a matriz padrões x peças
    matPaPe = criaMatPadraoPeca(nome_instancia)

    # 2. Construir o grafo
    G = construir_grafo(matPaPe)

    # 3. Aplicar a heurística híbrida adaptativa
    LP = heuristica_hibrida_adaptativa(G)

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