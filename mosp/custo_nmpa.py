

import numpy as np

def calcular_nmpa(ordering, matriz):

    if len(ordering) > 1:
        # Seleciona as linhas da matriz na ordem desejada
        matriz_ordenada = matriz[ordering, :]

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
