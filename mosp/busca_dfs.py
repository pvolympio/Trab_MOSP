"""
Este arquivo contém a função de Busca em Profundidade (DFS) para percorrer o grafo padrão-padrão.

Descrição:
    - Dada uma lista de adjacência e um vértice inicial, a função gera uma ordem de visitação dos padrões (vértices) utilizando o algoritmo DFS (versão iterativa).
    - A função inclui um mecanismo para garantir que todos os padrões sejam incluídos na ordem final, mesmo que o grafo tenha componentes desconexas (caso existam padrões que não compartilham peças com nenhum outro padrão). Isso é necessário porque o MOSP exige que todos os padrões sejam produzidos.
    - Além disso, a função foi ajustada para ser totalmente compatível com subgrafos (por exemplo, nas comunidades detectadas por 'heuristica_comunidades_adaptativa'), em que os vértices podem não ser numerados de 0 a N-1.

Uso no projeto:
    - A DFS gera uma ordem de produção inicial que será avaliada com a função de custo (NMPA).
    - Essa ordem é usada no benchmark para comparar diferentes estratégias de busca.

Função disponível:
    - dfs(lista_adjacencia, vertice_inicial)

Exemplo de uso:
    from mosp.busca_dfs import dfs
    ordem = dfs(lista_adjacencia, vertice_inicial)
"""
import numpy as np

def dfs(lista_adjacencia, vertice_inicial):
    """
    Executa a Busca em Profundidade (DFS) no grafo padrão-padrão ou subgrafo.

    Compatível com subgrafos (ex: comunidades detectadas).

    Args:
        lista_adjacencia: Dicionário {vértice: lista de vizinhos}.
        vertice_inicial: Índice do vértice de início da busca.

    Returns:
        ordem: Lista de padrões (vértices) na ordem em que foram visitados pela DFS.
               Se o grafo tiver componentes desconexas, os padrões isolados ou de outras componentes
               serão adicionados ao final da ordem.
    """
    # Correção: pegar os vértices reais, não um range de 0 até N-1
    todos_vertices = list(lista_adjacencia.keys())

    visitados = []
    pilha = [vertice_inicial]

    # Enquanto ainda houver vértices não visitados
    while todos_vertices:
        # Enquanto a pilha não estiver vazia
        while pilha:
            vertice_atual = pilha[0]

            if vertice_atual not in visitados:
                visitados.append(vertice_atual)

            # Encontra os vizinhos que ainda não foram visitados
            vizinhos_nao_visitados = list(set(lista_adjacencia[vertice_atual]) - set(visitados))
            vizinhos_nao_visitados.sort()

            if vizinhos_nao_visitados:
                pilha.insert(0, vizinhos_nao_visitados[0])
            else:
                pilha.pop(0)

        # Após terminar um componente, atualiza a lista de vértices não visitados
        todos_vertices = list(set(todos_vertices) - set(visitados))

        # Se ainda houver vértices não visitados, começa nova DFS por outro componente
        if todos_vertices:
            pilha = [todos_vertices[0]]

    return visitados

def dfs_limitado(subgrafo, no_inicial, visitados, matPaPe, limite=2):
    """
    Executa uma busca em profundidade (DFS) com profundidade máxima controlada,
    priorizando a visita de vizinhos mais similares (com mais peças em comum).

    Args:
        subgrafo: componente do grafo principal (NetworkX Graph).
        no_inicial: vértice de partida.
        visitados: conjunto compartilhado para marcar nós visitados globalmente.
        matPaPe: matriz padrão x peça.
        limite: profundidade máxima permitida.

    Returns:
        Sequência de visita DFS (lista de padrões).
    """
    pilha = [(no_inicial, 0)]  # Pilha DFS, com tuplas (nó, profundidade atual)
    sequencia = []

    while pilha:
        no_atual, profundidade = pilha.pop()  # Retira o último da pilha (LIFO)

        if no_atual not in visitados:
            visitados.add(no_atual)  # Marca como visitado
            sequencia.append(no_atual)  # Adiciona à sequência

            if profundidade < limite:
                # Ordena os vizinhos por similaridade de peças, priorizando os mais parecidos
                vizinhos = sorted(subgrafo.neighbors(no_atual),
                                  key=lambda x: np.sum(matPaPe[no_atual] & matPaPe[x]),
                                  reverse=True)
                # Adiciona à pilha (reverso para manter ordem original de prioridade)
                pilha.extend((v, profundidade + 1) for v in reversed(vizinhos) if v not in visitados)

    return sequencia
