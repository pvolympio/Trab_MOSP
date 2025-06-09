"""
Este arquivo contém a função para construção do grafo padrão-padrão a partir da matriz padrão x peça.

Descrição:
    - Cada padrão de produção é representado como um vértice do grafo.
    - Dois padrões são conectados por uma aresta se compartilham pelo menos uma peça.

Fluxo típico:
    1. A matriz padrão x peça é lida a partir de um arquivo .txt.
    2. Esta matriz é passada para a função `construir_grafo`.
    3. A função retorna um grafo NetworkX (nx.Graph), que pode ser explorado com algoritmos de busca, heurísticas, etc.

Função disponível:
    - construir_grafo(matriz_padroes_pecas)

Exemplo de uso:
    from mosp.grafo import construir_grafo
    grafo = construir_grafo(matriz_padroes_pecas)
"""

import networkx as nx
import numpy as np

def construir_grafo(matriz_padroes_pecas):
    """
    Constrói o grafo padrão-padrão a partir da matriz padrão x peça.

    Args:
        matriz_padroes_pecas: Matriz binária (n_padroes x n_pecas), onde:
                              - Cada linha representa um padrão.
                              - Cada coluna representa uma peça.
                              - Valor 1 indica que o padrão utiliza a peça.

    Returns:
        grafo: Objeto nx.Graph, onde:
               - Cada vértice representa um padrão.
               - Uma aresta é adicionada entre dois padrões se eles compartilham pelo menos uma peça.
    """
    num_padroes = matriz_padroes_pecas.shape[0]
    grafo = nx.Graph()

    # Adiciona todos os padrões como vértices
    grafo.add_nodes_from(range(num_padroes))

    # Verifica cada par de padrões e adiciona arestas quando necessário
    for padrao_i in range(num_padroes):
        for padrao_j in range(padrao_i + 1, num_padroes):
            if np.any(matriz_padroes_pecas[padrao_i] & matriz_padroes_pecas[padrao_j]):
                grafo.add_edge(padrao_i, padrao_j)

    return grafo
