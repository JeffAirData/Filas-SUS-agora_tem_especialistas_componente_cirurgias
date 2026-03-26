from __future__ import annotations

from pathlib import Path
import pandas as pd

BASE_DIR = Path("data/filas")
EXTRACTED_BASE = BASE_DIR / "extracted" / "mgdi_agora_tem_especialistas_componente_cirurgias"
FINAL_DIR = BASE_DIR / "final"

INPUTS = {
    "cirurgias_previstas_programa": EXTRACTED_BASE
    / "cirurgias_previstas_no_programa_csv"
    / "pnrfcirpre.csv",
    "cirurgias_realizadas_programa": EXTRACTED_BASE
    / "cirurgias_realizadas_pelo_programa_agora_tem_especialista_csv"
    / "pnrfcirrea.csv",
    "procedimentos_eletivos_rol_pate": EXTRACTED_BASE
    / "quantidade_de_procedimentos_cirurgicos_eletivos_do_rol_do_programa_agora_tem_especialista_csv"
    / "mgdi_ms_3f6.csv",
}


def _ensure_inputs() -> None:
    missing = [f"{key}: {path}" for key, path in INPUTS.items() if not path.exists()]
    if missing:
        raise FileNotFoundError("Arquivos de entrada ausentes:\n" + "\n".join(missing))


def _load_and_stack() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for indicador, file_path in INPUTS.items():
        df = pd.read_csv(file_path, encoding="utf-8-sig")
        df["indicador"] = indicador
        df["arquivo_origem"] = str(file_path)
        frames.append(df)

    final_df = pd.concat(frames, ignore_index=True)

    final_df["dt_competencia"] = pd.to_datetime(final_df["dt_competencia"], errors="coerce")
    final_df["dt_atualizacao"] = pd.to_datetime(final_df["dt_atualizacao"], errors="coerce")
    final_df["co_anomes"] = pd.to_numeric(final_df["co_anomes"], errors="coerce")

    numeric_cols = [
        "vl_indicador_calculado_uf",
        "vl_indicador_calculado_reg",
        "vl_indicador_calculado_br",
    ]
    for col in numeric_cols:
        final_df[col] = pd.to_numeric(final_df[col], errors="coerce")

    return final_df


def _latest_br_value(df: pd.DataFrame, indicador: str) -> float:
    subset = df[df["indicador"] == indicador].copy()
    if subset.empty:
        return 0.0

    latest_date = subset["dt_competencia"].max()
    latest_subset = subset[subset["dt_competencia"] == latest_date]
    values = latest_subset["vl_indicador_calculado_br"].dropna()
    if values.empty:
        return 0.0
    return float(values.iloc[0])


