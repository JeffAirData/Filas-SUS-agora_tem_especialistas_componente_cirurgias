# Medidas DAX - Filas SUS

## Calendario
```DAX
Calendario =
ADDCOLUMNS(
    CALENDAR(MIN(tabela_powerbi[dt_competencia]), MAX(tabela_powerbi[dt_competencia])),
    "Ano", YEAR([Date]),
    "Mes", MONTH([Date]),
    "AnoMes", FORMAT([Date], "YYYY-MM"),
    "AnoMesOrdem", YEAR([Date]) * 100 + MONTH([Date])
)
```

## Medidas base
```DAX
Soma Valor UF =
SUM(tabela_powerbi[vl_indicador_calculado_uf])

Soma Valor BR =
SUM(tabela_powerbi[vl_indicador_calculado_br])

Linhas =
COUNTROWS(tabela_powerbi)
```

## Medidas por indicador
```DAX
Previstas UF =
CALCULATE(
    [Soma Valor UF],
    tabela_powerbi[indicador] = "cirurgias_previstas_programa"
)

Realizadas UF =
CALCULATE(
    [Soma Valor UF],
    tabela_powerbi[indicador] = "cirurgias_realizadas_programa"
)

Rol PATE UF =
CALCULATE(
    [Soma Valor UF],
    tabela_powerbi[indicador] = "procedimentos_eletivos_rol_pate"
)
```

## Medidas comparativas
```DAX
Gap UF =
[Previstas UF] - [Realizadas UF]

Taxa Execucao UF =
DIVIDE([Realizadas UF], [Previstas UF], 0)

Participacao Rol PATE =
DIVIDE([Rol PATE UF], [Realizadas UF], 0)
```

## Medidas de variacao temporal
```DAX
Realizadas UF Mes Anterior =
CALCULATE(
    [Realizadas UF],
    DATEADD(Calendario[Date], -1, MONTH)
)

Variacao Mensal Realizadas =
[Realizadas UF] - [Realizadas UF Mes Anterior]

Variacao Mensal Realizadas % =
DIVIDE([Variacao Mensal Realizadas], [Realizadas UF Mes Anterior], 0)
```

## Medidas de qualidade
```DAX
Nulos co_uf =
COUNTROWS(
    FILTER(tabela_powerbi, ISBLANK(tabela_powerbi[co_uf]))
)

Nulos dt_competencia =
COUNTROWS(
    FILTER(tabela_powerbi, ISBLANK(tabela_powerbi[dt_competencia]))
)

Nulos valor_uf =
COUNTROWS(
    FILTER(tabela_powerbi, ISBLANK(tabela_powerbi[vl_indicador_calculado_uf]))
)

Ultima Atualizacao =
MAX(tabela_powerbi[dt_atualizacao])
```

## Configuracoes importantes
- Ordenar tabela_powerbi[competencia_ano_mes] por tabela_powerbi[periodo_ordem].
- Definir tipo de dado data para tabela_powerbi[dt_competencia].
- Definir tipo de dado numero inteiro para tabela_powerbi[periodo_ordem].
