"""
Este arquivo contém as heurísticas utilizadas para gerar ordens de produção no problema MOSP.

Descrição:
    - Diferente das buscas clássicas (BFS, DFS), estas heurísticas aplicam estratégias adaptativas ou aleatórias para gerar uma ordem de produção.
    - A heurística híbrida decide dinamicamente entre usar BFS ou DFS em cada componente do grafo, com base na densidade do componente.
    - A heurística aleatória simplesmente gera uma ordem aleatória dos padrões (baseline para comparação).

Uso no projeto:
    - As heurísticas geram ordens de produção que serão avaliadas com a função de custo (NMPA).
    - Essas ordens são usadas no benchmark para comparar diferentes estratégias.

Funções disponíveis:
    - heuristica_hibrida_adaptativa(grafo, matriz)
    - aleatoria(grafo)

Exemplo de uso:
    from mosp.heuristicas import heuristica_hibrida_adaptativa, aleatoria

    ordem_hibrida = heuristica_hibrida_adaptativa(grafo)
    ordem_aleatoria = aleatoria(grafo)
"""

import networkx as nx
import itertools
import random
from .busca_bfs import bfs_adaptativo
from .busca_dfs import dfs_limitado
from .custo_nmpa import calcular_nmpa
import numpy as np


def calcular_metricas_componente(subgrafo, matPaPe):
    """
    Calcula métricas estruturais de um subgrafo (componente conectado),
    com o objetivo de caracterizá-lo e apoiar a escolha de estratégias
    de travessia mais adequadas (BFS ou DFS) na heurística principal.

    Métricas calculadas:
    - Densidade: quão interconectado é o subgrafo (valor entre 0 e 1).
    - Clustering: grau médio de agrupamento (triângulos locais).
    - Grau médio: número médio de conexões por padrão.
    - Diversidade: proporção de tipos de peças presentes no componente.

    Args:
        subgrafo (nx.Graph): componente conectado do grafo padrão × padrão.
        matPaPe (np.ndarray): matriz binária padrão x peça.

    Returns:
        dict: dicionário com as métricas calculadas.
    """

    # Mede a densidade do subgrafo: quantas conexões existem
    # em relação ao número máximo possível de conexões
    densidade = nx.density(subgrafo)

    # Mede o clustering médio: indica formação de \"grupos fechados\"
    clustering = nx.average_clustering(subgrafo)

    # Extrai o grau de cada vértice do subgrafo
    graus = dict(subgrafo.degree())

    # Soma a ocorrência de cada peça nos padrões do componente
    pecas_componente = np.sum(matPaPe[list(subgrafo.nodes())], axis=0)

    # Calcula a diversidade: proporção de peças diferentes presentes no componente
    diversidade = np.sum(pecas_componente > 0) / matPaPe.shape[1]

    # Retorna todas as métricas em formato de dicionário
    return {
        'densidade': densidade,
        'clustering': clustering,
        'grau_medio': sum(graus.values()) / len(subgrafo),
        'diversidade': diversidade
    }


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

# Refinamento global e local com trocas entre posições
# ------------------------------
def refinamento_diferenciado(sequencia, matPaPe, n_iter=5):
    melhor_seq = sequencia.copy()
    melhor_nmpa = calcular_nmpa(sequencia, matPaPe)

    for _ in range(n_iter):
        for i in range(len(sequencia) - 1):
            nova_seq = sequencia.copy()
            nova_seq[i], nova_seq[i + 1] = nova_seq[i + 1], nova_seq[i]  # Troca adjacente
            novo_nmpa = calcular_nmpa(nova_seq, matPaPe)

            if novo_nmpa < melhor_nmpa:
                melhor_seq, melhor_nmpa = nova_seq, novo_nmpa

            # Trocas não adjacentes para explorar mais o espaço de soluções
            if i < len(sequencia) - 3:
                for j in range(i + 2, min(i + 5, len(sequencia))):
                    nova_seq = sequencia.copy()
                    nova_seq[i], nova_seq[j] = nova_seq[j], nova_seq[i]
                    novo_nmpa = calcular_nmpa(nova_seq, matPaPe)

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
        nmpa_local = calcular_nmpa(sequencia[i:i + janela], matPaPe)
        if nmpa_local > max_pilhas:
            max_pilhas = nmpa_local
            pior_inicio = i

    bloco = sequencia[pior_inicio:pior_inicio + janela]
    melhor_bloco = bloco.copy()
    melhor_nmpa = max_pilhas

    for perm in itertools.permutations(bloco):
        nova_sequencia = sequencia[:pior_inicio] + list(perm) + sequencia[pior_inicio + janela:]
        novo_nmpa = calcular_nmpa(nova_sequencia, matPaPe)
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


