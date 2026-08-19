# CGU 2º Concurso de Reúso de Dados Abertos — Submission Plan

## 1. Project concept

**Working title:** Interseccionalidade Salarial — mapping how sex × race × territory
compound wage inequality in Brazilian formal employment.

**One-liner:** An intersectional analysis of the RAIS labor microdata showing that
the wage gap between white men and Black women is not a low-skill phenomenon — it is
largest and *widening* among senior, credentialed workers in specific municipalities,
and this pattern is invisible in any single-axis (sex-only or race-only) reading of
the data.

**Headline stat — the "invisibility index" (built and verified 18/08):**
actual white-men-vs-Black-women gap minus (sex-only gap + race-only gap), computed
per municipality/year directly from RAIS worker-level aggregates
(`src/cgu_reuso/build_invisibility_index.py`, source: wage_gap's
`municipality_sex_race_summary.csv`). Verified findings, not assumptions:

- **Statewide, the raw pattern is close to additive** (2024: actual gap R$2,622 vs.
  naive sex-only + race-only sum of R$2,710 — invisibility index of only -3.3%).
  Report this honestly rather than force a "bigger than expected" framing the data
  doesn't support at the aggregate level.
- **The real finding is municipality-level heterogeneity, invisible in the
  statewide average**: among the 81 municipalities with ≥100 workers in both the
  white-men and Black-women cells (filtered to exclude small-N noise — unfiltered
  rankings were dominated by towns with 50-170 workers), invisibility_pct has a
  robust p5-p95 spread of **-39% to +40%** (std 52.7 points), with credible named
  cases at -40% (Quissamã) and +52% (Tanguá, Porto Real, Magé). A single-axis or
  state-level reading would never surface this variation — that's the actual
  "invisible" claim this project can defend. **Methodology note (post-EDA):**
  invisibility_pct divides by actual_gap and stays unstable even at N≥100 when a
  municipality's actual gap happens to sit near zero (e.g. Maricá, N=2,004,
  actual_gap=R$29 → -355%, despite ample sample size) — so the top-10 rankings in
  the summary JSON use invisibility_index in **R$**, not percent, and p5/p95
  rather than raw min/max is the reported spread. Full writeup:
  `outputs/tables/eda/eda_briefing.md`.
- **The "not a low-skill phenomenon" claim is independently confirmed with real
  numbers**: the gap as a share of white men's wage rises from ~31-34% at low
  education levels to **54% at complete higher education** and 51% at master's
  (`education_group_intersectional_summary.csv`, 2024).
- **The "widening" claim is confirmed**: Rio de Janeiro municipality's
  intersectional gap grew from R$1,993 (2014) to R$3,643 (2024), +R$1,650
  (`trends/municipality_largest_intersectional_gap_widening_2014_2024.csv`).

**Engineering verification (18/08):** `race_only_gap` and `sex_only_gap`
cross-checked against wage_gap's independently pre-computed `race_report` and
`gaps/municipality_gender_gap.csv` tables — matched to floating-point precision
(diffs ~1e-13), confirming the weighted-mean aggregation is correct and the
source tables are internally consistent. Source data quality checked (zero
duplicate keys, zero nulls, zero non-positive wages/counts, 92/92 municipality
coverage in every included year). A sensitivity check on one definitional choice
(sex-only gap computed across all races vs. black/white only) showed max 11.1%
divergence — not enough to change the conclusion.

Outputs: `outputs/tables/invisibility_index/{municipality,statewide}_invisibility_index.csv`,
`invisibility_index_summary.json`; EDA at `outputs/tables/eda/eda_briefing.md` +
`outputs/figures/eda/*.png`. Scripts: `src/cgu_reuso/build_invisibility_index.py`,
`src/cgu_reuso/eda_invisibility_index.py`. Designed writeup of the full audit
(data quality, both fixes, the race-specificity and uncertainty checks, and a
prioritized enhancement roadmap): https://claude.ai/code/artifact/9260c7cd-08de-4063-89bf-70d33e3980f8
— reusable as-is for the "Apresentação" / methodology-transparency portion of the
submission. These four verified numbers — not the original unverified "always
bigger" assumption — should anchor the narrative writeup, the dashboard's
homepage, and the reúso submission description.

**Themes targeted (per landing page):** Indicadores sociais, Indicadores
econômicos.

