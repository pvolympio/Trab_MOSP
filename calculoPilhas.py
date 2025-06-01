import numpy as np
import networkx as nx

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

Grafo = criaMatPadraoPeca("Cenário 3 - 1 - exemplo")

G = construir_grafo(Grafo)
print(G)