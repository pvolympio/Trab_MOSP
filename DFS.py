import numpy as np




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

# ------------------------------
# DFS com profundidade limitada e ordenação dos vizinhos por similaridade
# ------------------------------
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