**Correction (19/08) — retract the Anexo I claim.** Earlier drafts of this
plan cited "Salário médio de empregados" as a named Anexo I high-value
dataset that item 8.3 scores against directly. That was read from the **1st
edition's** edital PDF. The actual 2026 edital (`EDITAL CGU Nº 46, DE 19 DE
JUNHO DE 2026`, DOU, pasted in full and read directly — see §6, §8) has no
Anexo I high-value-dataset table and no item 8.3 tied to one; its item 8.3 is
just the NC scoring-formula explanation. Retracted from the reúso draft and
narrative. "Salário médio de empregados" is still a fine plain-language
description of the dataset, just not a scoring-mechanism citation.

## 2. Data sources

| Dataset | Role | Catalogued on dados.gov.br? | Notes |
|---|---|---|---|
| RAIS (Relação Anual de Informações Sociais) | Primary | **Yes — verified.** https://dados.gov.br/dataset/relacao-anual-de-informacoes-sociais-rais | Published by Ministério do Trabalho e Emprego (PDET). Satisfies the mandatory "at least one dataset from dados.gov.br" requirement on its own. |
| IBGE malha geométrica dos municípios | Secondary | **Yes — confirmed 19/08.** https://dados.gov.br/dataset/malha-geometrica-dos-municipios-brasileiros | Used for the territorial joins (mesoregion/microregion) throughout wage_gap's outputs. Both sources now cited by exact URL — "duas ou mais fontes" (weight 1) fully satisfied with verifiable links, not just claimed. |

Action item: when filling the Etapa 2 submission form, cite the exact dados.gov.br
RAIS dataset URL above as the required "conjunto de dados utilizado."

## 3. Scope decision: keep the Rio de Janeiro case study

The existing `wage_gap` project already processed RAIS for the MG/ES/RJ regional
file (66 GB raw, filtered down to RJ, 2014–2024) and validated it (42/42 checks).
A true national expansion (27 state units × 10 years) would be on the order of
10x the raw volume — not achievable before the **11/09/2026** submission deadline
(~4 weeks from today, 15/08/2026).

**Decision:** submit the RJ analysis as the core deliverable. Frame the methodology
explicitly as replicable/national-ready in the writeup — this converts the scope
limitation into a stated future-work item rather than hiding it, and costs nothing
to build now.

## 4. Reuse plan

### From `wage_gap` (primary source — already built and validated)
- `src/wage_gap/build_dataset.py`, `column_map.py`, `clean.py`, `data_loader.py` —
  ingestion/harmonization, reusable as-is.
- `build_intersectional_municipality_outputs.py`,
  `build_intersectional_territorial_outputs.py`,
  `build_intersectional_territorial_report_outputs.py`,
  `build_race_report_outputs.py` — the core intersectional analysis layer.
- `build_trend_outputs.py`, `build_composition_outputs.py` — longitudinal +
  education/age/firm-size composition findings (the "not a low-skill phenomenon"
  story).
- `train_xgboost.py` + `explain_xgboost.py` — SHAP-based explainability, feeds
  "Inovação e originalidade" (§6 — corrected 19/08, not its own criterion).
- `build_figures.py`, `build_territorial_figures.py` — existing chart set in
  `outputs/figures/intersectional/`, `.../race/`, `.../territorial/`.

### From `agente_constelacao-archive` (presentation layer only)
- `src/constelacao/web/app.py` Flask app (1212 lines, has `templates/` and
  `static/`) — repoint at the wage_gap processed tables/figures to give the
  submission a browsable dashboard instead of a static report. This is the main
  net-new build for this project.
  (Correction: the live `constelacao/agente_constelacao` path no longer exists on
  disk — the project was archived. Use the `-archive` path above.)

## 5. Gaps / new work needed

1. **Narrative writeup — drafted (19/08).** `submission/narrativa_achados.md`
   — plain-language (Portuguese) findings document anchored on the four
   verified numbers in §1: the invisibility index and municipality
   heterogeneity (Tanguá +52%, Quissamã -40%, named and fact-checked against
   the source CSV — caught and fixed one rounding error, R$1.126→R$1.125,
   during review), the education-gap finding (31-34%→54%), the widening
   trend (Rio de Janeiro +R$1.650, 2014-2024), and the SHAP model with its
   residual-vs-total-effect caveat. Links to the live dashboard and the EDA
   audit artifact. Not yet reviewed for tone/length against actual judge
   expectations — worth a re-read closer to submission.
2. **Presentation layer — built and tested (18/08).** Correction to the
   original plan: the archived Flask app (`agente_constelacao-archive`) turned
   out to have nothing reusable — every route imports from constelação's own
   `orchestration.idea_pipeline` / `chamber_pipeline`, entirely unrelated to
   wage data. Built fresh instead at `src/cgu_reuso/web/` (Flask, server-rendered,
   no JS dependency):
   - **Wage Gap Explorer** (`app.py`, `templates/index.html`) — pick a município,
     see actual gap vs. naive-additive prediction, invisibility index, and a
     per-município trend chart (SVG, breaks correctly across the missing
     2017/2019/2020 years rather than interpolating).
   - **SHAP/XGBoost panel — built (18/08).** `src/cgu_reuso/build_wage_model.py`
     trains on the full validated 2024 panel (5,775,860 rows — not
     wage_gap's own `rio_sample_200k.parquet`, which no script generates and
     which carries no year column, so its provenance couldn't be confirmed;
     traceability mattered more here than reusing an unverified shortcut).
     Test R²=0.734. Result requires careful framing, now built into the UI
     itself, not just this note: sex (#8/10) and race (#9/10) rank lowest in
     SHAP importance — but the model conditions on occupation, sector, and
     firm size, which are themselves downstream of occupational segregation,
     so this measures the residual gap *within the same job*, not sex/race's
     total effect. The dashboard's callout says this explicitly next to the
     chart so the panel can't be misread in isolation as "ML says race
     doesn't matter" — a real risk for a project going to a transparency body.
     The invisibility index (unconditional) and this SHAP panel (conditional)
     answer different questions; neither alone is "the explanation."
   - **Story-starter blurbs** (`story.py`) — auto-generated Portuguese paragraph
     per município, correctly caveats low-N municipalities (N<100) rather than
     presenting them with false confidence, aimed at the edital's "reportagens"
     reuse format.
   - **Downloadable CSVs** — `/download/<file>` with an explicit filename
     whitelist (verified: path-traversal attempt returns 404, not the file).
   - Accessible markup — real `<label for>`, SVG `role="img"` + `aria-label`,
     up/down state never conveyed by color alone (also labeled +/−R$).
   - Verified end-to-end: golden path (Rio de Janeiro), low-N edge case
     (Cardoso Moreira, correctly flagged), 404 on bad municipality code, CSS
     loads, download whitelist holds. Run locally: `cd src && python3 -c
     "from cgu_reuso.web.app import create_app; create_app().run(port=5050)"`
     (needs `flask` — installed in wage_gap's `.venv`, reused here rather than
     duplicating the pandas/numpy stack in a second venv).
3. **Admissibility-checklist pass** — re-read Edital articles 4º and 6º in full
   before submitting to confirm no formal requirement is missed (team registration,
   file formats, etc.) — not yet done.
4. **Reúso registration content — drafted (18/08).** `submission/reuso_submission_draft.md`
   — title, short/full description leading with the invisibility index and the
   Anexo I "Salário médio de empregados" match, dataset URL, and the live
   reúso URL below.
5. **Dashboard deployed (18/08).** Live at **https://louiseluli.github.io/cgu/**
   — GitHub Pages serving `docs/` on `main`, repo `louiseluli/cgu` (public).
   The Flask app is GET-only with no session state, so it's frozen to static
   HTML via `src/cgu_reuso/web/freeze.py` (one page per município, 92 total,
   using Flask's test client — no separate static-site generator needed) rather
   than run as a live server, which a free host wouldn't sustain reliably
   through the judging window anyway. The dropdown picker was replaced with a
   real link list for this — no JS dependency, still good practice even though
   Inclusividade turned out not to be its own scored criterion (§6, corrected
   19/08).
   **Process note:** `cgu` was not previously its own git repository — running
   git commands inside it resolved to `/Users/louisesfer`, a repo spanning
   unrelated projects with pending staged changes elsewhere. Initialized an
   independent nested repo scoped to `cgu/` instead of touching that; verified
   with `git rev-parse --show-toplevel` before committing anything.
6. **LICENSE file — added (19/08).** MIT, at repo root. Item 8.2's
   "Replicabilidade e escalabilidade" (weight 1, real criterion — §6)
   explicitly names "códigos abertos e licenças para replicação" as what it
   scores — the repo URL and license are now cited in both submission
   documents (§ below).
7. **Confirm eligibility, item 3.4 — needs your answer.** The 2026 edital bars
   "servidores em exercício na Controladoria-Geral da União" from
   participating, individually or as team members. Confirm this doesn't apply.

## 6. Judging-criteria mapping (edital 8.2)

**Rebuilt 19/08 from the actual 2026 edital text** (`EDITAL CGU Nº 46, DE 19
DE JUNHO DE 2026`, DOU Seção 3, pasted in full by the user and read directly
— not inferred from the 1st edition or the landing page summary, both of
which turned out to list a *different* 7-criterion table that doesn't match
this legally authoritative version). This replaces the previous version of
this table entirely.

Tie-break order on ties (item 8.6) is: benefício para a sociedade ou
economia > relevância e impacto > inovação e originalidade > apresentação e
usabilidade > replicabilidade e escalabilidade — i.e. the two weight-2
criteria decide close scores, same shape as before but different names.

| Critério | Peso | Edital wording (verbatim) | How this project addresses it |
|---|---|---|---|
| Relevância e impacto | 2 | "Dimensão e alcance do impacto potencialmente gerado pelo reúso." | Emphasize **scale**, not just depth: statewide coverage (92 municípios, millions of formal workers, 2010-2024), a tool any município or the state itself could use, methodology built to extend to all 27 states without structural changes |
| Benefício para a sociedade ou economia | 2 | "O reúso contribui para a melhoria de serviços ou políticas públicas, transparência, controle social, acesso a direitos, conhecimento ou inovação, economia digital ou para a geração benefícios à sociedade." | This is now the single criterion that absorbs what used to be two separate ones — lead with it. Per-município trend chart as a *policy-monitoring* tool (is a município's gap widening or narrowing — are local equal-pay efforts working); story-starter blurbs for "reportagens"; downloadable CSVs that re-feed the open-data ecosystem; the core finding itself is a transparency/accountability act |
| Apresentação e usabilidade | 1 | "O reúso apresenta dados de forma que desperte o interesse do usuário e facilita a compreensão dos dados." | Dashboard (Wage Gap Explorer) + plain-language narrative (§5.1) — same work as before, just now weight 1 not 2 |
| Inovação e originalidade | 1 | "uso de tecnologia ou conteúdo novo ou experiência original... ou permite ao usuário ter novas perspectivas ou obter novos conhecimentos." | Invisibility index (a genuinely new method, not just a new chart) + XGBoost/SHAP model (R²=0.734) — both fold "technology use" and "new perspective" into one criterion now |
| Replicabilidade e escalabilidade | 1 | "A iniciativa tem potencial para ser ampliada ou replicada; a iniciativa oferece **códigos abertos e licenças para replicação**." | **New criterion, concrete and checkable** — explicitly rewards open-source code plus an actual license, not just "the idea could scale" in the abstract. The public GitHub repo (`louiseluli/cgu`) is a direct match, but **needs a LICENSE file — doesn't have one yet (action item, §5)**. National-expansion framing (§3) also feeds this directly. |

**Gone as separately-scored criteria vs. the earlier (wrong) table:** "Uso
de 2+ fontes de dados abertos," "Uso de ferramentas tecnológicas," and
"Inclusividade" don't exist as their own line items in the real 2026 table.
The IBGE second-source work (§2) and accessible-markup work (§5.2) are still
good practice and still generally required by item 4.1.4's "utilização... de
dados públicos em formato aberto," just not separately weighted — don't
over-invest narrative space defending them as if they were.

## 7. Milestone plan (today: 18/08/2026, deadline: 11/09/2026)

**Correction (19/08):** the actual 2026 text (item 4.1.2, item 6.3) requires
the reúso be sent for homologação "**no período da inscrição**" — during the
registration window (29/06–11/09/2026) — not literally at the same moment as
Etapa 1, which is looser than the 1st-edition-based reading this plan had
until now. Doing both together in one sitting is still the practical default
(it's simple, and it's what the landing page's own procedural text
recommends), but there's more schedule flexibility than previously assumed
if something needs to slip a few days.

| Window | Work |
|---|---|
| 18–22/08 | ~~Compute invisibility index~~ done. Draft narrative findings writeup anchored on it (§1) |
| 22–29/08 | ~~Build dashboard~~ done (Wage Gap Explorer, SHAP panel, story-starter blurbs, downloadable CSVs, accessible markup — §5.2) |
| 29/08–03/09 | ~~Prepare Etapa 1 form content AND Etapa 2 reúso description~~ done — `submission/reuso_submission_draft.md`, live dashboard at https://louiseluli.github.io/cgu/. Add LICENSE file (§5.6). Get Portal Dados.Gov profile created/verified early |
| 03–05/09 | Submit both steps: fill Etapa 1 form, register + homologação-send the reúso on the Portal with the dataset URL(s) — same sitting, not strictly required to be the same minute |
| 05–11/09 | Buffer: confirm homologação email received, fix any admissibility gaps |

### Downstream contest dates (passive — no action needed yet)
- 25/09/2026 — resultado preliminar da admissibilidade
- 28/09–02/10/2026 — janela de recurso (admissibilidade)
- 12/10/2026 — resultado final das iniciativas admitidas
- 13/11/2026 — resultado preliminar do julgamento
- 16–20/11/2026 — janela de recurso (julgamento)
- 09/12/2026 — resultado final
- até 30/03/2027 — premiação

## 8. Admissibility checklist (rebuilt 19/08 — confirmed source)

**Sourcing:** `EDITAL CGU Nº 46, DE 19 DE JUNHO DE 2026`, published DOU
Seção 3, Nº 115, 23/06/2026, digitally signed (verifiable at
in.gov.br/autenticidade.html, código 05302026062300150) — pasted in full by
the user and read directly. This is the actual, current, legally
authoritative text. It supersedes both the earlier admissibility checklist
(built from the 1st edition as precedent, since automated fetch of this
document failed repeatedly) and the landing-page criteria summary, which
turned out not to match this document's item 8.2 (§6).

| # | Requirement (2026 edital, verbatim where quoted) | Status for this project |
|---|---|---|
| 3.1 | "pessoas físicas ou jurídicas, de direito público ou privado, nacionais ou estrangeiras" may participate | OK — much broader than the 1st edition's public-sector framing; individual citizens are squarely covered |
| 3.2 | Individual or team (até 20 participantes); no stated minimum team size | OK — submitting individually |
| 3.4 | Active CGU staff ("servidores em exercício na Controladoria-Geral da União") barred, individually or as team members | **Needs your confirmation** — not expected to apply, but this is a real disqualifier now stated for individuals specifically, not just judging-committee members as in the 1st edition |
| 4.1.1 | Registration form submitted within the deadline in the edital's Anexo | Pending — not yet submitted |
| 4.1.2 / 6.3 | Reúso registered on the Portal and sent for homologação **"no período da inscrição"** (during the registration window, not necessarily simultaneous with Etapa 1) | On track — see relaxed timing in §7 |
| 4.1.3 | Initiative promotes "acesso a direitos, transparência, controle social, melhoria de serviços ou políticas públicas, conhecimento ou inovação, economia digital ou benefícios à sociedade" | OK — broad, matches "Benefício para a sociedade ou economia" in §6; narrative should still name this explicitly rather than leave it implicit |
| 4.1.4 | "Utilização e identificação de dados públicos em formato aberto" | OK — RAIS + IBGE, both cited by exact URL (§2) |
| 4.2 | Initiatives that "promovam preconceito, discriminação, desinformação ou que atentem contra direitos e garantias legais" are barred | **Narrative care point, not a real risk** — the project *analyzes and exposes* discrimination; frame it unambiguously as measurement/accountability. Low actual risk, but worth one careful sentence |
| 4.3 | Initiatives that won top-3 in the **1st edition** cannot re-enter | N/A — new project, first submission |
| 6.6 | Same participant/team may submit multiple initiatives if "suficientemente distintas" | N/A — one submission planned |
| 8.6 / 8.7 | Tie-break order and final tiebreaker (earliest registration date) | Informational — register early within the window if this ever matters |
| — | IBGE secondary-source cataloging on dados.gov.br | **Resolved 19/08** — confirmed cataloged (§2) |
| — | LICENSE file for the "Replicabilidade e escalabilidade" criterion | **Open — action item §5.6** |
