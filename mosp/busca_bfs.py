"""
Este arquivo contém a função de Busca em Largura (BFS) para percorrer o grafo padrão-padrão.

Descrição:
    - Dada uma lista de adjacência e um vértice inicial, a função gera uma ordem de visitação dos padrões (vértices) utilizando o algoritmo BFS.
    - A função inclui um mecanismo para garantir que todos os padrões sejam incluídos na ordem final, mesmo que o grafo tenha componentes desconexas (caso existam padrões que não compartilham peças com nenhum outro padrão). Isso é necessário porque o MOSP exige que todos os padrões sejam produzidos.

Uso no projeto:
    - A BFS gera uma ordem de produção inicial que será avaliada com a função de custo (NMPA).
    - Essa ordem é usada no benchmark para comparar diferentes estratégias de busca.

Função disponível:
    - bfs(lista_adjacencia, vertice_inicial)

Exemplo de uso:
    from mosp.busca_bfs import bfs
    ordem = bfs(lista_adjacencia, vertice_inicial)
"""
from collections import deque
from .busca_dfs import dfs_limitado
import numpy as np
import random

def bfs(lista_adjacencia, vertice_inicial):
    """
    Executa a Busca em Largura (BFS) no grafo padrão-padrão.

    Args:
        lista_adjacencia: Dicionário {vértice: lista de vizinhos}.
        vertice_inicial: Índice do vértice de início da busca.

    Returns:
        ordem: Lista de padrões (vértices) na ordem em que foram visitados pela BFS.
    """
    fila = []
    ordem = []

    fila.append(vertice_inicial)

    while len(fila) != 0:
        vertice_atual = fila.pop(0)

        for vizinho in lista_adjacencia[vertice_atual]:
            if (vizinho not in fila) and (vizinho not in ordem):
                fila.append(vizinho)

        ordem.append(vertice_atual)

    # Garante que todos os vértices sejam incluídos (caso o grafo tenha componentes desconexas - padrão que não compartilha peça com nenhum outro padrão)
    for vertice in lista_adjacencia:
        if vertice not in ordem:
            ordem.append(vertice)

    return ordem

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
