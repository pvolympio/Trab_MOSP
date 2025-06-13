import networkx as nx
import numpy as np
from .custo_nmpa import calcular_nmpa
import itertools
def refinamento_minimo(sequencia, matPaPe,modo):
    
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
    """Ordenação otimizada para pequenos componentes"""
    nos = list(subgrafo.nodes())
    if len(nos) <= 1:
        return nos

    nos.sort(key=lambda x: -subgrafo.degree(x))
    primeiro = nos[0]
    similares = [(x, np.sum(matPaPe[primeiro] & matPaPe[x])) for x in nos[1:]]
    nos[1:] = [x for x, _ in sorted(similares, key=lambda par: -par[1])]

    return nos

def melhores_nos_iniciais(subgrafo: nx.Graph, matPaPe: np.ndarray, top_k: int = 3):
    """Retorna os top-k melhores nós iniciais com base em grau e similaridade"""
    ranking = sorted(
        subgrafo.nodes,
        key=lambda no: (
            0.6 * subgrafo.degree(no) +
            0.4 * np.sum(matPaPe[no] > 0)
        ),
        reverse=True
    )
    return ranking[:top_k]
