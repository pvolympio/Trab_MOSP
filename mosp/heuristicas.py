"""
Este arquivo contém as heurísticas adaptativas desenvolvidas para gerar ordens de produção no problema MOSP.

Descrição geral:
    - As heurísticas utilizam a modelagem por grafos para determinar boas sequências de execução dos padrões de corte.
    - Diferentes estratégias de travessia e priorização são aplicadas, considerando a estrutura de conectividade do grafo e o comportamento dinâmico do número máximo de pilhas abertas (NMPA).
    - As heurísticas exploram propriedades de densidade local, comunidades, componentes conexos e evolução temporal do NMPA.

Uso no projeto:
    - As heurísticas geram ordens de produção que são avaliadas com a função de custo (NMPA).
    - Servem de base para experimentação e benchmark de desempenho.

Funções disponíveis:
    - heuristica_comunidades_adaptativa(grafo, limiar_densidade=0.3)
    - heuristica_hibrida_adaptativa_pico(grafo, matriz, limiar_densidade=0.3)
    - heuristica_hibrida_por_componente(grafo, matPaPe)

Exemplo de uso:
    from mosp.heuristicas import (
        heuristica_comunidades_adaptativa,
        heuristica_hibrida_adaptativa_pico,
        heuristica_hibrida_por_componente
    )

    ordem_comunidades = heuristica_comunidades_adaptativa(grafo)
    ordem_pico = heuristica_hibrida_adaptativa_pico(grafo, matriz)
    ordem_por_componente = heuristica_hibrida_por_componente(grafo, matriz)
"""

import networkx as nx
import random
from mosp.busca_bfs import bfs, bfs_adaptativo
from mosp.busca_dfs import dfs, dfs_limitado
from mosp.metricas import calcular_metricas_componente, selecionar_no_inicial
from mosp.refinamento import refinamento_hibrido
from mosp.custo_nmpa import calcular_nmpa
from networkx.algorithms.community import greedy_modularity_communities

def heuristica_comunidades_adaptativa(grafo, limiar_densidade=0.3):
    """
    Gera uma ordem de produção utilizando comunidades (regiões densas).

    - Detecta comunidades internas com mais conexões internas do que externas.
    - Em cada comunidade:
        - Se densidade >= limiar → aplica BFS.
        - Caso contrário → aplica DFS.

    Args:
        grafo: Objeto nx.Graph.
        limiar_densidade: Limite para decidir BFS ou DFS.

    Returns:
        ordem_final: Lista de padrões (vértices).
        log_execucao: Lista de dicionários com log da busca em cada padrão.
    """
    visitados = set()
    ordem_final = []
    log_execucao = []

    comunidades = list(greedy_modularity_communities(grafo))

    for comunidade in comunidades:
        subgrafo = grafo.subgraph(comunidade)
        densidade = nx.density(subgrafo)
        vertice_inicio = next(iter(comunidade))

        lista_adjacencia = {v: list(subgrafo.neighbors(v)) for v in subgrafo.nodes()}

        if densidade >= limiar_densidade:
            ordem = bfs(lista_adjacencia, vertice_inicio)
            tipo_busca = "BFS"
        else:
            ordem = dfs(lista_adjacencia, vertice_inicio)
            tipo_busca = "DFS"

        for padrao in ordem:
            log_execucao.append({
                "Padrao": padrao,
                "Busca": tipo_busca,
                "DensidadeRegiao": densidade
            })

        ordem_final.extend(ordem)
        visitados.update(ordem)

    for vertice in grafo.nodes():
        if vertice not in visitados:
            ordem_final.append(vertice)
            log_execucao.append({
                "Padrao": vertice,
                "Busca": "SemComunidade",
                "DensidadeRegiao": 0.0
            })

    return ordem_final, log_execucao