def heuristica_hibrida_adaptativa(grafo, matPaPe):
   
    """
    Gera uma ordem de produção utilizando a heurística híbrida adaptativa.

    A ideia principal é explorar a estrutura do grafo padrão × padrão (ADRA),
    aplicando estratégias diferentes dependendo da conectividade de cada componente.

    - Em componentes densos: usa-se BFS (exploração em largura) para aproveitar peças compartilhadas.
    - Em componentes esparsos: usa-se DFS (exploração em profundidade) para fechar pilhas rapidamente.
    - Em componentes moderados: aplica-se BFS com profundidade maior para equilibrar ambos os efeitos.

    Ao final, um refinamento é aplicado para tentar reduzir ainda mais o número máximo de pilhas abertas (NMPA).

    Args:
        G (nx.Graph): grafo padrão × padrão com arestas indicando peças compartilhadas entre padrões.
        matPaPe (np.ndarray): matriz binária padrão × peça.

    Returns:
        list: sequência final de padrões que minimiza as pilhas abertas ao longo da produção.
    """
    sequencia_final = []  # Lista que irá conter a ordem global final de execução dos padrões

    # Percorre cada componente conectado do grafo
    for componente in nx.connected_components(grafo):
        subgrafo = grafo.subgraph(componente)  # Cria o subgrafo apenas com os nós do componente atual

        # Caso o componente tenha apenas um padrão, já adiciona direto à sequência
        if len(componente) == 1:
            sequencia_final.extend(componente)
            continue

        # Calcula métricas como densidade e diversidade do componente
        metricas = calcular_metricas_componente(subgrafo, matPaPe)

        # Seleciona o padrão inicial de forma inteligente, considerando peças críticas e conectividade
        no_inicial = selecionar_no_inicial(subgrafo, matPaPe)

        # Aplica a estratégia de travessia de acordo com a densidade do subgrafo
        if metricas['densidade'] > 0.6:
            # Componente denso → BFS com menor profundidade (evita explosão de pilhas)
            sequencia = bfs_adaptativo(subgrafo, no_inicial, matPaPe, profundidade_max=2)
        elif metricas['densidade'] >= 0.3:
            # Componente moderado → BFS mais profundo (mistura de exploração e fechamento)
            sequencia = bfs_adaptativo(subgrafo, no_inicial, matPaPe, profundidade_max=3)
        else:
            # Componente esparso → DFS limitada, ideal para fechar pilhas rapidamente
            visitados = set()
            sequencia = dfs_limitado(subgrafo, no_inicial, visitados, matPaPe, limite=3)

        # Junta a sequência local ao resultado final
        sequencia_final.extend(sequencia)

    # Aplica um refinamento global final na sequência completa (melhora o NMPA)
    return refinamento_hibrido(sequencia_final, matPaPe)

def aleatoria(grafo):
    """
    Gera uma ordem de produção aleatória.

    Esta heurística serve como baseline no benchmark.

    Args:
        grafo: Objeto nx.Graph (grafo padrão-padrão).

    Returns:
        ordem: Lista de padrões (vértices) em ordem aleatória.
    """
    vertices = list(grafo.nodes())
    random.shuffle(vertices)
    return vertices
