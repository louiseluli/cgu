"""Templated one-paragraph "story starter" per municipality, aimed at the
edital's "reportagens" reuse format — a citable fact, not a data dump."""

MIN_CELL_COUNT = 100


def format_brl(value: float, signed: bool = False) -> str:
    sign = "-" if value < 0 else ("+" if signed else "")
    return f"{sign}R${abs(value):,.0f}".replace(",", ".")


def build_story(row: dict, rank: int | None, n_qualified: int) -> str:
    name = row["municipality_name"]
    uf = row["uf_sigla"]
    actual = row["actual_gap"]
    invis = row["invisibility_index"]
    invis_pct = row["invisibility_pct"]
    qualified = row["count_male_white"] >= MIN_CELL_COUNT and row["count_female_black"] >= MIN_CELL_COUNT

    direction = "maior" if actual >= 0 else "menor"
    lede = (
        f"Em {name} ({uf}), o salário médio de homens brancos supera o de mulheres "
        f"negras em {format_brl(abs(actual))} por mês (dados RAIS, 2024)."
        if actual >= 0
        else
        f"Em {name} ({uf}), mulheres negras ganham em média {format_brl(abs(actual))} "
        f"a mais por mês do que homens brancos (dados RAIS, 2024) — um dos poucos "
        f"municípios do estado nessa situação."
    )

    if not qualified:
        return (
            f"{lede} Atenção: a amostra local é pequena "
            f"({int(row['count_female_black'])} mulheres negras empregadas formalmente), "
            f"então esse número deve ser lido com cautela — não é possível comparar de "
            f"forma confiável com outros municípios a partir daqui."
        )

    if abs(invis_pct) < 5:
        compounding = (
            "Esse valor está próximo do que se esperaria somando o efeito médio do "
            "gênero ao efeito médio da raça separadamente — ou seja, aqui a "
            "desigualdade interseccional não foge muito do previsto por uma leitura "
            "de eixo único."
        )
    elif invis_pct >= 5:
        compounding = (
            f"Isso é {abs(invis_pct):.0f}% maior do que a soma simples do efeito de "
            f"gênero com o efeito de raça calculados separadamente ({format_brl(row['sex_only_gap'])} "
            f"+ {format_brl(row['race_only_gap'])}) previa — um efeito de composição que "
            f"desaparece em qualquer leitura de eixo único (só gênero, ou só raça)."
        )
    else:
        compounding = (
            f"Isso é {abs(invis_pct):.0f}% menor do que a soma simples do efeito de "
            f"gênero com o efeito de raça calculados separadamente previa — aqui os "
            f"dois eixos parecem se sobrepor parcialmente, em vez de se somar."
        )

    rank_note = ""
    if rank is not None:
        rank_note = (
            f" Entre os {n_qualified} municípios do RJ com amostra suficiente para "
            f"comparação, {name} ocupa a posição #{rank} por tamanho do efeito "
            f"interseccional (em R$)."
        )

    return f"{lede} {compounding}{rank_note}"