def _build_metrics(df: pd.DataFrame) -> pd.DataFrame:
    metrics: list[dict] = []

    latest_competencia = df["dt_competencia"].max()
    latest_competencia_str = latest_competencia.strftime("%Y-%m") if pd.notna(latest_competencia) else ""

    # Volume total por indicador (soma UF em todas as competencias)
    agg = (
        df[df["sg_granularidade"].str.upper() == "UF"]
        .groupby("indicador", dropna=False)["vl_indicador_calculado_uf"]
        .sum(min_count=1)
        .fillna(0)
        .to_dict()
    )
    for indicador, value in agg.items():
        metrics.append(
            {
                "metrica": "volume_total_uf_no_periodo",
                "indicador": indicador,
                "valor": float(value),
                "periodo_referencia": "historico_disponivel",
                "descricao": "Soma de vl_indicador_calculado_uf em todas as competencias disponiveis.",
            }
        )

    previstas_br = _latest_br_value(df, "cirurgias_previstas_programa")
    realizadas_br = _latest_br_value(df, "cirurgias_realizadas_programa")
    rol_br = _latest_br_value(df, "procedimentos_eletivos_rol_pate")

    if previstas_br > 0:
        taxa_execucao = realizadas_br / previstas_br
    else:
        taxa_execucao = 0.0

    gap = previstas_br - realizadas_br
    participacao_rol = (rol_br / realizadas_br) if realizadas_br > 0 else 0.0

    metrics.extend(
        [
            {
                "metrica": "previstas_brasil_competencia_mais_recente",
                "indicador": "cirurgias_previstas_programa",
                "valor": previstas_br,
                "periodo_referencia": latest_competencia_str,
                "descricao": "Valor Brasil do indicador de cirurgias previstas na competencia mais recente.",
            },
            {
                "metrica": "realizadas_brasil_competencia_mais_recente",
                "indicador": "cirurgias_realizadas_programa",
                "valor": realizadas_br,
                "periodo_referencia": latest_competencia_str,
                "descricao": "Valor Brasil do indicador de cirurgias realizadas na competencia mais recente.",
            },
            {
                "metrica": "rol_pate_brasil_competencia_mais_recente",
                "indicador": "procedimentos_eletivos_rol_pate",
                "valor": rol_br,
                "periodo_referencia": latest_competencia_str,
                "descricao": "Valor Brasil do indicador de procedimentos eletivos do rol PATE na competencia mais recente.",
            },
            {
                "metrica": "taxa_execucao_realizadas_sobre_previstas",
                "indicador": "comparativo_previstas_realizadas",
                "valor": taxa_execucao,
                "periodo_referencia": latest_competencia_str,
                "descricao": "Razao entre realizadas e previstas na competencia mais recente.",
            },
            {
                "metrica": "gap_previstas_menos_realizadas",
                "indicador": "comparativo_previstas_realizadas",
                "valor": gap,
                "periodo_referencia": latest_competencia_str,
                "descricao": "Diferenca entre cirurgias previstas e realizadas no Brasil na competencia mais recente.",
            },
            {
                "metrica": "participacao_rol_pate_sobre_realizadas",
                "indicador": "comparativo_rol_vs_realizadas",
                "valor": participacao_rol,
                "periodo_referencia": latest_competencia_str,
                "descricao": "Participacao do rol PATE sobre o total de cirurgias realizadas na competencia mais recente.",
            },
        ]
    )

    return pd.DataFrame(metrics)


def _build_dictionary() -> pd.DataFrame:
    rows = [
        {
            "variavel": "co_anomes",
            "tipo": "inteiro",
            "descricao": "Competencia no formato AAAAMM.",
            "exemplo": "202507",
        },
        {
            "variavel": "co_uf",
            "tipo": "inteiro",
            "descricao": "Codigo IBGE da unidade federativa.",
            "exemplo": "35",
        },
        {
            "variavel": "no_municipio",
            "tipo": "texto",
            "descricao": "Nome do municipio quando granularidade for municipal.",
            "exemplo": "Sao Paulo",
        },
        {
            "variavel": "sg_uf",
            "tipo": "texto",
            "descricao": "Sigla da unidade federativa.",
            "exemplo": "SP",
        },
        {
            "variavel": "no_uf",
            "tipo": "texto",
            "descricao": "Nome da unidade federativa.",
            "exemplo": "Sao Paulo",
        },
        {
            "variavel": "co_regiao_brasil",
            "tipo": "inteiro",
            "descricao": "Codigo da regiao geografica brasileira.",
            "exemplo": "3",
        },
        {
            "variavel": "no_regiao_brasil",
            "tipo": "texto",
            "descricao": "Nome da regiao brasileira.",
            "exemplo": "Sudeste",
        },
        {
            "variavel": "sg_regiao_brasil",
            "tipo": "texto",
            "descricao": "Sigla da regiao brasileira.",
            "exemplo": "SE",
        },
        {
            "variavel": "vl_indicador_calculado_uf",
            "tipo": "numerico",
            "descricao": "Valor do indicador no nivel da UF.",
            "exemplo": "18315",
        },
        {
            "variavel": "vl_indicador_calculado_reg",
            "tipo": "numerico",
            "descricao": "Valor do indicador no nivel da regiao.",
            "exemplo": "183322",
        },
        {
            "variavel": "vl_indicador_calculado_br",
            "tipo": "numerico",
            "descricao": "Valor do indicador no nivel Brasil.",
            "exemplo": "3101449",
        },
        {
            "variavel": "dt_competencia",
            "tipo": "data",
            "descricao": "Data de referencia da competencia do indicador.",
            "exemplo": "2025-07-01",
        },
        {
            "variavel": "dt_atualizacao",
            "tipo": "datahora",
            "descricao": "Data e hora da ultima atualizacao do registro.",
            "exemplo": "2026-02-28 03:06:44",
        },
        {
            "variavel": "ds_unidade_medida",
            "tipo": "texto",
            "descricao": "Descricao da unidade de medida do indicador.",
            "exemplo": "Numero",
        },
        {
            "variavel": "sg_granularidade",
            "tipo": "texto",
            "descricao": "Sigla do nivel de agregacao territorial.",
            "exemplo": "UF",
        },
        {
            "variavel": "ds_granularidade",
            "tipo": "texto",
            "descricao": "Descricao do nivel de agregacao territorial.",
            "exemplo": "Unidade Federativa",
        },
        {
            "variavel": "indicador",
            "tipo": "categorica",
            "descricao": "Serie analitica de origem: previstas, realizadas ou rol PATE.",
            "exemplo": "cirurgias_realizadas_programa",
        },
        {
            "variavel": "arquivo_origem",
            "tipo": "texto",
            "descricao": "Caminho do CSV de origem dentro da estrutura extraida.",
            "exemplo": ".../pnrfcirrea.csv",
        },
    ]
    return pd.DataFrame(rows)