def heuristica_hibrida_adaptativa_pico(grafo, matriz, limiar_densidade=0.3):
    """
    Gera uma ordem de produção adaptando dinamicamente a estratégia conforme o NMPA parcial.

    - Inicia com DFS.
    - Monitora o NMPA ao longo da travessia.
    - Ao atingir o pico (ou janela de pico), troca para BFS.

    Args:
        grafo: Objeto nx.Graph.
        matriz: Matriz padrão-peça.
        limiar_densidade: Não utilizado diretamente (mantido por padrão).

    Returns:
        ordem_final: Lista de padrões.
        log_execucao: Log detalhado da busca.
    """
    visitados = set()
    ordem_final = []
    log_execucao = []
    nmpa_parcial = 0
    nmpa_max = 0
    uso_bfs = False

    for componente in nx.connected_components(grafo):
        componentes_nao_visitados = [v for v in componente if v not in visitados]
        if not componentes_nao_visitados:
            continue

        subgrafo = grafo.subgraph(componentes_nao_visitados)
        vertice_inicio = componentes_nao_visitados[0]
        lista_adjacencia = {v: list(subgrafo.neighbors(v)) for v in subgrafo.nodes()}

        agenda = [vertice_inicio]
        tipo_busca = "DFS"

        while agenda:
            if tipo_busca == "DFS":
                padrao = agenda.pop()
            else:
                padrao = agenda.pop(0)

            if padrao in visitados:
                continue

            visitados.add(padrao)
            ordem_final.append(padrao)

            nmpa_parcial = calcular_nmpa(ordem_final, matriz)
            if nmpa_parcial > nmpa_max:
                nmpa_max = nmpa_parcial

            log_execucao.append({
                "Padrao": padrao,
                "Busca": tipo_busca,
                "NMPA_Parcial": nmpa_parcial
            })

            if not uso_bfs and nmpa_parcial >= nmpa_max * 0.95:
                tipo_busca = "BFS"
                uso_bfs = True

            vizinhos = [v for v in lista_adjacencia[padrao] if v not in visitados]

            if tipo_busca == "DFS":
                agenda.extend(vizinhos[::-1])
            else:
                agenda.extend(vizinhos)

    return ordem_final, log_execucao

def heuristica_hibrida_por_componente(grafo, matPaPe):
    """
    Aplica BFS ou DFS em cada componente do grafo, adaptando a profundidade com base em métricas estruturais.

    - Em componentes densos → BFS rasa.
    - Em componentes moderados → BFS profunda.
    - Em componentes esparsos → DFS limitada.

    Ao final, aplica um refinamento sobre a ordem obtida.

    Args:
        grafo: Objeto nx.Graph.
        matPaPe: Matriz padrão x peça.

    Returns:
        ordem_final: Lista de padrões após o refinamento.
        log_execucao: Log da estratégia adotada por componente.
    """
    log_execucao = []
    sequencia_final = []

    for componente in nx.connected_components(grafo):
        subgrafo = grafo.subgraph(componente)

        if len(componente) == 1:
            sequencia_final.extend(componente)
            continue

        metricas = calcular_metricas_componente(subgrafo, matPaPe)
        no_inicial = selecionar_no_inicial(subgrafo, matPaPe)

        if metricas['densidade'] > 0.6:
            sequencia = bfs_adaptativo(subgrafo, no_inicial, matPaPe, profundidade_max=2)
            tipo_busca = "BFS"
        elif metricas['densidade'] >= 0.3:
            sequencia = bfs_adaptativo(subgrafo, no_inicial, matPaPe, profundidade_max=3)
            tipo_busca = "BFS"
        else:
            visitados = set()
            sequencia = dfs_limitado(subgrafo, no_inicial, visitados, matPaPe, limite=3)
            tipo_busca = "DFS"

        for padrao in sequencia:
            log_execucao.append({
                "Padrao": padrao,
                "Densidade": metricas["densidade"],
                "Busca": tipo_busca
            })

        sequencia_final.extend(sequencia)

    return refinamento_hibrido(sequencia_final, matPaPe), log_execucao