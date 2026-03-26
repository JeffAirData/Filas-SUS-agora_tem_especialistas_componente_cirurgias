# Filas SUS - Pipeline de Coleta, Curadoria e Base Analitica

Projeto em Python para descoberta, coleta e consolidacao de dados do Programa Agora Tem Especialistas (Componente Cirurgias), com foco em gerar uma base final pronta para analise e Power BI.

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

## Saidas para analise e BI

Arquivos mais importantes para consumo:

- `data/filas/final/tabela_powerbi.csv`: base principal para o modelo no Power BI.
- `data/filas/final/painel_executivo_uf.csv`: resumo executivo por UF.
- `data/filas/final/metricas_principais.csv`: KPIs consolidados.
- `data/filas/final/dicionario_variaveis.csv`: definicao dos campos.
- `data/filas/final/medidas_dax.md`: medidas sugeridas em DAX.

## Publicacao do BI (arquivo no OneDrive)

Se o arquivo `.pbix` esta no OneDrive, o fluxo recomendado e:

1. Abrir o arquivo `.pbix` no Power BI Desktop (direto da pasta sincronizada do OneDrive).
2. Conferir que a origem aponta para `tabela_powerbi.csv` atualizada.
3. Clicar em `Publicar` e escolher o workspace no Power BI Service.
4. No Power BI Service, abrir o dataset e configurar `Atualizacao agendada`.
5. Se o CSV tambem ficar no OneDrive/SharePoint, usar credenciais OAuth da conta organizacional para refresh.
6. Validar no Service se os visuais batem com os indicadores esperados (previstas, realizadas, gap e taxa de execucao).

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