def _build_interpretation(metrics_df: pd.DataFrame) -> str:
    lookup = {(row["metrica"], row["indicador"]): row["valor"] for _, row in metrics_df.iterrows()}
    period = metrics_df.loc[
        metrics_df["metrica"] == "previstas_brasil_competencia_mais_recente", "periodo_referencia"
    ].iloc[0]

    previstas = lookup.get(("previstas_brasil_competencia_mais_recente", "cirurgias_previstas_programa"), 0.0)
    realizadas = lookup.get(("realizadas_brasil_competencia_mais_recente", "cirurgias_realizadas_programa"), 0.0)
    rol = lookup.get(("rol_pate_brasil_competencia_mais_recente", "procedimentos_eletivos_rol_pate"), 0.0)
    taxa = lookup.get(("taxa_execucao_realizadas_sobre_previstas", "comparativo_previstas_realizadas"), 0.0)
    gap = lookup.get(("gap_previstas_menos_realizadas", "comparativo_previstas_realizadas"), 0.0)
    part_rol = lookup.get(("participacao_rol_pate_sobre_realizadas", "comparativo_rol_vs_realizadas"), 0.0)

    return (
        "# Interpretação Analítica para Decisão\n\n"
        "## Pergunta analítica de cada CSV\n"
        "1. pnrfcirpre.csv: Qual o volume de cirurgias previstas por UF/região/Brasil em cada competência?\n"
        "2. pnrfcirrea.csv: Qual o volume de cirurgias realizadas por UF/região/Brasil em cada competência?\n"
        "3. mgdi_ms_3f6.csv: Qual o volume de procedimentos eletivos realizados no rol PATE por UF/região/Brasil em cada competência?\n\n"
        "## Métricas principais (competência mais recente)\n"
        f"- Competência mais recente: {period}\n"
        f"- Cirurgias previstas (Brasil): {previstas:,.0f}\n"
        f"- Cirurgias realizadas (Brasil): {realizadas:,.0f}\n"
        f"- Procedimentos do rol PATE (Brasil): {rol:,.0f}\n"
        f"- Taxa de execução (realizadas/previstas): {taxa:.2%}\n"
        f"- Gap previsto - realizado: {gap:,.0f}\n"
        f"- Participação rol PATE sobre realizadas: {part_rol:.2%}\n\n"
        "## Leitura executiva\n"
        "- Se a taxa de execução estiver abaixo de 100%, há espaço para ampliar capacidade cirúrgica ou reduzir perdas operacionais.\n"
        "- Gap positivo indica fila potencial futura se a produção não acompanhar o volume previsto.\n"
        "- Alta participação do rol PATE nas realizadas sugere aderência ao foco prioritário do programa.\n"
        "- Use cortes por UF e por competência para priorizar territórios com maior discrepância prevista versus realizada.\n"
    )


