def BFS(listaAdj, v):
    q = []
    resultado = []
    q.append(v)
    while(len(q) != 0):
        v = q.pop(0)
        for i in listaAdj[v]:
            if (i not in q) & (i not in resultado):
                q.append(i)
        resultado.append(v)
    for j in listaAdj:
        if j not in resultado:
            resultado.append(j)
    return resultado