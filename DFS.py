def dfs_completo(G):
    visitados = set()
    resultado = []

    for v in G.nodes():
        if v not in visitados:
            pilha = [v]
            while pilha:
                atual = pilha.pop()
                if atual not in visitados:
                    visitados.add(atual)
                    resultado.append(atual)
                    vizinhos = sorted([u for u in G.neighbors(atual) if u not in visitados], reverse=True)
                    pilha.extend(vizinhos)
    return resultado


def DFS(G, v_inicial):
    visitados = set()
    pilha = [v_inicial]
    resultado = []

    while pilha:
        atual = pilha.pop()
        if atual not in visitados:
            visitados.add(atual)
            resultado.append(atual)
            vizinhos = sorted([v for v in G.neighbors(atual) if v not in visitados], reverse=True)
            pilha.extend(vizinhos)

    return resultado
