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

**Themes targeted (per edital):** Indicadores sociais, Indicadores econômicos.
**Specific high-value dataset match (Anexo I, confirmed 18/08 from the 1st
edition's edital — see §8):** under tema "Indicadores econômicos," Anexo I
names "Salário médio de empregados" verbatim as a priority high-value dataset.
Per item 8.3, the "Foco nas pessoas e impacto para a sociedade" criterion
(weight 2) is scored *against this named list*, not a general impression — so
the reúso description and narrative should cite "Salário médio de empregados"
by name, not just the broader "Indicadores econômicos" theme label.

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
- `train_xgboost.py` + `explain_xgboost.py` — SHAP-based explainability, useful for
  the "Uso de ferramentas tecnológicas" criterion.
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
   real link list for this — no JS dependency, and arguably a better fit for
   the Inclusividade criterion's "menor acesso à tecnologia" wording than a
   JS-driven `<select>` would have been.
   **Process note:** `cgu` was not previously its own git repository — running
   git commands inside it resolved to `/Users/louisesfer`, a repo spanning
   unrelated projects with pending staged changes elsewhere. Initialized an
   independent nested repo scoped to `cgu/` instead of touching that; verified
   with `git rev-parse --show-toplevel` before committing anything.

## 6. Judging-criteria mapping (edital 8.2)

Descriptions below are the actual 8.2 wording from the 1st edition's edital
(confirmed 18/08 — see §8 for sourcing/caveat), richer than the landing-page
summary. Tie-break order on ties (item 8.7) is: transparência > foco nas
pessoas > inovação > apresentação > inclusividade > fontes > ferramentas —
i.e. the two criteria this project already leans on hardest are also what
decides close scores.

| Critério | Peso | Edital wording | How this project addresses it |
|---|---|---|---|
| Apresentação | 2 | "Reúsos que priorizem a apresentação dos dados de forma **gráfica e dinâmica**, seguindo os parâmetros de **usabilidade e acessibilidade**." | Dashboard (Wage Gap Explorer, dynamic per-município view) + plain-language narrative anchored on the invisibility index (§1, §5.1–5.2) |
| Inovação | 2 | "Reúsos que representem ideia, método ou objeto criado de forma **diversa de padrões anteriores**." | Intersectional-not-additive claim proven with a computed number (invisibility index) rather than asserted — a genuinely new method, not just a new chart; SHAP explainability |
| Fomento à transparência e controle social | 2 | "Reúsos que permitam **acompanhar, monitorar e avaliar políticas públicas** e as ações de Governo... solucionar problemas ou assegurar a manutenção dos serviços de atendimento ao cidadão." | Narrative must frame the per-município trend chart explicitly as a monitoring tool (does a município's gap widen/narrow year over year — i.e. are local equal-pay efforts working), not just a static finding. Story-starter blurbs (targets "reportagens" reuse format) + downloadable derived CSVs that re-feed the open-data ecosystem |
| Foco nas pessoas e impacto para a sociedade | 2 | Scored against Anexo I high-value datasets (item 8.3) — "Salário médio de empregados" under Indicadores econômicos is a direct, named match (§1). | Cite "Salário médio de empregados" by name, not just "Indicadores econômicos." Explorer makes the impact concrete and personal (pick your município, see your gap) |
| Uso de 2+ fontes de dados abertos | 1 | "Reúsos de dados construídos a partir de diferentes conjuntos de dados abertos." | RAIS + IBGE (IBGE cataloging still unconfirmed, §8) |
| Uso de ferramentas tecnológicas | 1 | "Reúsos que realizem utilização, criação e desenvolvimento de tecnologia." | XGBoost/SHAP modeling (R²=0.734 on 5.78M held-out rows, built and wired into the dashboard), interactive dashboard |
| Inclusividade | 1 | "Reúsos baseados em **solução acessível para diferentes públicos, especialmente aqueles com menor acesso à tecnologia**." | **Correction (18/08):** this criterion is about the *dashboard's* accessibility for low-tech-access users, not primarily about the subject matter being race/sex. Already well-served by the no-JS, server-rendered, semantic-HTML build — but the narrative description should say this explicitly rather than lean on "intersectional lens = inclusividade," which is a weaker match to the actual wording |

## 7. Milestone plan (today: 18/08/2026, deadline: 11/09/2026)

**Correction (18/08):** Etapa 1 and Etapa 2 are not sequential with slack
between them — item 4.1.2 requires the reúso be registered and sent for
homologação on the Portal *at the moment of* Etapa 1 registration, and the
2026 landing page independently confirms this ("envie o formulário e avance
**imediatamente** para a Etapa 2"). Both must be submission-ready
simultaneously; plan accordingly rather than treating Etapa 2 as a follow-up
task with its own week.

| Window | Work |
|---|---|
| 18–22/08 | ~~Compute invisibility index~~ done. Draft narrative findings writeup anchored on it (§1) |
| 22–29/08 | ~~Build dashboard~~ done (Wage Gap Explorer, SHAP panel, story-starter blurbs, downloadable CSVs, accessible markup — §5.2) |
| 29/08–03/09 | ~~Prepare Etapa 1 form content AND Etapa 2 reúso description~~ done — `submission/reuso_submission_draft.md`, live dashboard at https://louiseluli.github.io/cgu/. Get Portal Dados.Gov profile created/verified early so nothing blocks the simultaneous submit |
| 03–05/09 | Submit both steps together: fill Etapa 1 form, then immediately register + homologação-send the reúso on the Portal with the dataset URL(s) |
| 05–11/09 | Buffer: confirm homologação email received, fix any admissibility gaps, re-verify the 2nd edition's actual PDF once reachable (§8) |

### Downstream contest dates (passive — no action needed yet)
- 25/09/2026 — resultado preliminar da admissibilidade
- 28/09–02/10/2026 — janela de recurso (admissibilidade)
- 12/10/2026 — resultado final das iniciativas admitidas
- 13/11/2026 — resultado preliminar do julgamento
- 16–20/11/2026 — janela de recurso (julgamento)
- 09/12/2026 — resultado final
- até 30/03/2027 — premiação

## 8. Admissibility checklist (18/08)

**Sourcing note:** the 2nd edition's own edital PDF is hosted on
`in.gov.br`/DOU, which failed to fetch on repeated attempts (connection reset
— likely blocks automated fetches), and `web.archive.org` is blocked in this
environment. What follows is read directly from the **1st edition's** edital
PDF (`EDITAL CGU Nº 21, DE 10 DE ABRIL DE 2025`, gov.br-hosted, successfully
fetched and read page-by-page). The judging-criteria table matches the 2026
landing page exactly (same 7 criteria, same weights), and the "advance
immediately to Etapa 2" instruction is independently confirmed on the 2026
page too — strong precedent, but item numbers/wording could shift between
editions. **Before final submission, get the actual 2026 PDF** (try
downloading it manually via browser from the "Confira aqui o edital" link
on the landing page, since it renders fine in a browser even though automated
fetch fails) and diff against this checklist.

| # | Requirement (1st-edition wording) | Status for this project |
|---|---|---|
| 3.4 | Individual citizens without institutional bond may participate | OK — no team required |
| 3.6 | If submitting as a team, 2–20 people | N/A unless submitting as a team |
| 4.1.1 | Registration form submitted within the deadline window | Pending — not yet submitted |
| 4.1.2 | Reúso registered + sent for homologação on the Portal **at the moment of** Etapa 1 registration | **Process risk, now fixed in §7** — do both simultaneously, not sequentially |
| 4.1.3 | Initiative aligned with transparency/social-control/public-policy/societal-benefit principles | OK, but narrative must explicitly frame the trend data as *policy-monitoring* capability (see §6, Fomento à transparência) — don't leave this implicit |
| 4.1.4 | Uses open data from a Portal-registered org or that org's own platform, in open format | OK — RAIS/MTE confirmed cataloged (§2) |
| 4.2 / 15.6 | Off-theme, "viés preconceituoso ou discriminatório," plagiarism, fraud, or non-conforming submissions are disqualified | **Narrative care point, not a real risk**: the project *analyzes and exposes* discrimination — frame it unambiguously as measurement/accountability, not content that could be misread as carrying the bias itself. Low actual risk (Inclusividade is an explicit judged criterion, so equity-focused subject matter is clearly welcomed), but worth one careful sentence in the writeup |
| 15.8 | Comissão Julgadora / Comitê Gestor members and relatives (to 3rd degree) barred from participating | Confirm no conflict — not expected to apply |
| 13.7 | Cannot appeal against the 8.2 criteria themselves, only the process | Informational |
| — | IBGE secondary-source cataloging on dados.gov.br | **Resolved 19/08** — confirmed cataloged (§2), no longer a risk |
