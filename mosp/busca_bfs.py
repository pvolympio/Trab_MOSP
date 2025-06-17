"""
Este arquivo contém as funções de Busca em Largura (BFS) para percorrer o grafo padrão-padrão.

Descrição:
    - Dadas listas de adjacência ou subgrafos, as funções geram ordens de visitação dos padrões (vértices) utilizando variações da BFS.
    - A função 'bfs' implementa a BFS clássica pura, garantindo a cobertura de todos os padrões, mesmo em componentes desconexas.
    - A função 'bfs_adaptado' implementa uma BFS aprimorada com ordenação adaptativa dos vizinhos, considerando grau e similaridade de peças, buscando favorecer o agrupamento de padrões relacionados.

Uso no projeto:
    - As buscas geram ordens de produção que serão avaliadas com a função de custo (NMPA).
    - Essas ordens são usadas no benchmark para comparar diferentes estratégias de busca.

Funções disponíveis:
    - bfs(lista_adjacencia, vertice_inicial):
        Realiza a BFS tradicional sobre o grafo.
    - bfs_adaptado(subgrafo, no_inicial, matPaPe):
        Realiza a BFS adaptativa com priorização baseada em grau e similaridade de peças.

Exemplo de uso:
    from mosp.busca_bfs import bfs, bfs_adaptado
    ordem_bfs = bfs(lista_adjacencia, vertice_inicial)
    ordem_adapt = bfs_adaptado(subgrafo, no_inicial, matriz_padroes_pecas)
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
    """
    Executa uma busca em largura (BFS) otimizada para grafos densos.

    Ideia central:
    - A BFS tradicional expande os vértices em ondas (nível por nível).
    - Nesta versão, os vizinhos são ordenados com base em uma combinação ponderada:
        * Grau do nó (quantidade de conexões): 60%
        * Similaridade de peças (quantas peças em comum com o nó atual): 40%

    
    - A BFS explora os vizinhos próximos antes de se afastar, mantendo grupos de vértices "relacionados" mais unidos na sequência.
    - Isso reduz o risco de abrir pilhas novas cedo demais, favorecendo a minimização do NMPA no MOSP.
    """

    visitados = set()                   # Conjunto de nós já visitados
    fila = deque([no_inicial])         # Fila para BFS (estrutura FIFO)
    sequencia = []                     # Sequência final de visitação

    while fila:
        no_atual = fila.popleft()      # Pega o próximo da fila
        if no_atual not in visitados:
            visitados.add(no_atual)
            sequencia.append(no_atual)

            # Seleciona vizinhos ainda não visitados
            vizinhos = [v for v in subgrafo.neighbors(no_atual) if v not in visitados]
            if vizinhos:
                # Calcula o grau e a similaridade com o nó atual
                graus = np.array([subgrafo.degree(v) for v in vizinhos])
                similaridades = np.sum(matPaPe[no_atual] & matPaPe[vizinhos], axis=1)

                # Combinação ponderada entre grau e similaridade
                pesos = 0.6 * graus + 0.4 * similaridades

                # Ordena os vizinhos com base nesses pesos (prioriza mais conectados e mais semelhantes)
                ordenados = [v for _, v in sorted(zip(pesos, vizinhos), reverse=True)]

                # Adiciona os vizinhos ordenados à fila
                fila.extend(ordenados)

    return sequencia