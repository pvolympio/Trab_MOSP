# -*- coding: utf-8 -*-

"""
Este arquivo contém as funções de Busca em Profundidade (DFS) para percorrer o grafo padrão-padrão.

Descrição:
    - Dadas listas de adjacência ou subgrafos, as funções geram ordens de visitação dos padrões (vértices) utilizando variações da DFS.
    - A função 'dfs' implementa a DFS clássica pura, garantindo a cobertura de todos os padrões, mesmo em componentes desconexas.
    - A função 'dfs_limitado' implementa uma DFS com profundidade máxima controlada, priorizando vizinhos com maior similaridade de peças, de modo a balancear exploração e fechamento precoce de pilhas.

Uso no projeto:
    - As buscas geram ordens de produção que serão avaliadas com a função de custo (NMPA).
    - Essas ordens são usadas no benchmark para comparar diferentes estratégias de busca e adaptação.

Funções disponíveis:
    - dfs(lista_adjacencia, vertice_inicial):
        - Realiza a DFS tradicional sobre o grafo.
    - dfs_limitado(subgrafo, no_inicial, visitados, matPaPe, limite=2):
        - Realiza uma DFS limitada em profundidade, priorizando vizinhos mais similares na escolha de expansão.

Exemplo de uso:
    from mosp.busca_dfs import dfs, dfs_limitado
    ordem_dfs = dfs(lista_adjacencia, vertice_inicial)
    ordem_limitada = dfs_limitado(subgrafo, no_inicial, visitados, matriz_padroes_pecas, limite=2)
"""

import numpy as np

def dfs(lista_adjacencia, vertice_inicial):
    """
    Executa a Busca em Profundidade (DFS) no grafo padrão-padrão ou subgrafo.

    Compatível com subgrafos (ex: comunidades detectadas).

    Args:
        lista_adjacencia: Dicionário {vértice: lista de vizinhos}.
        vertice_inicial: Índice do vértice de início da busca.

    Returns:
        ordem: Lista de padrões (vértices) na ordem em que foram visitados pela DFS.
               Se o grafo tiver componentes desconexas, os padrões isolados ou de outras componentes serão adicionados ao final da ordem.
    """
    # Correção: pegar os vértices reais, não um range de 0 até N-1
    todos_vertices = list(lista_adjacencia.keys())

    visitados = []
    pilha = [vertice_inicial]

    # Enquanto ainda houver vértices não visitados
    while todos_vertices:
        # Enquanto a pilha não estiver vazia
        while pilha:
            vertice_atual = pilha[0]

            if vertice_atual not in visitados:
                visitados.append(vertice_atual)

            # Encontra os vizinhos que ainda não foram visitados
            vizinhos_nao_visitados = list(set(lista_adjacencia[vertice_atual]) - set(visitados))
            vizinhos_nao_visitados.sort()

            if vizinhos_nao_visitados:
                pilha.insert(0, vizinhos_nao_visitados[0])
            else:
                pilha.pop(0)

        # Após terminar um componente, atualiza a lista de vértices não visitados
        todos_vertices = list(set(todos_vertices) - set(visitados))

        # Se ainda houver vértices não visitados, começa nova DFS por outro componente
        if todos_vertices:
            pilha = [todos_vertices[0]]

    return visitados

def dfs_adaptado(subgrafo, no_inicial, visitados, matPaPe, limite=2):
    """
    Executa uma busca em profundidade (DFS) com profundidade máxima controlada, priorizando a visita de vizinhos mais similares (com mais peças em comum).

    Args:
        subgrafo: componente do grafo principal (NetworkX Graph).
        no_inicial: vértice de partida.
        visitados: conjunto compartilhado para marcar nós visitados globalmente.
        matPaPe: matriz padrão x peça.
        limite: profundidade máxima permitida.

    Returns:
        Sequência de visita DFS (lista de padrões).
    """
    pilha = [(no_inicial, 0)] # Pilha DFS, com tuplas (nó, profundidade atual)
    sequencia = []

    while pilha:
        no_atual, profundidade = pilha.pop() # Retira o último da pilha

        if no_atual not in visitados:
            visitados.add(no_atual) # Marca como visitado
            sequencia.append(no_atual) # Adiciona à sequência

            if profundidade < limite:
                # Ordena os vizinhos por similaridade de peças, priorizando os mais parecidos
                vizinhos = sorted(subgrafo.neighbors(no_atual),
                                  key=lambda x: np.sum(matPaPe[no_atual] & matPaPe[x]),
                                  reverse=True)
                # Adiciona à pilha (reverso para manter ordem original de prioridade)
                pilha.extend((v, profundidade + 1) for v in reversed(vizinhos) if v not in visitados)

    return sequencia
