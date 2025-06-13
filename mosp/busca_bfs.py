"""
Este arquivo contém a função de Busca em Largura (BFS) para percorrer o grafo padrão-padrão.

Descrição:
    - Dada uma lista de adjacência e um vértice inicial, a função gera uma ordem de visitação dos padrões (vértices) utilizando o algoritmo BFS.
    - A função inclui um mecanismo para garantir que todos os padrões sejam incluídos na ordem final, mesmo que o grafo tenha componentes desconexas (caso existam padrões que não compartilham peças com nenhum outro padrão). Isso é necessário porque o MOSP exige que todos os padrões sejam produzidos.
    - Além disso, a função foi ajustada para ser totalmente compatível com subgrafos (por exemplo, nas comunidades detectadas por 'heuristica_comunidades_adaptativa'), em que os vértices podem não ser numerados de 0 a N-1.

Uso no projeto:
    - A BFS gera uma ordem de produção inicial que será avaliada com a função de custo (NMPA).
    - Essa ordem é usada no benchmark para comparar diferentes estratégias de busca.

Função disponível:
    - bfs(lista_adjacencia, vertice_inicial)

Exemplo de uso:
    from mosp.busca_bfs import bfs
    ordem = bfs(lista_adjacencia, vertice_inicial)
"""
import numpy as np
from collections import deque
import random

def bfs(lista_adjacencia, vertice_inicial):
    """
    Executa a Busca em Largura (BFS) no grafo padrão-padrão ou subgrafo.

    Compatível com subgrafos (ex: comunidades detectadas).

    Args:
        lista_adjacencia: Dicionário {vértice: lista de vizinhos}.
        vertice_inicial: Índice do vértice de início da busca.

    Returns:
        ordem: Lista de padrões (vértices) na ordem em que foram visitados pela BFS.
               Se o grafo tiver componentes desconexas, os padrões isolados ou de outras componentes
               serão adicionados ao final da ordem.
    """
    # Correção: pegar os vértices reais, não um range de 0 até N-1
    # Isso garante que a BFS funcione corretamente em subgrafos (ex: comunidades),
    # onde os vértices podem ser qualquer conjunto de índices.
    todos_vertices = list(lista_adjacencia.keys())

    visitados = set()
    ordem = []
    fila = [vertice_inicial]

    # Enquanto ainda houver vértices não visitados
    while todos_vertices:
        # Enquanto a fila não estiver vazia
        while fila:
            vertice_atual = fila.pop(0)

            if vertice_atual not in visitados:
                visitados.add(vertice_atual)
                ordem.append(vertice_atual)

                for vizinho in sorted(lista_adjacencia[vertice_atual]):
                    if vizinho not in visitados and vizinho not in fila:
                        fila.append(vizinho)

        # Após terminar um componente, atualiza a lista de vértices não visitados
        todos_vertices = list(set(todos_vertices) - visitados)

        # Se ainda houver vértices não visitados, começa nova BFS por outro componente
        if todos_vertices:
            fila = [todos_vertices[0]]

    return ordem

def bfs_adaptado(subgrafo, no_inicial, matPaPe):
    
    visitados = set()
    fila = deque([no_inicial])
    sequencia = []

    while fila:
        no_atual = fila.popleft()
        if no_atual not in visitados:
            visitados.add(no_atual)
            sequencia.append(no_atual)

            vizinhos = [v for v in subgrafo.neighbors(no_atual) if v not in visitados]
            if vizinhos:
                graus = np.array([subgrafo.degree(v) for v in vizinhos])
                similaridades = np.sum(matPaPe[no_atual] & matPaPe[vizinhos], axis=1)
                pesos = 0.6 * graus + 0.4 * similaridades
                ordenados = [v for _, v in sorted(zip(pesos, vizinhos), reverse=True)]
                fila.extend(ordenados)

    return sequencia