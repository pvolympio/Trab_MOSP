"""
Este arquivo contém as funções responsáveis pelo cálculo de métricas estruturais dos componentes do grafo e pela seleção heurística do nó inicial de travessia.

Descrição:
    - As métricas caracterizam a conectividade e diversidade de cada componente conectado do grafo padrão x padrão.
    - A seleção do nó inicial busca identificar padrões críticos, considerando grau de conectividade e relevância das peças, para orientar as travessias.

Contexto:
    - No problema MOSP, essas métricas apoiam a definição de estratégias adaptativas de busca (BFS ou DFS), explorando a estrutura do grafo na geração de sequências produtivas.

Funções disponíveis:
    - calcular_metricas_componente(subgrafo, matPaPe)
    - selecionar_no_inicial(subgrafo, matPaPe)

Exemplo de uso:
    from mosp.metricas import calcular_metricas_componente, selecionar_no_inicial
"""

import networkx as nx
import numpy as np

def calcular_metricas_componente(subgrafo, matPaPe):
    """
    Calcula métricas estruturais de um subgrafo (componente conectado), com o objetivo de caracterizá-lo e apoiar a escolha de estratégias de travessia mais adequadas (BFS ou DFS) na heurística principal.

    Métricas calculadas:
        - Densidade: quão interconectado é o subgrafo (valor entre 0 e 1).
        - Clustering: grau médio de agrupamento (triângulos locais).
        - Grau médio: número médio de conexões por padrão.
        - Diversidade: proporção de tipos de peças presentes no componente.

    Parâmetros:
        subgrafo (nx.Graph): componente conectado do grafo padrão x padrão.
        matPaPe (np.ndarray): matriz binária padrão x peça.

    Retorno:
        dict: dicionário com as métricas calculadas.
    """
    densidade = nx.density(subgrafo)
    clustering = nx.average_clustering(subgrafo)
    graus = dict(subgrafo.degree())
    pecas_componente = np.sum(matPaPe[list(subgrafo.nodes())], axis=0)
    diversidade = np.sum(pecas_componente > 0) / matPaPe.shape[1]

    return {
        'densidade': densidade,
        'clustering': clustering,
        'grau_medio': sum(graus.values()) / len(subgrafo),
        'diversidade': diversidade
    }

def selecionar_no_inicial(subgrafo, matPaPe):
    """
    Seleciona (a partir de heurística) o nó inicial de travessia com base na conectividade e criticidade de peças.

    Critérios considerados:
        - Grau do vértice.
        - Número de peças críticas presentes.
        - Penalização para padrões que utilizam muitas peças simultaneamente.

    Parâmetros:
        subgrafo (nx.Graph): componente conectado do grafo.
        matPaPe (np.ndarray): matriz binária padrão x peça.

    Retorno:
        int: índice do padrão selecionado como ponto inicial da travessia.
    """
    nos = list(subgrafo.nodes())
    pecas_componente = np.sum(matPaPe[nos], axis=0)
    pecas_criticas = np.argsort(-pecas_componente)[:3]

    scores = []
    for no in nos:
        grau = subgrafo.degree(no)
        peso_pecas_criticas = np.sum(matPaPe[no][pecas_criticas])
        penalidade_pecas = 0.2 * np.sum(matPaPe[no])
        score = (0.4 * grau + 0.5 * peso_pecas_criticas - penalidade_pecas)
        scores.append(score)

    return nos[np.argmax(scores)]