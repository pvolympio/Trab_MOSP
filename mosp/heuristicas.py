"""
Este arquivo contém as heurísticas adaptativas desenvolvidas para gerar ordens de produção no problema MOSP.

Descrição geral:
    - As heurísticas utilizam a modelagem por grafos para gerar sequências de produção que buscam minimizar o número máximo de pilhas abertas (NMPA).
    - Três abordagens principais foram implementadas:
        - Heurística por comunidades: explora a densidade interna de subestruturas (comunidades) detectadas no grafo.
        - Heurística adaptativa por pico: adapta dinamicamente a estratégia durante a execução, monitorando o NMPA em tempo real.
        - Heurística por componentes: combina métricas estruturais, múltiplos nós iniciais e variações adaptadas de BFS e DFS em cada componente conexo.

Uso no projeto:
    - As heurísticas geram ordens de produção que são avaliadas com a função de custo (NMPA).
    - Servem de base para o benchmark comparativo de desempenho.

Funções disponíveis:
    - heuristica_hibrida_comunidades(grafo, limiar_densidade=0.3)
    - heuristica_hibrida_adaptativa_pico(grafo, matriz, limiar_densidade=0.3)
    - heuristica_hibrida_por_componente(grafo, matPaPe)

Exemplo de uso:
    from mosp.heuristicas import (
        heuristica_hibrida_comunidades,
        heuristica_hibrida_adaptativa_pico,
        heuristica_hibrida_por_componente
    )

    ordem_comunidades = heuristica_hibrida_comunidades(grafo)
    ordem_pico = heuristica_hibrida_adaptativa_pico(grafo, matriz)
    ordem_por_componente = heuristica_hibrida_por_componente(grafo, matriz)
"""

import networkx as nx
import random

import numpy as np
from mosp.busca_bfs import bfs, bfs_adaptado
from mosp.busca_dfs import dfs,dfs_adaptado


from mosp.busca_bfs import bfs, bfs_adaptado
from mosp.busca_dfs import dfs, dfs_adaptado

from mosp.metricas import ordenacao_rapida,melhores_nos_iniciais
from mosp.refinamento import refinamento_minimo
from mosp.custo_nmpa import calcular_nmpa
from networkx.algorithms.community import greedy_modularity_communities

def heuristica_hibrida_comunidades(grafo, limiar_densidade=0.3):
    """
    Gera uma ordem de produção utilizando comunidades (regiões densas).

    - Detecta comunidades internas com mais conexões internas do que externas.
    - Em cada comunidade:
        - Se densidade >= limiar: aplica BFS.
        - Caso contrário: aplica DFS.

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

    # Detectar comunidades
    comunidades = list(greedy_modularity_communities(grafo))

    # Processar cada comunidade
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

    # Garantir que todos os vértices estejam na ordem (caso alguma parte não detectada em comunidade)
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
    Gera uma ordem de produção utilizando uma heurística híbrida adaptativa baseada na evolução do NMPA.

    Motivação:
        - Observou-se que as heurísticas que aplicavam BFS desde o início (baseadas apenas na densidade do grafo) geravam ordens com NMPA muito semelhantes ao BFS puro.
        - Esta abordagem explora um comportamento mais adaptativo:
            - Inicia com DFS, que tende a postergar a abertura de pilhas.
            - Monitora a evolução do NMPA à medida que a sequência é construída.
            - Quando o NMPA atinge valores próximos do seu pico (ou janela de pico), a estratégia é alterada para BFS, favorecendo o fechamento simultâneo de pilhas restantes.

    Diferenças em relação às heurísticas anteriores:
        - Enquanto a 'heuristica_hibrida_comunidades' toma a decisão BFS/DFS com base na densidade de cada subestrutura, esta heurística adapta a estratégia dinamicamente com base no comportamento do próprio NMPA durante a execução.
        - A matriz padrão-peça é necessária para o cálculo contínuo do NMPA.

    Args:
        grafo: Objeto nx.Graph (grafo padrão-padrão).
        matriz: Matriz padrão-peça (necessária para cálculo do NMPA).
        limiar_densidade: (opcional) não é utilizado diretamente nesta heurística.

    Returns:
        ordem_final: Lista de padrões (vértices) na ordem gerada.
        log_execucao: Lista de dicionários com log detalhado da busca (padrão, tipo de busca, NMPA parcial).
    """

    visitados = set()
    ordem_final = []
    log_execucao = []

    nmpa_parcial = 0
    nmpa_max = 0
    uso_bfs = False # Flag para indicar se já começamos a usar BFS

    # Começa pelo componente principal
    for componente in nx.connected_components(grafo):
        componentes_nao_visitados = [v for v in componente if v not in visitados]
        if not componentes_nao_visitados:
            continue

        subgrafo = grafo.subgraph(componentes_nao_visitados)
        vertice_inicio = componentes_nao_visitados[0]
        lista_adjacencia = {v: list(subgrafo.neighbors(v)) for v in subgrafo.nodes()}

        # Vamos usar uma lista "agenda" de padrões a explorar
        # Começamos com DFS (pilha)
        agenda = [vertice_inicio]
        tipo_busca = "DFS"

        while agenda:
            if tipo_busca == "DFS":
                padrao = agenda.pop() # Pilha (último elemento)
            else:
                padrao = agenda.pop(0) # Fila (primeiro elemento) - vira BFS

            if padrao in visitados:
                continue

            # Marca como visitado e adiciona à ordem
            visitados.add(padrao)
            ordem_final.append(padrao)

            # Atualiza NMPA parcial
            nmpa_parcial = calcular_nmpa(ordem_final, matriz)

            # Atualiza o NMPA máximo observado
            if nmpa_parcial > nmpa_max:
                nmpa_max = nmpa_parcial

            # Log do passo
            log_execucao.append({
                "Padrao": padrao,
                "Busca": tipo_busca,
                "NMPA_Parcial": nmpa_parcial
            })

            # Se atingimos o pico muda para BFS
            # Aqui podemos ajustar o critério: ex. muda para BFS quando o NMPA atual >= 95% do NMPA máximo observado até agora
            if not uso_bfs and nmpa_parcial >= nmpa_max * 0.95:
                tipo_busca = "BFS"
                uso_bfs = True

            # Adiciona vizinhos não visitados à agenda
            vizinhos = [v for v in lista_adjacencia[padrao] if v not in visitados]

            if tipo_busca == "DFS":
                agenda.extend(vizinhos[::-1]) # Para DFS, adiciona na ordem inversa
            else:
                agenda.extend(vizinhos) # Para BFS, adiciona no final da fila

    return ordem_final, log_execucao




