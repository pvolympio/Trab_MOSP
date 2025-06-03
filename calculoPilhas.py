import numpy as np
import networkx as nx
from DFS import DeepFirstSearch, DFSIterativa, DFS
from BFS import BFS

def criaMatPadraoPeca(instancia):
    caminho = 'cenarios/' + instancia + '.txt'
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




def heuristica_hibrida_adaptativa(G, limiar_densidade=0.3):
    visitados = set()
    seq_final = []

    # Vértice de maior grau
    v_inicial = max(G.degree, key=lambda x: x[1])[0]

    # Primeiro componente
    componente_inicial = nx.node_connected_component(G, v_inicial)
    subgrafo_inicial = G.subgraph(componente_inicial)
    
    seq = BFS(subgrafo_inicial, v_inicial)
    seq_final.extend(seq)
    visitados.update(seq)

    # Demais componentes
    for componente in nx.connected_components(G):
        comp_nao_visitados = [v for v in componente if v not in visitados]
        if not comp_nao_visitados:
            continue

        subgrafo = G.subgraph(comp_nao_visitados)
        densidade = nx.density(subgrafo)
        v_inicio = comp_nao_visitados[0]

        if densidade >= limiar_densidade:
            seq = BFS(subgrafo, v_inicio)
        else:
            seq = DFS(subgrafo, v_inicio)

        seq_final.extend(seq)
        visitados.update(seq)

    return seq_final