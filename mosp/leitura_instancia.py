"""
Este arquivo contém a função para leitura de instâncias do problema MOSP (Minimização de Pilhas Abertas).

Função:
    - criar_matriz_padroes_pecas(caminho_txt)

Descrição:
    - Lê um arquivo .txt que representa a matriz padrão x peça da instância.
    - A primeira linha do arquivo contém dois inteiros: número de padrões (linhas) e número de peças (colunas).
    - As linhas seguintes contêm a matriz binária:
        - Cada linha representa um padrão.
        - Cada coluna representa uma peça.
        - Valor 1 indica que o padrão utiliza a peça correspondente.

Exemplo de uso:
    from mosp.leitura_instancia import criar_matriz_padroes_pecas
    matriz = criar_matriz_padroes_pecas("cenarios/Cenario_1.txt")
"""

import numpy as np

def criar_matriz_padroes_pecas(caminho_txt):
    """
    Lê um arquivo de instância do MOSP e retorna a matriz padrão x peça.

    Args:
        caminho_txt: Caminho completo para o arquivo .txt da instância.

    Returns:
        matriz: Matriz binária (n_padroes x n_pecas), onde:
                - Cada linha representa um padrão.
                - Cada coluna representa uma peça.
                - Valor 1 indica que o padrão utiliza a peça.
    """
    with open(caminho_txt, 'rb') as arquivo:
        num_padroes, num_pecas = [int(valor) for valor in arquivo.readline().split()]
        matriz = np.genfromtxt(arquivo, dtype="int32", max_rows=num_padroes)
    
    return matriz