def heuristica_hibrida_por_componente(grafo, matPaPe):
    """
    Heurística híbrida BFS/DFS adaptativa por componente conexo do grafo.

    Estratégia:
    - Divide o grafo em componentes conexos.
    - Aplica uma heurística adaptativa em cada componente:
        * BFS se densidade > 0.4
        * DFS se densidade <= 0.4
    - Usa múltiplos nós iniciais para cada componente (multi-start).
    - Aplica refinamento local ao final.

    Racional:
    - A abordagem por componente melhora a escalabilidade.
    - A escolha BFS/DFS adaptativa melhora a qualidade da solução.
    - O log é construído por padrão individual (1 linha por padrão) para
      facilitar análise e visualização em CSV.
    """
    sequencia_final = []
    log_execucao = []

    for componente in nx.connected_components(grafo):
        if not componente:
            continue

        subgrafo = grafo.subgraph(componente)
        tamanho = len(componente)
        densidade = nx.density(subgrafo)

        # Caso trivial: componente com 1 nó
        if tamanho == 1:
            no = next(iter(componente))
            sequencia_final.append(no)
            log_execucao.append({
                "Padrao": [no],
                "Busca": "Trivial",
                "DensidadeRegiao": densidade,
                "NMPA_Parcial": calcular_nmpa(sequencia_final, matPaPe)
            })
            continue

        # Caso pequeno: ordenação rápida
        elif tamanho <= 5:
            seq = ordenacao_rapida(subgrafo, matPaPe)
            sequencia_final.extend(seq)
            log_execucao.append({
                "Padrao": seq,
                "Busca": "Ordenacao_Rapida",
                "DensidadeRegiao": densidade,
                "NMPA_Parcial": calcular_nmpa(sequencia_final, matPaPe)
            })
            continue

        # Multi-start: testa vários nós iniciais
        nos_iniciais = melhores_nos_iniciais(subgrafo, matPaPe, top_k=3)
        melhores_seqs = []

        for no_inicial in nos_iniciais:
            if densidade > 0.4:
                seq = bfs_adaptado(subgrafo, no_inicial, matPaPe)
                tipo_busca = "BFS"
            else:
                seq = dfs_adaptado(subgrafo, no_inicial, matPaPe)
                tipo_busca = "DFS"

            nmpa_seq = calcular_nmpa(sequencia_final + seq, matPaPe)
            melhores_seqs.append((nmpa_seq, seq, tipo_busca))

        # Seleciona a melhor sequência entre as 3 testadas
        melhores_seqs.sort(key=lambda x: x[0])
        melhor_nmpa, melhor_seq, tipo_busca = melhores_seqs[0]

        # Adiciona a sequência à final
        sequencia_final.extend(melhor_seq)

        # Log linha a linha (um padrão por linha no CSV)
        for padrao in melhor_seq:
            log_execucao.append({
                "Padrao": padrao,
                "Busca": tipo_busca,
                "DensidadeRegiao": densidade,
                "NMPA_Parcial": melhor_nmpa
            })

    # Aplica refinamento final na sequência montada
    return refinamento_minimo(sequencia_final, matPaPe, modo="padrao"), log_execucao