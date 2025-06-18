# MOSP - Minimization of Open Stacks Problem

Este projeto implementa heurísticas para o MOSP (Minimization of Open Stacks Problem), utilizando representações de grafos e estratégias de busca para minimizar o Número Máximo de Pilhas Abertas (NMPA).

O código possui documentação e estrutura padronizada para facilitar a manutenção e o entendimento do projeto.

## Estrutura do projeto
```
Trab_MOSP/
├── mosp/                   
│   ├── busca_bfs.py
│   ├── busca_dfs.py
│   ├── custo_nmpa.py
│   ├── grafo.py
│   ├── heuristicas.py
│   ├── leitura_instancia.py
│   ├── metricas.py
│   ├── refinamento.py
├── benchmark.py            
├── main.py                 
├── gerar_grafico.py
├── teste_limiar_densidade.py
├── plot_teste_limiar.py   
├── cenarios/               
├── resultados/             
└── .gitignore
```

## Pré-requisitos

- Python 3.6 ou superior (projeto testado com Python 3.12)
- Bibliotecas necessárias:
  ```
  pip install networkx pandas matplotlib
  ```
  
## Como executar

1. Executar o benchmark completo (gera um arquivo CSV com os resultados):
   ```
   python3 benchmark.py
   ```
Gera o arquivo: resultados/benchmark_mosp.csv.

2. Gerar o gráfico de comparação das heurísticas:
   ```
   python3 gerar_grafico.py
   ```
Gera o arquivo: resultados/grafico_barras.png.

3. Testar uma instância individual:
   ```
   python3 main.py
   ```
Exibe no console:
- A ordem de produção gerada
- O respectivo NMPA (Número Máximo de Pilhas Abertas)

## Organização do código
- mosp/: contém os módulos do projeto, com as funções reutilizáveis para:
  - Leitura das instâncias
  - Construção do grafo padrão-padrão
  - Heurísticas implementadas
  - Cálculo do NMPA
- benchmark.py: script principal que executa todas as instâncias e gera os resultados no arquivo CSV.
- main.py: script para depuração e teste, que executa uma instância específica.
- gerar_grafico.py: script de visualização que gera um gráfico comparativo das heurísticas.
- cenarios/: pasta que contém as instâncias de entrada (.txt).
- resultados/: pasta onde são gerados os resultados e gráficos.
- .gitignore: define arquivos e pastas que não devem ser versionados, como `__pycache__`, arquivos temporários e arquivos específicos do sistema.

## Autores

Projeto desenvolvido por:
- Giovana Silverio Pereira
- Laís Padovan
- Paulo Olympio
- Rodrigo Rocha
