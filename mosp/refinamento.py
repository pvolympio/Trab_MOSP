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

def refinamento_diferenciado(sequencia, matPaPe, n_iter=5):
    """
    Refinamento global com trocas locais e permutações parciais para tentar reduzir o NMPA.

    Parâmetros:
        sequencia (list): ordem inicial de padrões.
        matPaPe (np.ndarray): matriz padrão x peça.
        n_iter (int): número de iterações de refinamento.

    Retorno:
        list: nova sequência refinada.
    """
    melhor_seq = sequencia.copy()
    melhor_nmpa = calcular_nmpa(sequencia, matPaPe)

    for _ in range(n_iter):
        for i in range(len(sequencia) - 1):
            nova_seq = sequencia.copy()
            nova_seq[i], nova_seq[i + 1] = nova_seq[i + 1], nova_seq[i]
            novo_nmpa = calcular_nmpa(nova_seq, matPaPe)

            if novo_nmpa < melhor_nmpa:
                melhor_seq, melhor_nmpa = nova_seq, novo_nmpa

            if i < len(sequencia) - 3:
                for j in range(i + 2, min(i + 5, len(sequencia))):
                    nova_seq = sequencia.copy()
                    nova_seq[i], nova_seq[j] = nova_seq[j], nova_seq[i]
                    novo_nmpa = calcular_nmpa(nova_seq, matPaPe)

                    if novo_nmpa < melhor_nmpa:
                        melhor_seq, melhor_nmpa = nova_seq, novo_nmpa

        sequencia = melhor_seq.copy()

    return melhor_seq

def refinamento_hotspots(sequencia, matPaPe, janela=5):
    """
    Refinamento local em regiões (hotspots) de maior concentração de pilhas abertas.

    Parâmetros:
        sequencia (list): ordem inicial de padrões.
        matPaPe (np.ndarray): matriz padrão x peça.
        janela (int): tamanho da região analisada.

    Retorno:
        list: nova sequência refinada.
    """
    max_pilhas = 0
    pior_inicio = 0
    for i in range(len(sequencia) - janela + 1):
        nmpa_local = calcular_nmpa(sequencia[i:i + janela], matPaPe)
        if nmpa_local > max_pilhas:
            max_pilhas = nmpa_local
            pior_inicio = i

    bloco = sequencia[pior_inicio:pior_inicio + janela]
    melhor_bloco = bloco.copy()
    melhor_nmpa = max_pilhas

    for perm in itertools.permutations(bloco):
        nova_sequencia = sequencia[:pior_inicio] + list(perm) + sequencia[pior_inicio + janela:]
        novo_nmpa = calcular_nmpa(nova_sequencia, matPaPe)
        if novo_nmpa < melhor_nmpa:
            melhor_bloco = perm
            melhor_nmpa = novo_nmpa

    return sequencia[:pior_inicio] + list(melhor_bloco) + sequencia[pior_inicio + janela:]

def refinamento_hibrido(sequencia, matPaPe):
    """
    Aplica o refinamento diferenciado e, caso necessário, o refinamento por hotspots.

    Parâmetros:
        sequencia (list): ordem inicial de padrões.
        matPaPe (np.ndarray): matriz padrão x peça.

    Retorno:
        list: sequência refinada final.
    """
    seq = refinamento_diferenciado(sequencia, matPaPe, n_iter=3)
    if len(seq) > 10:
        seq = refinamento_hotspots(seq, matPaPe)
    return seq