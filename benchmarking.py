import os
import csv
from DFS import DFS
from BFS import BFS
from calculoPilhas import criaMatPadraoPeca, NMPA, construir_grafo,heuristica_hibrida_adaptativa, aleatoria

def executar_benchmark(pasta_instancias, caminho_saida_csv):
    resultados = []

    for arquivo in os.listdir(pasta_instancias):
        if arquivo.endswith(".txt"):
            nome = arquivo.replace(".txt", "")
            print(f">>> Processando: {nome}")

            mat = criaMatPadraoPeca(os.path.join(pasta_instancias, nome))
            G = construir_grafo(mat)

            LP_bfs = BFS(G,0)
            LP_dfs = DFS(G,0)
            LP_hibrida = heuristica_hibrida_adaptativa(G)
            LP_random = aleatoria(G)

            resultados.append({
                "Instancia": nome,
                "NMPA_BFS": NMPA(LP_bfs, mat),
                "NMPA_DFS": NMPA(LP_dfs, mat),
                "NMPA_Hibrida": NMPA(LP_hibrida, mat),
                "NMPA_Random": NMPA(LP_random, mat)
            })

    # Escrever o CSV
    os.makedirs(os.path.dirname(caminho_saida_csv), exist_ok=True)
    with open(caminho_saida_csv, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Instancia", "NMPA_BFS", "NMPA_DFS", "NMPA_Hibrida", "NMPA_Random"])
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\n✅ Benchmark finalizado! Resultados salvos em: {caminho_saida_csv}")


executar_benchmark(
    pasta_instancias="cenarios",
    caminho_saida_csv="resultados/benchmark_mosp.csv")