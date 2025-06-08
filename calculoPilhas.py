import numpy as np
import networkx as nx
from DFS import DFS, dfs_limitado  # Funções personalizadas de busca em profundidade
from BFS import BFS, bfs_adaptativo  # Funções personalizadas de busca em largura
import random
from collections import deque, defaultdict
from sklearn.cluster import AgglomerativeClustering  # (Importado mas não utilizado)
import itertools

# ------------------------------
# Função para ler a instância (matriz padrão x peça) a partir de um arquivo
# ------------------------------
def criaMatPadraoPeca(instancia):
    caminho = instancia + '.txt'  # Monta o caminho para o arquivo da instância
    with open(caminho, 'rb') as f:
        nrows, ncols = [int(field) for field in f.readline().split()]  # Lê dimensões
        data = np.genfromtxt(f, dtype="int32", max_rows=nrows)  # Lê os dados como matriz binária
    return data

# ------------------------------
# Função que calcula o número máximo de pilhas abertas (NMPA)
# ------------------------------
def NMPA(LP, matPaPe):
    if len(LP) > 1:
        Q = matPaPe[LP, :]  # Seleciona os padrões da sequência
        # Calcula a quantidade de pilhas abertas em cada instante
        Q = np.maximum.accumulate(Q, axis=0) & np.maximum.accumulate(Q[::-1, :], axis=0)[::-1, :]
        pa = np.sum(Q, 1)
    else:
        Q = matPaPe[LP, :]
        pa = [np.sum(Q)]
    return np.amax(pa)  # Retorna o maior número de pilhas abertas em qualquer instante

# ------------------------------
# Constrói o grafo padrão x padrão (ADRA)
# ------------------------------
def construir_grafo(matPaPe):
    n_padroes = matPaPe.shape[0]
    G = nx.Graph()
    G.add_nodes_from(range(n_padroes))  # Adiciona cada padrão como vértice

    for i in range(n_padroes):
        for j in range(i + 1, n_padroes):
            if np.any(matPaPe[i] & matPaPe[j]):  # Se compartilham pelo menos uma peça
                G.add_edge(i, j)

    return G

# ------------------------------
# Calcula métricas estruturais do componente conectado
# ------------------------------
def calcular_metricas_componente(subgrafo, matPaPe):
    densidade = nx.density(subgrafo)
    clustering = nx.average_clustering(subgrafo)
    graus = dict(subgrafo.degree())

    # Mede a diversidade de peças do componente (proporção de peças presentes)
    pecas_componente = np.sum(matPaPe[list(subgrafo.nodes())], axis=0)
    diversidade = np.sum(pecas_componente > 0) / matPaPe.shape[1]

    return {
        'densidade': densidade,
        'clustering': clustering,
        'grau_medio': sum(graus.values()) / len(subgrafo),
        'diversidade': diversidade
    }

# ------------------------------
# Seleciona o nó inicial com base em critérios de conectividade e criticidade de peças
# ------------------------------
def selecionar_no_inicial(subgrafo, matPaPe):
    nos = list(subgrafo.nodes())

    # Identifica as peças mais presentes no componente
    pecas_componente = np.sum(matPaPe[nos], axis=0)
    pecas_criticas = np.argsort(-pecas_componente)[:3]  # Top 3 peças mais usadas

    scores = []
    for no in nos:
        grau = subgrafo.degree(no)
        peso_pecas_criticas = np.sum(matPaPe[no][pecas_criticas])
        penalidade_pecas = 0.2 * np.sum(matPaPe[no])  # Penaliza padrões com muitas peças

        score = (0.4 * grau + 0.5 * peso_pecas_criticas - penalidade_pecas)
        scores.append(score)

    return nos[np.argmax(scores)]  # Retorna o nó com melhor pontuação

# ------------------------------
# Refinamento global e local com trocas entre posições
# ------------------------------
def refinamento_diferenciado(sequencia, matPaPe, n_iter=5):
    melhor_seq = sequencia.copy()
    melhor_nmpa = NMPA(sequencia, matPaPe)

    for _ in range(n_iter):
        for i in range(len(sequencia) - 1):
            nova_seq = sequencia.copy()
            nova_seq[i], nova_seq[i + 1] = nova_seq[i + 1], nova_seq[i]  # Troca adjacente
            novo_nmpa = NMPA(nova_seq, matPaPe)

            if novo_nmpa < melhor_nmpa:
                melhor_seq, melhor_nmpa = nova_seq, novo_nmpa

            # Trocas não adjacentes para explorar mais o espaço de soluções
            if i < len(sequencia) - 3:
                for j in range(i + 2, min(i + 5, len(sequencia))):
                    nova_seq = sequencia.copy()
                    nova_seq[i], nova_seq[j] = nova_seq[j], nova_seq[i]
                    novo_nmpa = NMPA(nova_seq, matPaPe)

                    if novo_nmpa < melhor_nmpa:
                        melhor_seq, melhor_nmpa = nova_seq, novo_nmpa

        sequencia = melhor_seq.copy()

    return melhor_seq

# ------------------------------
# Refinamento focado em "hotspots" de pilhas abertas
# ------------------------------
def refinamento_hotspots(sequencia, matPaPe, janela=5):
    max_pilhas = 0
    pior_inicio = 0
    for i in range(len(sequencia) - janela + 1):
        nmpa_local = NMPA(sequencia[i:i + janela], matPaPe)
        if nmpa_local > max_pilhas:
            max_pilhas = nmpa_local
            pior_inicio = i

    bloco = sequencia[pior_inicio:pior_inicio + janela]
    melhor_bloco = bloco.copy()
    melhor_nmpa = max_pilhas

    for perm in itertools.permutations(bloco):
        nova_sequencia = sequencia[:pior_inicio] + list(perm) + sequencia[pior_inicio + janela:]
        novo_nmpa = NMPA(nova_sequencia, matPaPe)
        if novo_nmpa < melhor_nmpa:
            melhor_bloco = perm
            melhor_nmpa = novo_nmpa

    return sequencia[:pior_inicio] + list(melhor_bloco) + sequencia[pior_inicio + janela:]

# ------------------------------
# Aplica ambos os refinamentos sequencialmente
# ------------------------------
def refinamento_hibrido(sequencia, matPaPe):
    seq = refinamento_diferenciado(sequencia, matPaPe, n_iter=3)
    if len(seq) > 10:
        seq = refinamento_hotspots(seq, matPaPe)
    return seq

# ------------------------------
# Função principal da heurística híbrida adaptativa
# ------------------------------
def heuristica_hibrida_completa(G, matPaPe):
    sequencia_final = []

    for componente in nx.connected_components(G):
        subgrafo = G.subgraph(componente)

        if len(componente) == 1:
            sequencia_final.extend(componente)
            continue

        metricas = calcular_metricas_componente(subgrafo, matPaPe)
        no_inicial = selecionar_no_inicial(subgrafo, matPaPe)

        # Escolhe a estratégia com base na densidade
        if metricas['densidade'] > 0.6:
            sequencia = bfs_adaptativo(subgrafo, no_inicial, matPaPe, profundidade_max=2)
        elif metricas['densidade'] >= 0.3:
            sequencia = bfs_adaptativo(subgrafo, no_inicial, matPaPe, profundidade_max=3)
        else:
            visitados = set()
            sequencia = dfs_limitado(subgrafo, no_inicial, visitados, matPaPe, limite=3)

        sequencia_final.extend(sequencia)

    # Aplica refinamento final na sequência global
    return refinamento_hibrido(sequencia_final, matPaPe)
