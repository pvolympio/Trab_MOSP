from DFS import dfs_limitado
from collections import deque
import numpy as np
import random

def BFS(G, v_inicial):
    from collections import deque

    visitados = set([v_inicial])
    fila = deque([v_inicial])
    resultado = []

    while fila:
        atual = fila.popleft()
        resultado.append(atual)

        for vizinho in sorted(G.neighbors(atual)):
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append(vizinho)

    return resultado

def bfs_adaptativo(subgrafo, no_inicial, matPaPe, profundidade_max=3):
    """
    Realiza uma busca em largura adaptativa (BFS) com possibilidade de transição para DFS
    em profundidades mais altas, dependendo da estrutura local do grafo e da aleatoriedade.

    Args:
        subgrafo: componente do grafo principal (NetworkX Graph).
        no_inicial: vértice de partida da busca.
        matPaPe: matriz padrão x peça.
        profundidade_max: profundidade limite para considerar transição para DFS.

    Returns:
        Lista com a sequência de visita aos padrões (vértices).
    """
    visitados = set()  # Conjunto de nós já explorados
    fila = deque([(no_inicial, 0)])  # Fila de BFS, com tuplas (nó, profundidade)
    sequencia = []  # Armazena a sequência final dos nós visitados

    while fila:
        no_atual, profundidade = fila.popleft()  # Retira o primeiro da fila

        if no_atual not in visitados:
            visitados.add(no_atual)  # Marca como visitado
            sequencia.append(no_atual)  # Adiciona à sequência

            # Ordena os vizinhos por similaridade de peças (mais similares primeiro)
            vizinhos = sorted(subgrafo.neighbors(no_atual),
                              key=lambda x: np.sum(matPaPe[no_atual] & matPaPe[x]),
                              reverse=True)

            for vizinho in vizinhos:
                if vizinho not in visitados:
                    # Se profundidade for alta, há chance de transitar para DFS
                    if profundidade >= profundidade_max and random.random() < 0.7:
                        # Executa DFS a partir do vizinho como fallback local
                        sequencia.extend(dfs_limitado(subgrafo, vizinho, visitados, matPaPe, limite=2))
                    else:
                        fila.append((vizinho, profundidade + 1))  # Continua BFS normalmente

    return sequencia
