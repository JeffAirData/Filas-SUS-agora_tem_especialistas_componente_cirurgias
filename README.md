# Como Reduzir Filas no SUS - Pipeline de Coleta, Curadoria e Base Analitica

Projeto em Python para descoberta, coleta e consolidacao de dados do Programa Agora Tem Especialistas (Componente Cirurgias), com foco em gerar uma base final pronta para analise e Power BI.

O projeto surgiu como uma busca webscraping por dados acerca de filas no SUS - Brasil - e como a maioria desses dados são sensíveis, vez que seu compartilhamento pode ferir normas éticas, definiu-se em certo momento o uso dos dados disponibilizados pelo Programa em um corte bem definido que é a previsão e realização de cirurgias. Certo de que a publicizacao destes dados não ferem a LGPD e podem ser utilizados como dados anônimos.

Outros cortes poderão surgir, outra vez que, o projeto de mentoria Fiocruz está no início e poderemos ainda falar muito sobre filas no SUS, na tentativa de, senão acabar com o problema, ao menos contribuir com a melhora do sistema.


## Objetivo

Transformar a coleta bruta em uma esteira analitica reproduzivel:

1. Descobrir datasets no Portal de Dados Abertos da Saude.
2. Filtrar apenas recursos de alta relevancia.
3. Baixar e validar artefatos (incluindo ZIP).
4. Consolidar uma tabela final para analise por UF, competencia e indicador.
5. Gerar arquivos auxiliares para BI (metricas, dicionario e painel executivo).

## O que foi feito (passo a passo)

1. Diagnostico inicial
- Execucao dos scripts e identificacao de dependencias ausentes.
- Ajuste do ambiente Python e instalacao de bibliotecas necessarias.

2. Limpeza e robustez da coleta
- Tratamento de fontes indisponiveis (ex.: respostas 404).
- Resiliencia por fonte para evitar interrupcao total do processo.

3. Refatoracao da estrategia de descoberta
- Troca de raspagem generica por descoberta orientada ao portal oficial.
- Classificacao de relevancia (alta/media/baixa).
- Restricao para processamento de alta relevancia.

4. Qualidade de artefatos
- Validacao para evitar salvar HTML como se fosse CSV.
- Download, extracao de ZIP e inventario dos arquivos extraidos.

5. Consolidacao analitica
- Geracao da tabela final com padronizacao de campos.
- Producao de metricas-chave, dicionario de variaveis e interpretacao direta.
- Geracao da tabela pronta para Power BI e painel executivo por UF.

## Estrutura principal

```
.
├── src/
│   ├── main.py
│   ├── scrapers/
│   │   ├── fila_dataset_scraper.py
│   │   ├── fila_metadata_scraper.py
│   │   ├── fila_scraper.py
│   │   └── fila_scraper (2).py
│   └── tools/
│       └── build_final_analytical_table.py
├── data/
│   ├── filas/
│   │   ├── analytical_datasets.csv
│   │   ├── analytical_resources.csv
│   │   ├── downloads.csv
│   │   ├── extracted_inventory.csv
│   │   └── final/
│   │       ├── tabela_final_analitica.csv
│   │       ├── tabela_powerbi.csv
│   │       ├── painel_executivo_uf.csv
│   │       ├── metricas_principais.csv
│   │       ├── dicionario_variaveis.csv
│   │       ├── interpretacao_direta.md
│   │       ├── powerbi_especificacao.md
│   │       └── medidas_dax.md
│   └── metadata/
│       ├── filas_sus_metadata.csv
│       └── filas_sus_metadata.json
└── requirements.txt
```

## Requisitos

- Python 3.10+
- Ambiente virtual recomendado
- Dependencias em `requirements.txt`

## Como executar

1. Criar e ativar ambiente virtual

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

3. Rodar pipeline principal (dados + metadados)

```powershell
python src/main.py
```

4. Gerar base final analitica

```powershell
python src/tools/build_final_analytical_table.py
```

<img width="1600" height="675" alt="image" src="https://github.com/user-attachments/assets/8738aa04-91db-46ed-8158-33807098d80d" />


## Saidas para analise e BI

Arquivos mais importantes para consumo:

- `data/filas/final/tabela_powerbi.csv`: base principal para o modelo no Power BI.
- `data/filas/final/painel_executivo_uf.csv`: resumo executivo por UF.
- `data/filas/final/metricas_principais.csv`: KPIs consolidados.
- `data/filas/final/dicionario_variaveis.csv`: definicao dos campos.
- `data/filas/final/medidas_dax.md`: medidas sugeridas em DAX.

## Acesso ao BI [Link Dashboard]:
(https://app.powerbi.com/groups/me/reports/4eefb0bb-2ad6-402d-99a3-26d83da3503d/f38f12716d4efc0600ed?experience=power-bi)


<img width="1600" height="675" alt="image" src="https://github.com/user-attachments/assets/a1f65e43-f87a-4c7c-83d3-0c995b0f173c" />


## Conclusão à primeira vista

Vemos por exemplo nos gráficos que o número de cirurgias por região e UF aumentam do início de janeiro num crescente até o final do ano em dezembro, voltando a diminuir no início de janeiro do próximo ano. E que as cirurgias realizadas e eletivas ultrapassam as planejadas no decorrer do ano. E mais, percebemos que para este corte a tendência é sempre pelo aumento do número de cirurgias elevando também a proporção horasmédicos* , sendo necessário o aumento desses profissionais a cada ano (talvez devido ao aumento da população, os fatores precisam de uma análise mais aprofundada para uma conclusão tão abrangente, mas já é um indício).

*horasmédicos : neologismo aplicado a quantidade de horas que um certo número de profissionais da saúde necessita para executar uma tarefa.


## Rastreabilidade da fonte

Para identificar origem institucional e recurso baixado:

- `data/filas/analytical_datasets.csv` (coluna `dataset_url`)
- `data/filas/downloads.csv` (coluna `resource_url`)

## Licenciamento e uso

### Codigo deste repositorio

- Recomenda-se publicar o codigo sob licenca MIT (arquivo `LICENSE`).
- Isso permite uso, copia, modificacao e distribuicao, com manutencao do aviso de copyright.

### Dados publicos de terceiros

- Os dados utilizados neste projeto sao obtidos de fontes institucionais publicas.
- Este repositorio nao relicencia os dados de origem como propriedade propria.
- O uso dos dados deve respeitar os termos oficiais das fontes publicadoras.
- Sempre valide restricoes, atualizacoes e notas metodologicas no portal oficial.

### Atribuicao recomendada (texto pronto)

Use o modelo abaixo quando publicar derivacoes deste projeto:

"Este trabalho reutiliza codigo do projeto Filas SUS - Pipeline de Coleta, Curadoria e Base Analitica e dados publicos institucionais de saude. As regras de uso dos dados seguem os termos da fonte oficial."

## Colaboracao e forks

- O repositorio pode ser publico para consulta e reproducao.
- Contribuicoes por terceiros podem ser desabilitadas no fluxo de manutencao do projeto.
- Usuarios podem fazer fork/copia para uso proprio, respeitando a licenca do codigo e os termos dos dados.

## Observacoes

- O foco atual e manter apenas fontes de alta relevancia para reduzir ruido analitico.
- Metadados institucionais permanecem no pipeline para auditoria e governanca.
