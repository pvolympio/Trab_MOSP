# -*- coding: utf-8 -*-

"""
Este arquivo realiza um teste de sensibilidade para o limiar de densidade das heurísticas adaptativas no problema MOSP.

Motivação:
    - As heurísticas 'heuristica_hibrida_adaptativa' e 'heuristica_comunidades_adaptativa' utilizam um parâmetro 'limiar_densidade' para decidir quando aplicar BFS ou DFS.
    - Este teste explora diferentes valores de limiar para analisar como o NMPA varia.
    - O objetivo é identificar o limiar de densidade que gera as melhores ordens (menor NMPA).

Fluxo:
    - Lê cada instância da pasta "cenarios/"
    - Para cada valor de limiar definido:
        - Aplica 'heuristica_hibrida_adaptativa'
        - Aplica 'heuristica_comunidades_adaptativa'
        - Calcula o NMPA de cada ordem
    - Armazena os resultados em um CSV separado: "resultados/teste_limiar_densidade.csv"

Como rodar:
    python teste_limiar_densidade.py

Notas:
    - Este teste é exploratório. Os resultados NÃO devem ser misturados com o benchmark final.
    - Após rodar este teste, o usuário pode escolher o limiar de densidade ótimo para uso no benchmark.py.
"""

import os
import csv
import pandas as pd

from mosp.leitura_instancia import criar_matriz_padroes_pecas
from mosp.grafo import construir_grafo
from mosp.custo_nmpa import calcular_nmpa
from mosp.heuristicas import heuristica_hibrida_adaptativa, heuristica_comunidades_adaptativa

def teste_limiar_densidade(pasta_instancias, limiares, caminho_saida_csv):
    """
    Executa o teste de sensibilidade para o limiar de densidade.

    Args:
        pasta_instancias: Caminho da pasta onde estão os arquivos .txt das instâncias.
        limiares: Lista de valores de limiar de densidade a serem testados.
        caminho_saida_csv: Caminho do arquivo CSV de saída.
    """
    resultados = []

    for limiar in limiares:
        print(f"\nTestando limiar de densidade = {limiar}")

        for arquivo in os.listdir(pasta_instancias):
            if arquivo.endswith(".txt"):
                nome_instancia = arquivo.replace(".txt", "")
                caminho_instancia = os.path.join(pasta_instancias, arquivo)

                print(f"    Processando instância: {nome_instancia}")

                # 1. Ler a matriz padrão × peça
                matriz = criar_matriz_padroes_pecas(caminho_instancia)

                # 2. Construir o grafo padrão-padrão
                grafo = construir_grafo(matriz)

                # 3. Aplicar heurísticas adaptativas com o limiar atual
                ordem_hibrida, _ = heuristica_hibrida_adaptativa(grafo, limiar_densidade=limiar)
                ordem_comunidades, _ = heuristica_comunidades_adaptativa(grafo, limiar_densidade=limiar)

                # 4. Calcular NMPA
                nmpa_hibrida = calcular_nmpa(ordem_hibrida, matriz)
                nmpa_comunidades = calcular_nmpa(ordem_comunidades, matriz)

                # 5. Armazenar resultado
                resultados.append({
                    "Instancia": nome_instancia,
                    "Limiar_Densidade": limiar,
                    "NMPA_Hibrida": nmpa_hibrida,
                    "NMPA_Comunidades": nmpa_comunidades
                })

    # 6. Escrever resultados no CSV
    os.makedirs(os.path.dirname(caminho_saida_csv), exist_ok=True)
    with open(caminho_saida_csv, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Instancia", "Limiar_Densidade", "NMPA_Hibrida", "NMPA_Comunidades"
        ])
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\nTeste de limiar de densidade finalizado.")
    print(f"Resultados salvos em: {caminho_saida_csv}")

if __name__ == "__main__":
    # Lista de limiares que serão testados
    lista_limiares = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    teste_limiar_densidade(
        pasta_instancias="cenarios",
        limiares=lista_limiares,
        caminho_saida_csv="resultados/teste_limiar_densidade.csv"
    )