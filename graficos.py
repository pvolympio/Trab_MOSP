import pandas as pd
import matplotlib.pyplot as plt
import os

def gerar_grafico_barras(csv_path, salvar_em="resultados/grafico_barras.png"):
    df = pd.read_csv(csv_path, encoding='latin1')  # <-- correção aqui
    df.set_index("Instancia", inplace=True)

    ax = df.plot(kind="bar", figsize=(12, 6), colormap="Set2")
    plt.title("Comparação de NMPA por Heurística")
    plt.ylabel("Número Máximo de Pilhas Abertas (NMPA)")
    plt.xlabel("Instância")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()

    os.makedirs(os.path.dirname(salvar_em), exist_ok=True)
    plt.savefig(salvar_em)
    print(f"✅ Gráfico de barras salvo em: {salvar_em}")
    plt.show()

gerar_grafico_barras("resultados/benchmark_mosp.csv")