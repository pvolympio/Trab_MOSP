"""
Este arquivo contém as heurísticas utilizadas para gerar ordens de produção no problema MOSP.

Descrição:
    - Diferente das buscas clássicas (BFS, DFS), estas heurísticas aplicam estratégias adaptativas ou aleatórias para gerar uma ordem de produção.
    - A heurística híbrida decide dinamicamente entre usar BFS ou DFS em cada componente do grafo, com base na densidade do componente.
    - A heurística de comunidades identifica regiões densas no grafo (comunidades) e decide dinamicamente entre BFS ou DFS em cada uma.
    - A heurística aleatória simplesmente gera uma ordem aleatória dos padrões (baseline para comparação).

Uso no projeto:
    - As heurísticas geram ordens de produção que serão avaliadas com a função de custo (NMPA).
    - Essas ordens são usadas no benchmark para comparar diferentes estratégias.

Funções disponíveis:
    - heuristica_hibrida_adaptativa(grafo, limiar_densidade=0.3)
    - heuristica_comunidades_adaptativa(grafo, limiar_densidade=0.3)
    - aleatoria(grafo)

Exemplo de uso:
    from mosp.heuristicas import heuristica_hibrida_adaptativa, aleatoria

    ordem_hibrida = heuristica_hibrida_adaptativa(grafo)
    ordem_comunidades = heuristica_comunidades_adaptativa(grafo)
    ordem_aleatoria = aleatoria(grafo)
"""

import networkx as nx
import random
import numpy as np
from mosp.busca_bfs import bfs, bfs_adaptado
from mosp.busca_dfs import dfs,dfs_adaptado
from mosp.metricas_heuristicas import ordenacao_rapida, refinamento_minimo, melhores_nos_iniciais
from mosp.custo_nmpa import calcular_nmpa
from networkx.algorithms.community import greedy_modularity_communities

def heuristica_hibrida_adaptativa(grafo, limiar_densidade=0.3):
    """
    Gera uma ordem de produção utilizando a heurística híbrida adaptativa.

    - Baseia-se na densidade de cada **componente conectado** do grafo.
    - Em cada componente:
        - Se densidade >= limiar → aplica BFS.
        - Caso contrário → aplica DFS.
    - Se o grafo for todo conectado (1 componente), aplica-se a heurística ao grafo inteiro.

    Diferença em relação à heurística de comunidades:
        - Aqui a decisão é por componente (definido topologicamente — conjuntos conectados).
        - A heurística de comunidades detecta subgrupos densos dentro de componentes.

    Args:
        grafo: Objeto nx.Graph (grafo padrão-padrão).
        limiar_densidade: Limite para decidir entre BFS e DFS.

    Returns:
        ordem_final: Lista de padrões (vértices).
        log_execucao: Lista de dicionários com log da busca em cada padrão.
    """
    visitados = set()
    ordem_final = []
    log_execucao = []

    # Começa pelo vértice de maior grau
    vertice_inicial = max(grafo.degree, key=lambda x: x[1])[0]

    # Primeiro componente
    componente_inicial = nx.node_connected_component(grafo, vertice_inicial)
    subgrafo_inicial = grafo.subgraph(componente_inicial)

    lista_adjacencia = {v: list(subgrafo_inicial.neighbors(v)) for v in subgrafo_inicial.nodes()}
    ordem = bfs(lista_adjacencia, vertice_inicial)

    for padrao in ordem:
        log_execucao.append({
            "Padrao": padrao,
            "Busca": "BFS",
            "DensidadeRegiao": nx.density(subgrafo_inicial)
        })

    ordem_final.extend(ordem)
    visitados.update(ordem)

    # Demais componentes
    for componente in nx.connected_components(grafo):
        componentes_nao_visitados = [v for v in componente if v not in visitados]
        if not componentes_nao_visitados:
            continue

        subgrafo = grafo.subgraph(componentes_nao_visitados)
        densidade = nx.density(subgrafo)
        vertice_inicio = componentes_nao_visitados[0]

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

    return ordem_final, log_execucao

def heuristica_comunidades_adaptativa(grafo, limiar_densidade=0.3):
    """
    Gera uma ordem de produção utilizando comunidades (regiões densas).

    - Detecta comunidades internas com mais conexões internas do que externas.
    - Em cada comunidade:
        - Se densidade >= limiar → aplica BFS.
        - Caso contrário → aplica DFS.

    Diferença em relação à heurística de componentes:
        - Aqui a "região" é uma comunidade detectada automaticamente (pode estar dentro de um componente).
        - Comunidades podem sobrepor ou dividir um componente grande em várias regiões.

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
        vertice_inicio = next(iter(comunidade))  # Pega um vértice qualquer da comunidade

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

    - Motivação:
        - Observou-se que as heurísticas que aplicavam BFS desde o início (baseadas apenas na densidade do grafo) geravam ordens com NMPA muito semelhantes ao BFS puro.
        - A proposta aqui é explorar uma abordagem mais dinâmica:
            - Começar aplicando DFS, que tende a abrir mais pilhas no início.
            - Monitorar a evolução do NMPA em tempo real.
            - Quando o NMPA atingir seu pico (ou uma janela de pico), mudar a estratégia para BFS, tentando reduzir o número de pilhas abertas de forma mais eficaz.

    - Diferenças em relação às heurísticas anteriores:
        - Enquanto 'heuristica_hibrida_adaptativa' e 'heuristica_comunidades_adaptativa' tomam a decisão BFS/DFS com base em densidade de região, esta heurística adapta a estratégia dinamicamente com base no estado atual do NMPA.
        - A matriz padrão-peça é necessária aqui, pois o cálculo do NMPA em tempo real depende dela.

    Args:
        grafo: Objeto nx.Graph (grafo padrão-padrão).
        matriz: Matriz padrão-peça (necessária para cálculo do NMPA).
        limiar_densidade: (opcional) ainda pode ser usado para decidir BFS/DFS antes do pico.

    Returns:
        ordem_final: Lista de padrões (vértices) na ordem gerada.
        log_execucao: Lista de dicionários com log detalhado da busca em cada passo (padrão, busca, NMPA parcial).
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