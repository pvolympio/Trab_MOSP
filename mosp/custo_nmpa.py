"""
Este arquivo contém a função para cálculo do NMPA (Número Máximo de Pilhas Abertas) de uma ordem de produção.

Descrição:
    - Dada uma ordem de produção (sequência de padrões) e a matriz padrão x peça, a função calcula quantas pilhas (peças) ficam abertas em cada etapa da produção.
    - O NMPA é o valor máximo dessas pilhas abertas ao longo da produção.

Contexto:
    - No problema MOSP, queremos encontrar uma ordem de produção que minimize o NMPA.

Função disponível:
    - calcular_nmpa(ordering, matriz_padroes_pecas)

Exemplo de uso:
    from mosp.custo_nmpa import calcular_nmpa
    nmpa = calcular_nmpa(ordering, matriz_padroes_pecas)
"""

import numpy as np

def calcular_nmpa(ordering, matriz_padroes_pecas):
    """
    Calcula o NMPA (Número Máximo de Pilhas Abertas) para uma ordem de produção.

    Args:
        ordering: Lista de índices de padrões (ordem em que os padrões serão produzidos).
                  Exemplo: [2, 0, 1]
        matriz_padroes_pecas: Matriz binária (n_padroes x n_pecas), onde:
                              - Cada linha representa um padrão.
                              - Cada coluna representa uma peça.
                              - Valor 1 indica que o padrão utiliza a peça.

    Returns:
        nmpa: Número máximo de pilhas abertas durante a produção.
    """
    if len(ordering) > 1:
        # Seleciona as linhas da matriz na ordem desejada
        matriz_ordenada = matriz_padroes_pecas[ordering, :]

        # Calcula o "acúmulo para frente" e "acúmulo para trás" para cada peça
        acumulado_frente = np.maximum.accumulate(matriz_ordenada, axis=0)
        acumulado_tras = np.maximum.accumulate(matriz_ordenada[::-1, :], axis=0)[::-1, :]

        # Uma pilha está aberta se a peça já foi usada e ainda será usada
        pilhas_abertas = acumulado_frente & acumulado_tras

        # Conta quantas pilhas abertas existem em cada etapa
        pilhas_abertas_por_etapa = np.sum(pilhas_abertas, axis=1)
    else:
        # Caso trivial: apenas um padrão na ordem
        matriz_ordenada = matriz_padroes_pecas[ordering, :]
        pilhas_abertas_por_etapa = [np.sum(matriz_ordenada)]

    # Retorna o número máximo de pilhas abertas ao longo da produção
    nmpa = np.amax(pilhas_abertas_por_etapa)
    return nmpa
