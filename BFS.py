def BFS(G, v_inicial):
    from collections import deque

    visitados = set([v_inicial])
    fila = deque([v_inicial])
    resultado = []

    while fila:
        atual = fila.popleft()
        resultado.append(atual)

        for vizinho in sorted(G.neighbors(atual)):
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append(vizinho)

    return resultado
