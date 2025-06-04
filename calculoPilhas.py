import numpy as np
import networkx as nx
import random
from DFS import DFS
from BFS import BFS

def carregar_matriz_padrao_peca(nome_arquivo):
    """Lê a matriz padrão x peça a partir de um arquivo."""
    caminho = nome_arquivo + '.txt'
    with open(caminho, 'rb') as f:
        nrows, ncols = [int(x) for x in f.readline().split()]
        matriz = np.genfromtxt(f, dtype='int32', max_rows=nrows)
    return matriz

import numpy as np

def calcular_maximo_pilhas_usando_padrao_padrao(ordem_padroes, matriz_padrao_peca):
    """
    Calcula o número máximo de pilhas abertas (peças simultaneamente ativas)
    com base na ordem de aplicação dos padrões.

    Parâmetros:
    - ordem_padroes: lista com a ordem dos padrões (índices dos vértices do grafo)
    - matriz_padrao_peca: matriz binária (padrão x peça), onde 1 indica uso da peça

    Retorna:
    - Um inteiro representando o número máximo de pilhas abertas em algum momento
    """
    if len(ordem_padroes) <= 1:
        return int(np.sum(matriz_padrao_peca[ordem_padroes[0]]))

    # Submatriz na ordem desejada
    Q = matriz_padrao_peca[ordem_padroes, :]
    
    # Acúmulo da esquerda para a direita
    acumulado_frente = np.maximum.accumulate(Q, axis=0)
    
    # Acúmulo da direita para a esquerda (reverso)
    acumulado_tras = np.maximum.accumulate(Q[::-1, :], axis=0)[::-1, :]
    
    # Peças que permanecem ativas entre o início e fim da sequência
    combinacao = acumulado_frente & acumulado_tras
    
    # Quantas peças estão ativas em cada etapa
    pilhas_por_etapa = np.sum(combinacao, axis=1)

    # Retorna o maior número de pilhas simultaneamente abertas
    return int(np.max(pilhas_por_etapa))


def gerar_matriz_padrao_padrao(matriz_padrao_peca):
    """Gera uma matriz padrão x padrão com base na sobreposição de peças."""
    return matriz_padrao_peca @ matriz_padrao_peca.T

def construir_grafo_por_pecas_em_comum(mat_padrao_peca):
    """Cria um grafo onde os nós são padrões, com arestas entre padrões que compartilham peças."""
    n_padroes = mat_padrao_peca.shape[0]
    G = nx.Graph()
    
    for i in range(n_padroes):
        G.add_node(i)
        for j in range(i + 1, n_padroes):
            # Se os padrões i e j compartilham ao menos uma peça
            if np.any(mat_padrao_peca[i] & mat_padrao_peca[j]):
                G.add_edge(i, j)
    
    return G

def heuristica_hibrida_por_densidade(grafo, limiar=0.3):
    """Define uma ordem de visita híbrida (BFS ou DFS) com base na densidade dos componentes."""
    visitados = set()
    ordem_total = []

    # Começa pelo nó com maior grau
    no_inicial = max(grafo.degree, key=lambda x: x[1])[0]
    componente = nx.node_connected_component(grafo, no_inicial)
    subgrafo = grafo.subgraph(componente)
    ordem = BFS(subgrafo, no_inicial)
    ordem_total.extend(ordem)
    visitados.update(ordem)

    # Visita os demais componentes
    for comp in nx.connected_components(grafo):
        restantes = [v for v in comp if v not in visitados]
        if not restantes:
            continue
        sub = grafo.subgraph(restantes)
        densidade = nx.density(sub)
        inicio = restantes[0]
        if densidade >= limiar:
            ordem = BFS(sub, inicio)
        else:
            ordem = DFS(sub, inicio)
        ordem_total.extend(ordem)
        visitados.update(ordem)

    return ordem_total

def ordem_aleatoria(grafo):
    """Gera uma ordem aleatória dos padrões."""
    vertices = list(grafo.nodes())
    random.shuffle(vertices)
    return vertices