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

def dfs_adaptado(subgrafo, no_inicial, matPaPe, limite=2):
    """
    Executa uma busca em profundidade (DFS) otimizada com profundidade limitada.

    Ideia central:
    - A DFS tradicional segue o caminho até onde puder antes de voltar.
    - Aqui, impomos um limite de profundidade (parâmetro `limite`), evitando que a busca se aprofunde demais.
    - Os vizinhos são ordenados com base em similaridade com o nó atual, favorecendo caminhos "tematicamente coesos".

   

    Racional do limite:
    - Limitar a profundidade evita que a DFS vá longe demais em caminhos ruins.
    - Um limite pequeno (ex: 2) já oferece controle e evita explorações "exageradas".
    """

    pilha = [(no_inicial, 0)]          # Pilha para DFS (estrutura LIFO), armazenando também a profundidade atual
    visitados = set()                  # Conjunto de nós já visitados
    sequencia = []                     # Sequência final de visitação

    while pilha:
        no_atual, profundidade = pilha.pop()
        if no_atual not in visitados:
            visitados.add(no_atual)
            sequencia.append(no_atual)

            if profundidade < limite:
                # Seleciona vizinhos ainda não visitados
                vizinhos = [v for v in subgrafo.neighbors(no_atual) if v not in visitados]
                if vizinhos:
                    # Similaridade entre o nó atual e os vizinhos
                    similaridades = np.sum(matPaPe[no_atual] & matPaPe[vizinhos], axis=1)

                    # Ordena vizinhos pela similaridade decrescente (mais parecidos primeiro)
                    ordenados = [v for _, v in sorted(zip(similaridades, vizinhos), reverse=True)]

                    # Adiciona os vizinhos à pilha com profundidade incrementada (reversed para manter ordem no LIFO)
                    pilha.extend((v, profundidade + 1) for v in reversed(ordenados))

    return sequencia