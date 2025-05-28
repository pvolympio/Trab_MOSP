def DeepFirstSearch(sequencia, listaAdj, v):
    sequencia.append(v)
    adjacente = listaAdj[v]
    for adj in adjacente:
        if adj not in sequencia:
            DeepFirstSearch(sequencia, listaAdj, adj)

def DFSIterativa(listaAdj, v):
    seq = []
    DeepFirstSearch(seq, listaAdj, v)
    return seq

def DFS(listaAdj, v):
    numVertices = len(listaAdj)                   
    todosVertices = list(range(numVertices))       
    visitados = []                                      
    pilha = [v]                            

    # Enquanto ainda houver vértices não visitados
    while todosVertices:
        # Enquanto a pilha não estiver vazia
        while pilha:
            atual = pilha[0]                            

            if atual not in visitados:
                visitados.append(atual)                  

            # Encontra os vizinhos que ainda não foram visitados
            vizinhosNaoVisitados = list(set(listaAdj[atual]) - set(visitados))
            vizinhosNaoVisitados.sort()                  

            if vizinhosNaoVisitados:
                pilha.insert(0, vizinhosNaoVisitados[0]) 
            else:
                pilha.pop(0)                           

        # Após terminar um componente, atualiza a lista de vértices não visitados
        todosVertices = list(set(todosVertices) - set(visitados))

        # Se ainda houver vértices não visitados, começa nova DFS por outro componente
        if todosVertices:
            pilha = [todosVertices[0]]

    return visitados