def _build_executive_panel_uf(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    uf_base = df[df["sg_granularidade"].str.upper() == "UF"].copy()
    latest_competencia = uf_base["dt_competencia"].max()
    latest = uf_base[uf_base["dt_competencia"] == latest_competencia].copy()

    previstas = latest[latest["indicador"] == "cirurgias_previstas_programa"][
        ["sg_uf", "no_uf", "vl_indicador_calculado_uf"]
    ].rename(columns={"vl_indicador_calculado_uf": "previstas_uf"})

    realizadas = latest[latest["indicador"] == "cirurgias_realizadas_programa"][
        ["sg_uf", "no_uf", "vl_indicador_calculado_uf"]
    ].rename(columns={"vl_indicador_calculado_uf": "realizadas_uf"})

    base = previstas.merge(realizadas, on=["sg_uf", "no_uf"], how="outer")
    base["previstas_uf"] = base["previstas_uf"].fillna(0)
    base["realizadas_uf"] = base["realizadas_uf"].fillna(0)
    base["gap_previstas_menos_realizadas"] = base["previstas_uf"] - base["realizadas_uf"]
    base["taxa_execucao"] = base.apply(
        lambda row: (row["realizadas_uf"] / row["previstas_uf"]) if row["previstas_uf"] > 0 else 0,
        axis=1,
    )

    realizadas_hist = uf_base[uf_base["indicador"] == "cirurgias_realizadas_programa"].copy()
    first_by_uf = (
        realizadas_hist.sort_values("dt_competencia")
        .groupby("sg_uf", as_index=False)
        .first()[["sg_uf", "vl_indicador_calculado_uf"]]
        .rename(columns={"vl_indicador_calculado_uf": "realizadas_primeira_competencia"})
    )
    latest_by_uf = (
        realizadas_hist.sort_values("dt_competencia")
        .groupby("sg_uf", as_index=False)
        .last()[["sg_uf", "vl_indicador_calculado_uf"]]
        .rename(columns={"vl_indicador_calculado_uf": "realizadas_ultima_competencia"})
    )

    evolucao = first_by_uf.merge(latest_by_uf, on="sg_uf", how="inner")
    evolucao["evolucao_abs_realizadas"] = (
        evolucao["realizadas_ultima_competencia"] - evolucao["realizadas_primeira_competencia"]
    )
    evolucao["evolucao_pct_realizadas"] = evolucao.apply(
        lambda row: (
            row["evolucao_abs_realizadas"] / row["realizadas_primeira_competencia"]
            if row["realizadas_primeira_competencia"] > 0
            else 0
        ),
        axis=1,
    )

    base = base.merge(evolucao[["sg_uf", "evolucao_abs_realizadas", "evolucao_pct_realizadas"]], on="sg_uf", how="left")
    base["competencia_referencia"] = latest_competencia.strftime("%Y-%m") if pd.notna(latest_competencia) else ""

    pior_gap = base.sort_values("gap_previstas_menos_realizadas", ascending=False).head(top_n).copy()
    pior_gap["ranking_tipo"] = "top_pior_gap"
    pior_gap["ranking_posicao"] = range(1, len(pior_gap) + 1)

    melhor_evolucao = base.sort_values("evolucao_abs_realizadas", ascending=False).head(top_n).copy()
    melhor_evolucao["ranking_tipo"] = "top_melhor_evolucao_realizadas"
    melhor_evolucao["ranking_posicao"] = range(1, len(melhor_evolucao) + 1)

    panel = pd.concat([pior_gap, melhor_evolucao], ignore_index=True)
    panel = panel[
        [
            "ranking_tipo",
            "ranking_posicao",
            "competencia_referencia",
            "sg_uf",
            "no_uf",
            "previstas_uf",
            "realizadas_uf",
            "gap_previstas_menos_realizadas",
            "taxa_execucao",
            "evolucao_abs_realizadas",
            "evolucao_pct_realizadas",
        ]
    ]
    return panel


def _build_powerbi_table(df: pd.DataFrame) -> pd.DataFrame:
    powerbi = df.copy()
    powerbi["competencia_ano"] = powerbi["dt_competencia"].dt.year
    powerbi["competencia_mes"] = powerbi["dt_competencia"].dt.month
    powerbi["competencia_ano_mes"] = powerbi["dt_competencia"].dt.strftime("%Y-%m")
    powerbi["periodo_ordem"] = powerbi["co_anomes"]

    powerbi["territorio_chave"] = powerbi.apply(
        lambda row: (
            f"UF-{row['sg_uf']}"
            if str(row.get("sg_granularidade", "")).upper() == "UF"
            else (
                f"REG-{row.get('sg_regiao_brasil', '')}"
                if str(row.get("sg_granularidade", "")).upper() == "REG"
                else "BR"
            )
        ),
        axis=1,
    )

    powerbi = powerbi.rename(
        columns={
            "no_uf": "territorio_nome_uf",
            "no_regiao_brasil": "territorio_nome_regiao",
            "sg_uf": "territorio_sigla_uf",
            "sg_regiao_brasil": "territorio_sigla_regiao",
            "ds_granularidade": "territorio_granularidade",
        }
    )

    ordered_columns = [
        "indicador",
        "co_anomes",
        "competencia_ano",
        "competencia_mes",
        "competencia_ano_mes",
        "periodo_ordem",
        "dt_competencia",
        "dt_atualizacao",
        "territorio_granularidade",
        "territorio_chave",
        "territorio_sigla_uf",
        "territorio_nome_uf",
        "territorio_sigla_regiao",
        "territorio_nome_regiao",
        "co_uf",
        "no_municipio",
        "vl_indicador_calculado_uf",
        "vl_indicador_calculado_reg",
        "vl_indicador_calculado_br",
        "ds_unidade_medida",
        "arquivo_origem",
    ]
    return powerbi[ordered_columns]


def build_final_outputs() -> None:
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_inputs()

    final_table = _load_and_stack()
    metrics = _build_metrics(final_table)
    dictionary = _build_dictionary()
    interpretation_text = _build_interpretation(metrics)
    executive_panel = _build_executive_panel_uf(final_table)
    powerbi_table = _build_powerbi_table(final_table)

    final_table.to_csv(FINAL_DIR / "tabela_final_analitica.csv", index=False, encoding="utf-8-sig")
    executive_panel.to_csv(FINAL_DIR / "painel_executivo_uf.csv", index=False, encoding="utf-8-sig")
    powerbi_table.to_csv(FINAL_DIR / "tabela_powerbi.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(FINAL_DIR / "metricas_principais.csv", index=False, encoding="utf-8-sig")
    dictionary.to_csv(FINAL_DIR / "dicionario_variaveis.csv", index=False, encoding="utf-8-sig")

    with open(FINAL_DIR / "interpretacao_direta.md", "w", encoding="utf-8") as f:
        f.write(interpretation_text)

    print("[OK] Tabela final gerada em:", FINAL_DIR / "tabela_final_analitica.csv")
    print("[OK] Painel executivo UF gerado em:", FINAL_DIR / "painel_executivo_uf.csv")
    print("[OK] Tabela Power BI gerada em:", FINAL_DIR / "tabela_powerbi.csv")
    print("[OK] Métricas geradas em:", FINAL_DIR / "metricas_principais.csv")
    print("[OK] Dicionário gerado em:", FINAL_DIR / "dicionario_variaveis.csv")
    print("[OK] Interpretação gerada em:", FINAL_DIR / "interpretacao_direta.md")


if __name__ == "__main__":
    build_final_outputs()
