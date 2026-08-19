# Etapa 2 — Rascunho para submissão de reúso no Portal Dados.Gov

> Preencher no fluxo "Enviar para homologação" do Portal Brasileiro de Dados
> Abertos. Este rascunho cobre o conteúdo textual; os campos exatos do
> formulário (título, descrição, tipo, URLs) podem variar ligeiramente —
> adaptar conforme necessário, mas manter as menções específicas abaixo, que
> foram calibradas para os critérios de julgamento do item 8.2 do edital.

## Título da iniciativa

Explorador da Desigualdade Salarial Interseccional — Rio de Janeiro

## Tipo de reúso

Painel / dashboard interativo

## URL do reúso

https://louiseluli.github.io/cgu/

## Conjunto(s) de dados utilizado(s)

- **RAIS (Relação Anual de Informações Sociais)** — Ministério do Trabalho e
  Emprego. https://dados.gov.br/dataset/relacao-anual-de-informacoes-sociais-rais
  (catalogado no Portal Brasileiro de Dados Abertos — satisfaz o requisito
  obrigatório do item 4.1.4)
- **Malha geométrica dos municípios brasileiros** — IBGE.
  https://dados.gov.br/dataset/malha-geometrica-dos-municipios-brasileiros
  (usada nos agrupamentos territoriais — mesorregião/microrregião — presentes
  em todas as tabelas do painel; satisfaz o item 4.1.4 do edital, "utilização
  e identificação de dados públicos em formato aberto")

## Temas

Indicadores econômicos (especificamente: salário médio de empregados),
Indicadores sociais.

## Descrição curta (para listagem)

Um modelo XGBoost e um índice interseccional original mostram que a
diferença salarial entre homens brancos e mulheres negras no Rio de Janeiro
não é a soma simples do efeito de gênero com o efeito de raça — em
municípios específicos, o efeito real chega a ser 52% maior do que essa
soma prevê, um padrão invisível em qualquer leitura de eixo único.

## Descrição completa

Este reúso constrói, a partir da RAIS (2010–2024, Rio de Janeiro), um
**índice de invisibilidade**: a diferença entre o gap salarial real
observado entre homens brancos e mulheres negras e o que se preveria apenas
somando o gap médio de gênero ao gap médio de raça, calculados
separadamente. Esse número, inédito nesta forma, mostra que a média
estadual está próxima do previsto pela soma simples (-3,3% em 2024) — mas
essa média esconde uma variação real e relevante entre municípios: em
Tanguá, o gap real chega a ser 52% maior do que a soma simples prevê;
em Magé, 40% maior; em Porto Real, 10% maior. Em outros municípios — como
Quissamã, 40% menor —, o efeito vai na direção oposta. Essa heterogeneidade
municipal é o achado central do projeto e é completamente invisível tanto
em uma leitura estadual agregada quanto em qualquer análise de eixo único
(só gênero, ou só raça).

O projeto também treina um modelo XGBoost sobre o painel completo de 2024
(5.775.860 vínculos formais, R²=0,734 em dados de teste) e usa SHAP para
decompor quais características mais influenciam o salário previsto —
ocupação, tempo de emprego e escolaridade lideram, com sexo e raça
aparecendo como os fatores de menor peso direto quando se condiciona nessas
variáveis. O painel explica explicitamente por que isso não contradiz o
índice de invisibilidade: ocupação e porte do estabelecimento são, eles
mesmos, canais pelos quais a segregação ocupacional opera, então o modelo
mede o gap residual dentro do mesmo cargo, não o efeito total de sexo e
raça.

O **Explorador da Desigualdade Salarial** (painel web, https://louiseluli.github.io/cgu/)
permite consultar, para cada um dos 92 municípios do Rio de Janeiro, o gap
real, o índice de invisibilidade, e uma série histórica 2010–2024, além de
um parágrafo-resumo citável (voltado ao uso jornalístico) e as tabelas
completas para download. A série temporal por município funciona como
ferramenta de monitoramento — permite acompanhar, ano a ano, se o gap local
está aumentando ou diminuindo, apoiando o controle social sobre políticas
municipais de equidade salarial.

Todo o código é aberto e está publicado em
https://github.com/louiseluli/cgu — os scripts de construção do índice de
invisibilidade e do modelo XGBoost/SHAP, o próprio painel, e a auditoria de
qualidade de dados. A metodologia foi desenhada para ser replicada em
qualquer estado brasileiro sem alterações estruturais: o mesmo pipeline que
processa o Rio de Janeiro processaria os demais 26 estados, bastando
substituir o recorte geográfico de entrada.

Metodologia documentada com auditoria própria de qualidade de dados,
verificação cruzada contra tabelas independentes do projeto de origem
(concordância a 1e-13) e testes de sensibilidade sobre escolhas
metodológicas — disponível em `outputs/tables/eda/eda_briefing.md` no
repositório do projeto.

## Organização responsável

Individual (participante sem vínculo institucional, conforme item 3.4 do
edital).

## Checklist antes de enviar

- [ ] Confirmar que https://louiseluli.github.io/cgu/ está no ar (build do
      GitHub Pages concluído)
- [ ] Preencher o formulário de inscrição da Etapa 1 (Anexo II) e enviar este
      reúso para homologação **no mesmo momento**, conforme item 4.1.2
- [ ] Selecionar "Enviar para homologação" no Portal
- [ ] Guardar o e-mail de confirmação de homologação
