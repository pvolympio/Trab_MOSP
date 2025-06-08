"""
Arquivo para testar uma única instância do problema MOSP.

Fluxo:
    - Lê uma instância específica
    - Constrói o grafo padrão-padrão
    - Aplica a heurística híbrida
    - Calcula o NMPA
    - Exibe os resultados no console

Como rodar:
    python main.py
"""

from mosp.leitura_instancia import criar_matriz_padroes_pecas
from mosp.grafo import construir_grafo
from mosp.custo_nmpa import calcular_nmpa
from mosp.heuristicas import heuristica_hibrida_adaptativa

def main():
    # Nome da instância (sem .txt)
    nome_instancia = "Cenario_3-1-exemplo"
    caminho_instancia = f"cenarios/{nome_instancia}.txt"

    # 1. Ler a matriz padrão × peça
    matriz = criar_matriz_padroes_pecas(caminho_instancia)

    # 2. Construir o grafo padrão-padrão
    grafo = construir_grafo(matriz)

    # 3. Aplicar heurística híbrida
    ordem = heuristica_hibrida_adaptativa(grafo)

    # 4. Calcular NMPA
    nmpa = calcular_nmpa(ordem, matriz)

    # 5. Exibir resultados
    print("-" * 50)
    print(f"Instância: {nome_instancia}")
    print(f"Ordem gerada pela heurística híbrida: {ordem}")
    print(f"NMPA (Número Máximo de Pilhas Abertas): {nmpa}")
    print("-" * 50)

if __name__ == "__main__":
    main()