"""
Este arquivo contém a função de Busca em Profundidade (DFS) para percorrer o grafo padrão-padrão.

Descrição:
    - Dada uma lista de adjacência e um vértice inicial, a função gera uma ordem de visitação dos padrões (vértices) utilizando o algoritmo DFS (versão iterativa).
    - A função inclui um mecanismo para garantir que todos os padrões sejam incluídos na ordem final, mesmo que o grafo tenha componentes desconexas (caso existam padrões que não compartilham peças com nenhum outro padrão). Isso é necessário porque o MOSP exige que todos os padrões sejam produzidos.

Uso no projeto:
    - A DFS gera uma ordem de produção inicial que será avaliada com a função de custo (NMPA).
    - Essa ordem é usada no benchmark para comparar diferentes estratégias de busca.

Função disponível:
    - dfs(lista_adjacencia, vertice_inicial)

Exemplo de uso:
    from mosp.busca_dfs import dfs
    ordem = dfs(lista_adjacencia, vertice_inicial)
"""

def dfs(lista_adjacencia, vertice_inicial):
    """
    Executa a Busca em Profundidade (DFS) no grafo padrão-padrão.

    Args:
        lista_adjacencia: Dicionário {vértice: lista de vizinhos}.
        vertice_inicial: Índice do vértice de início da busca.

    Returns:
        ordem: Lista de padrões (vértices) na ordem em que foram visitados pela DFS.
               Se o grafo tiver componentes desconexas, os padrões isolados ou de outras componentes
               serão adicionados ao final da ordem.
    """
    num_vertices = len(lista_adjacencia)
    todos_vertices = list(range(num_vertices))
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