"""
Este arquivo contém as funções responsáveis pelos refinamentos aplicados sobre as ordens de produção geradas inicialmente pelas heurísticas.

Descrição:
    - Os refinamentos buscam reduzir o número máximo de pilhas abertas (NMPA) através de permutações locais e globais na sequência.
    - As estratégias atuam sobre a sequência completa ou em regiões críticas identificadas (hotspots).
    - São aplicados como etapas posteriores às heurísticas principais.

Contexto:
    - No problema MOSP, o refinamento permite melhorar soluções heurísticas iniciais, tentando reduzir ainda mais o NMPA.

Funções disponíveis:
    - refinamento_diferenciado(sequencia, matPaPe, n_iter=5)
    - refinamento_hotspots(sequencia, matPaPe, janela=5)
    - refinamento_hibrido(sequencia, matPaPe)

Exemplo de uso:
    from mosp.refinamento import refinamento_hibrido
    sequencia_final = refinamento_hibrido(sequencia_inicial, matriz_padroes_pecas)
"""

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