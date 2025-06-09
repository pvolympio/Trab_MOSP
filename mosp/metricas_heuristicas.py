import networkx as nx
import numpy as np
from .custo_nmpa import calcular_nmpa
import itertools
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
