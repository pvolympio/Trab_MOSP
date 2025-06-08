"""
Este arquivo contém a função de Busca em Largura (BFS) para percorrer o grafo padrão-padrão.

Descrição:
    - Dada uma lista de adjacência e um vértice inicial, a função gera uma ordem de visitação dos padrões (vértices) utilizando o algoritmo BFS.
    - A função inclui um mecanismo para garantir que todos os padrões sejam incluídos na ordem final, mesmo que o grafo tenha componentes desconexas (caso existam padrões que não compartilham peças com nenhum outro padrão). Isso é necessário porque o MOSP exige que todos os padrões sejam produzidos.

Uso no projeto:
    - A BFS gera uma ordem de produção inicial que será avaliada com a função de custo (NMPA).
    - Essa ordem é usada no benchmark para comparar diferentes estratégias de busca.

Função disponível:
    - bfs(lista_adjacencia, vertice_inicial)

Exemplo de uso:
    from mosp.busca_bfs import bfs
    ordem = bfs(lista_adjacencia, vertice_inicial)
"""

def bfs(lista_adjacencia, vertice_inicial):
    """
    Executa a Busca em Largura (BFS) no grafo padrão-padrão.

    Args:
        lista_adjacencia: Dicionário {vértice: lista de vizinhos}.
        vertice_inicial: Índice do vértice de início da busca.

    Returns:
        ordem: Lista de padrões (vértices) na ordem em que foram visitados pela BFS.
    """
    fila = []
    ordem = []

    fila.append(vertice_inicial)

    while len(fila) != 0:
        vertice_atual = fila.pop(0)

        for vizinho in lista_adjacencia[vertice_atual]:
            if (vizinho not in fila) and (vizinho not in ordem):
                fila.append(vizinho)

        ordem.append(vertice_atual)

    # Garante que todos os vértices sejam incluídos (caso o grafo tenha componentes desconexas - padrão que não compartilha peça com nenhum outro padrão)
    for vertice in lista_adjacencia:
        if vertice not in ordem:
            ordem.append(vertice)

    return ordem
