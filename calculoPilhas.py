import numpy as np
import networkx as nx
from networkx.algorithms.cluster import average_clustering
from networkx.algorithms.link_prediction import jaccard_coefficient
from DFS import dfs_completo, DFS
from BFS import BFS
import random

def criaMatPadraoPeca(instancia):
    caminho =  instancia + '.txt'
    with open(caminho, 'rb') as f:
        nrows, ncols = [int(field) for field in f.readline().split()]
        data = np.genfromtxt(f, dtype="int32", max_rows=nrows) #OBS. Instancias estao no formato padrao x peca
    return data

def NMPA(LP, matPaPe):
    if len(LP) > 1:
        Q = matPaPe[LP, :]
        Q = np.maximum.accumulate(Q, axis=0) & np.maximum.accumulate(Q[::-1, :], axis=0)[::-1, :]
        pa = np.sum(Q, 1)
    else: # Apenas usado no caso de matrizes com uma só coluna.
        Q = matPaPe[LP, :]
        pa = [np.sum(Q)]
    return np.amax(pa) # Obtém a maior pilha do vetor

def construir_grafo(matPaPe):
    n_padroes = matPaPe.shape[0]
    G = nx.Graph()

    # Adiciona todos os padrões como vértices
    G.add_nodes_from(range(n_padroes))

    # Adiciona arestas entre padrões que compartilham ao menos uma peça
    for i in range(n_padroes):
        for j in range(i + 1, n_padroes):
            if np.any(matPaPe[i] & matPaPe[j]):
                G.add_edge(i, j)

    return G

def conectividade_local(G_sub, alpha=0.6, beta=0.4):
    """
    Calcula a conectividade local combinando:
    - Clustering médio
    - Jaccard médio entre vértices conectados
    alpha + beta devem somar 1
    """
    clustering = average_clustering(G_sub)

    jaccard_scores = list(jaccard_coefficient(G_sub, G_sub.edges()))
    jaccard_valores = [s[2] for s in jaccard_scores]
    jaccard_medio = sum(jaccard_valores) / len(jaccard_valores) if jaccard_valores else 0

    return alpha * clustering + beta * jaccard_medio




def heuristica_hibrida_adaptativa(G, limiar_conectividade=0.3, alpha=0.6, beta=0.4):
    visitados = set()
    seq_final = []

    # Vértice de maior grau
    v_inicial = max(G.degree, key=lambda x: x[1])[0]
    componente_inicial = nx.node_connected_component(G, v_inicial)
    subgrafo_inicial = G.subgraph(componente_inicial)

    seq = BFS(subgrafo_inicial, v_inicial)
    seq_final.extend(seq)
    visitados.update(seq)

    # Processar componentes restantes
    for componente in nx.connected_components(G):
        comp_nao_visitados = [v for v in componente if v not in visitados]
        if not comp_nao_visitados:
            continue

        subgrafo = G.subgraph(comp_nao_visitados)
        v_inicio = comp_nao_visitados[0]

        # Caso especial: subgrafo desconectado ou com poucos vértices
        if subgrafo.number_of_nodes() <= 2 or subgrafo.degree(v_inicio) == 0:
            seq = dfs_completo(subgrafo)
        else:
            conectividade = conectividade_local(subgrafo, alpha, beta)
            if conectividade >= limiar_conectividade:
                seq = BFS(subgrafo, v_inicio)
            else:
                seq = DFS(subgrafo, v_inicio)

        seq_final.extend(seq)
        visitados.update(seq)

    return seq_final

def aleatoria(grafo):
    """Gera uma ordem aleatória dos padrões."""
    vertices = list(grafo.nodes())
    random.shuffle(vertices)
    return vertices