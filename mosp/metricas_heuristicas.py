import networkx as nx
import numpy as np
from .custo_nmpa import calcular_nmpa
import itertools
def refinamento_minimo(sequencia, matPaPe, modo = "padrao"):
    """
    Refinamento leve que tenta melhorar a sequência sem piorar o NMPA.

    Estratégia:
    - Testa se inverter a sequência melhora o NMPA.
    - Em seguida, tenta fazer trocas locais entre pares vizinhos.

    Racional:
    - Refinamentos simples ajudam a corrigir falhas das heurísticas,
      sem custo computacional elevado.
    """
    if len(sequencia) <= 3:
        return sequencia

    nmpa_original = calcular_nmpa(sequencia, matPaPe)
    sequencia_invertida = sequencia[::-1]
    nmpa_invertido = calcular_nmpa(sequencia_invertida, matPaPe)

    if nmpa_invertido < nmpa_original:
        return sequencia_invertida

    melhor_seq = sequencia.copy()
    melhor_nmpa = nmpa_original

    for i in range(len(sequencia) - 1):
        nova_seq = melhor_seq.copy()
        nova_seq[i], nova_seq[i + 1] = nova_seq[i + 1], nova_seq[i]
        novo_nmpa = calcular_nmpa(nova_seq, matPaPe)

        if novo_nmpa < melhor_nmpa:
            melhor_seq, melhor_nmpa = nova_seq, novo_nmpa

    return melhor_seq
def ordenacao_rapida(subgrafo, matPaPe):
    """
    Ordenação otimizada para pequenos componentes.

    Estratégia:
    - Ordena os nós com base no grau (nós mais conectados primeiro).
    - Depois, ordena os nós restantes por similaridade com o primeiro nó.
      A similaridade aqui é calculada como a interseção entre os vetores de peça.

    Racional:
    - Para grafos pequenos (<= 5 nós), é mais rápido aplicar uma heurística leve
      baseada em conectividade e semelhança de peças, sem usar BFS/DFS.
    """
    nos = list(subgrafo.nodes())
    if len(nos) <= 1:
        return nos

    # Ordena por grau (prioriza nós com mais conexões)
    nos.sort(key=lambda x: -subgrafo.degree(x))
    primeiro = nos[0]

    # Ordena os restantes por similaridade com o primeiro
    similares = [(x, np.sum(matPaPe[primeiro] & matPaPe[x])) for x in nos[1:]]
    nos[1:] = [x for x, _ in sorted(similares, key=lambda par: -par[1])]

    return nos

def melhores_nos_iniciais(subgrafo, matPaPe, top_k = 3):
    """
    Retorna os top-k melhores nós iniciais.

    Estratégia:
    - Classifica os nós por grau e similaridade, e pega os top_k melhores.

    Racional:
    - Permite aplicar a heurística Multi-Start (vários pontos de partida),
      aumentando a chance de encontrar uma boa sequência final.
    """
    ranking = sorted(
        subgrafo.nodes,
        key=lambda no: (
            0.6 * subgrafo.degree(no) +
            0.4 * np.sum(matPaPe[no] > 0)
        ),
        reverse=True
    )
    return ranking[:top_k]