import numpy as np
import networkx as nx
from DFS import  DFS
from BFS import BFS
import random
from collections import deque

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

def heuristica_hibrida_por_densidade(G):
    """
    Heurística híbrida por densidade:
    - Usa BFS como padrão
    - Usa DFS apenas em componentes grandes e esparsos (densidade < 0.2 e > 4 nós)
    """
    visitados = set()
    seq_final = []

    # Primeiro componente (vértice de maior grau)
    v_inicial = max(G.degree, key=lambda x: x[1])[0]
    componente_inicial = nx.node_connected_component(G, v_inicial)
    subgrafo_inicial = G.subgraph(componente_inicial)
    densidade = nx.density(subgrafo_inicial)

    if len(subgrafo_inicial) > 4 and densidade < 0.2:
        seq = DFS(subgrafo_inicial, v_inicial)
    else:
        seq = BFS(subgrafo_inicial, v_inicial)

    seq_final.extend(seq)
    visitados.update(seq)

    # Demais componentes
    for componente in nx.connected_components(G):
        comp_nao_visitados = [v for v in componente if v not in visitados]
        if not comp_nao_visitados:
            continue

        subgrafo = G.subgraph(comp_nao_visitados)
        v_inicio = comp_nao_visitados[0]
        densidade = nx.density(subgrafo)

        if len(subgrafo) > 4 and densidade < 0.2:
            seq = DFS(subgrafo, v_inicio)
        else:
            seq = BFS(subgrafo, v_inicio)

        seq_final.extend(seq)
        visitados.update(seq)

    return seq_final


def aleatoria(grafo):
    """Gera uma ordem aleatória dos padrões."""
    vertices = list(grafo.nodes())
    random.shuffle(vertices)
    return vertices

def similaridade(matPaPe, u, v):
    return np.dot(matPaPe[u], matPaPe[v])

def metrica_combinada(G_sub):
    dens = nx.density(G_sub)
    cluster = nx.average_clustering(G_sub)
    return 0.6 * dens + 0.4 * cluster

def diversidade_pecas(matPaPe, indices):
    submat = matPaPe[indices, :]
    usos = np.sum(submat, axis=1)
    return np.mean(usos)

def ordenar_vizinhos_lookahead(G, atual, matPaPe, visitados, profundidade=1):
    vizinhos = [v for v in G.neighbors(atual) if v not in visitados]
    pontuacoes = []

    for v in vizinhos:
        score = similaridade(matPaPe, atual, v)
        if profundidade > 1:
            sub_viz = [u for u in G.neighbors(v) if u not in visitados and u != atual]
            score += sum(similaridade(matPaPe, v, u) for u in sub_viz)
        pontuacoes.append((v, score))

    pontuacoes.sort(key=lambda x: x[1], reverse=True)
    return [v for v, _ in pontuacoes]

def bfs_por_similaridade(G, v_inicial, matPaPe):
    visitados = set([v_inicial])
    fila = deque([v_inicial])
    resultado = []

    while fila:
        atual = fila.popleft()
        resultado.append(atual)
        vizinhos_ordenados = ordenar_vizinhos_lookahead(G, atual, matPaPe, visitados, profundidade=1)
        for vizinho in vizinhos_ordenados:
            visitados.add(vizinho)
            fila.append(vizinho)

    return resultado

def dfs_por_similaridade(G, v_inicial, matPaPe):
    visitados = set()
    pilha = [v_inicial]
    resultado = []

    while pilha:
        atual = pilha.pop()
        if atual not in visitados:
            visitados.add(atual)
            resultado.append(atual)
            vizinhos_ordenados = ordenar_vizinhos_lookahead(G, atual, matPaPe, visitados, profundidade=1)
            pilha.extend(reversed(vizinhos_ordenados))

    return resultado

def refinamento_local_avancado(LP, matPaPe, max_iter=2):
    from copy import deepcopy
    LP = deepcopy(LP)
    melhor_nmpa = NMPA(LP, matPaPe)

    for _ in range(max_iter):
        melhorou = False
        for i in range(0, len(LP) - 1, 2):  # reduz combinações
            for j in range(i + 1, min(i + 5, len(LP))):  # trocas locais
                LP[i], LP[j] = LP[j], LP[i]
                novo_nmpa = NMPA(LP, matPaPe)
                if novo_nmpa < melhor_nmpa:
                    melhor_nmpa = novo_nmpa
                    melhorou = True
                else:
                    LP[i], LP[j] = LP[j], LP[i]
        if not melhorou:
            break
    return LP

def heuristica_hibrida_avancada(G, matPaPe):
    visitados = set()
    seq_final = []

    for componente in nx.connected_components(G):
        subgrafo = G.subgraph(componente)
        tamanho = len(subgrafo)
        n_start = min(3, max(1, tamanho // 4))  # menor número de vértices por componente
        melhor_seq = None
        melhor_nmpa = float("inf")

        candidatos = random.sample(list(subgrafo.nodes()), min(n_start, tamanho))

        for v_inicio in candidatos:
            score_conect = metrica_combinada(subgrafo)
            score_diversidade = diversidade_pecas(matPaPe, list(subgrafo.nodes()))
            limiar = 0.25 + 0.05 * np.log10(tamanho + 1)

            if score_diversidade < 2.5:
                score_conect += 0.1

            if score_conect >= limiar:
                seq = bfs_por_similaridade(subgrafo, v_inicio, matPaPe)
            else:
                seq = dfs_por_similaridade(subgrafo, v_inicio, matPaPe)

            nmpa = NMPA(seq, matPaPe)
            if nmpa < melhor_nmpa:
                melhor_seq = seq
                melhor_nmpa = nmpa

        seq_final.extend(melhor_seq)
        visitados.update(melhor_seq)

    # Só refina se o NMPA for alto
    if NMPA(seq_final, matPaPe) >= 6:
        return refinamento_local_avancado(seq_final, matPaPe)
    return seq_final