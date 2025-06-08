"""
Este arquivo contém as heurísticas utilizadas para gerar ordens de produção no problema MOSP.

Descrição:
    - Diferente das buscas clássicas (BFS, DFS), estas heurísticas aplicam estratégias adaptativas ou aleatórias para gerar uma ordem de produção.
    - A heurística híbrida decide dinamicamente entre usar BFS ou DFS em cada componente do grafo, com base na densidade do componente.
    - A heurística aleatória simplesmente gera uma ordem aleatória dos padrões (baseline para comparação).

Uso no projeto:
    - As heurísticas geram ordens de produção que serão avaliadas com a função de custo (NMPA).
    - Essas ordens são usadas no benchmark para comparar diferentes estratégias.

Funções disponíveis:
    - heuristica_hibrida_adaptativa(grafo, limiar_densidade=0.3)
    - aleatoria(grafo)

Exemplo de uso:
    from mosp.heuristicas import heuristica_hibrida_adaptativa, aleatoria

    ordem_hibrida = heuristica_hibrida_adaptativa(grafo)
    ordem_aleatoria = aleatoria(grafo)
"""

import networkx as nx
import random
from mosp.busca_bfs import bfs
from mosp.busca_dfs import dfs

def heuristica_hibrida_adaptativa(grafo, limiar_densidade=0.3):
    """
    Gera uma ordem de produção utilizando a heurística híbrida adaptativa.

    - A heurística aplica BFS em componentes mais densos e DFS em componentes mais esparsos.
    - O objetivo é explorar diferentes características estruturais do grafo padrão-padrão.

    A função garante que todos os padrões (vértices) sejam incluídos na ordem final,
    mesmo que o grafo tenha componentes desconexas.

    Args:
        grafo: Objeto nx.Graph (grafo padrão-padrão).
        limiar_densidade: Limite para decidir entre BFS e DFS em cada componente.

    Returns:
        ordem_final: Lista de padrões (vértices) na ordem gerada pela heurística híbrida.
    """
    visitados = set()
    ordem_final = []

    # Começa pelo vértice de maior grau
    vertice_inicial = max(grafo.degree, key=lambda x: x[1])[0]

    # Primeiro componente
    componente_inicial = nx.node_connected_component(grafo, vertice_inicial)
    subgrafo_inicial = grafo.subgraph(componente_inicial)

    lista_adjacencia = {v: list(subgrafo_inicial.neighbors(v)) for v in subgrafo_inicial.nodes()}
    ordem = bfs(lista_adjacencia, vertice_inicial)
    ordem_final.extend(ordem)
    visitados.update(ordem)

    # Demais componentes
    for componente in nx.connected_components(grafo):
        componentes_nao_visitados = [v for v in componente if v not in visitados]
        if not componentes_nao_visitados:
            continue

        subgrafo = grafo.subgraph(componentes_nao_visitados)
        densidade = nx.density(subgrafo)
        vertice_inicio = componentes_nao_visitados[0]

        lista_adjacencia = {v: list(subgrafo.neighbors(v)) for v in subgrafo.nodes()}

        if densidade >= limiar_densidade:
            ordem = bfs(lista_adjacencia, vertice_inicio)
        else:
            ordem = dfs(lista_adjacencia, vertice_inicio)

        ordem_final.extend(ordem)
        visitados.update(ordem)

    return ordem_final

def aleatoria(grafo):
    """
    Gera uma ordem de produção aleatória.

    Esta heurística serve como baseline no benchmark.

    Args:
        grafo: Objeto nx.Graph (grafo padrão-padrão).

    Returns:
        ordem: Lista de padrões (vértices) em ordem aleatória.
    """
    vertices = list(grafo.nodes())
    random.shuffle(vertices)
    return vertices
