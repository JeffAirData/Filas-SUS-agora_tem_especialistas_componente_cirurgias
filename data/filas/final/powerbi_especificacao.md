# Especificacao Power BI - Filas SUS

## 1) Fonte de dados
- Tabela principal: data/filas/final/tabela_powerbi.csv
- Tabela de apoio ranking: data/filas/final/painel_executivo_uf.csv
- Tabela de apoio metricas: data/filas/final/metricas_principais.csv

## 2) Modelo recomendado
- Fato principal: tabela_powerbi
- Dim calendario: gerar por DAX com base em dt_competencia
- Dim territorio (opcional): derivar de tabela_powerbi (territorio_chave, territorio_sigla_uf, territorio_nome_uf, territorio_sigla_regiao, territorio_nome_regiao)

Relacoes:
- calendario[Data] 1:* tabela_powerbi[dt_competencia]
- dim_territorio[territorio_chave] 1:* tabela_powerbi[territorio_chave] (opcional)

## 3) Abas e visuais

### Aba 1 - Visao Nacional
Objetivo: panorama de producao e diferencas entre previsto e realizado.

Visuais:
- Cartoes:
  - Previstas Brasil
  - Realizadas Brasil
  - Rol PATE Brasil
  - Taxa Execucao Brasil
  - Gap Brasil
- Linha temporal:
  - Eixo: competencia_ano_mes
  - Legenda: indicador
  - Valor: Soma Valor UF
- Matriz por regiao:
  - Linhas: territorio_nome_regiao
  - Colunas: indicador
  - Valores: Soma Valor UF

Filtros:
- competencia_ano
- indicador
- territorio_granularidade

### Aba 2 - Ranking UF
Objetivo: priorizacao tatico-operacional de estados.

Fonte principal: painel_executivo_uf.csv

Visuais:
- Tabela ranking pior gap:
  - Filtro visual ranking_tipo = top_pior_gap
  - Colunas: ranking_posicao, sg_uf, no_uf, previstas_uf, realizadas_uf, gap_previstas_menos_realizadas, taxa_execucao
- Tabela ranking melhor evolucao:
  - Filtro visual ranking_tipo = top_melhor_evolucao_realizadas
  - Colunas: ranking_posicao, sg_uf, no_uf, evolucao_abs_realizadas, evolucao_pct_realizadas
- Barras horizontal (Top 10 pior gap):
  - Eixo: no_uf
  - Valor: gap_previstas_menos_realizadas

### Aba 3 - Evolucao Temporal
Objetivo: acompanhar tendencia por UF.

Visuais:
- Linha por UF selecionada:
  - Eixo: competencia_ano_mes
  - Valor: Soma Valor UF
  - Legenda: indicador
- Area (opcional):
  - Eixo: competencia_ano_mes
  - Valor: Soma Valor UF
  - Filtro: indicador = cirurgias_realizadas_programa

Filtros:
- territorio_sigla_uf
- competencia_ano

### Aba 4 - Qualidade e Governanca
Objetivo: confiabilidade e rastreabilidade dos dados.

Visuais:
- Cartao: Max dt_atualizacao
- Tabela de completude:
  - colunas: indicador, contagem de linhas, nulos de co_uf, nulos de dt_competencia, nulos de vl_indicador_calculado_uf
- Tabela de origem:
  - colunas: arquivo_origem, contagem de linhas

## 4) Regras de ordenacao e formatacao
- Ordenar competencia_ano_mes por periodo_ordem.
- Formatar taxa_execucao e evolucao_pct_realizadas como percentual.
- Formatar valores de volume com separador de milhar e 0 casas decimais.

## 5) Checagens de consistencia
- Confirmar se competencia_ano_mes cobre todas as competencias esperadas.
- Verificar se taxa_execucao > 100% ocorre em serie especifica e interpretar como diferenca metodologica de indicadores, nao necessariamente erro.
- Garantir que filtros de granularidade nao misturem UF com BR/REG quando a analise for estadual.
