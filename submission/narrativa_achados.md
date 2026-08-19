# O Salário Invisível: como raça e gênero se combinam — e nem sempre se somam — na desigualdade salarial do Rio de Janeiro

*Interseccionalidade Salarial — 2º Concurso de Reúso de Dados Abertos da CGU*

## O número que resume tudo

Em Tanguá, no Rio de Janeiro, uma mulher negra ganha, em média, R$602 a menos
por mês do que um homem branco com o mesmo tipo de trabalho. Se você
calculasse esse número apenas somando "quanto as mulheres ganham a menos que
os homens" com "quanto trabalhadores negros ganham a menos que brancos" —
como normalmente se faz —, chegaria a R$290. A diferença real é **52% maior**
do que essa soma simples prevê.

Em Quissamã, acontece o oposto: a diferença real (R$804) é **40% menor** do
que a soma simples (R$1.125) sugeriria.

Nenhum desses dois números aparece se você olhar só para o gênero, só para a
raça, ou só para a média do estado inteiro. Eles só aparecem quando se olha
para a interseção — e é exatamente isso que este projeto faz, usando dados
públicos da RAIS (Relação Anual de Informações Sociais), o principal
registro de empregos formais do Brasil.

## O que descobrimos

### 1. A desigualdade não é uma simples soma

A hipótese mais comum sobre desigualdade interseccional é que os efeitos "se
empilham": se ser mulher custa X e ser negro custa Y, ser mulher negra
custaria X+Y. Testamos essa hipótese diretamente, comparando o gap real
entre homens brancos e mulheres negras com a soma dos gaps de gênero e de
raça calculados separadamente, para cada um dos 92 municípios do Rio de
Janeiro, todos os anos entre 2010 e 2024.

Na média estadual, a hipótese da soma simples se sustenta razoavelmente bem
— o gap real de 2024 (R$2.622) é próximo da soma prevista (R$2.710). **Mas
essa média esconde uma variação real e substancial entre municípios**: entre
as 81 cidades com amostra grande o suficiente para uma comparação confiável,
o gap real varia de 39,0% abaixo a 39,7% acima do que a soma simples prevê
— quase 79 pontos percentuais entre os extremos, invisível em qualquer
leitura estadual ou de eixo único.

Essa heterogeneidade municipal — não uma regra única e universal — é o
achado central deste projeto.

### 2. Não é um fenômeno de baixa escolaridade

Uma leitura comum sobre desigualdade salarial é que ela reflete diferenças
de qualificação — se resolvida a educação, o problema desapareceria.
Testamos isso também: comparamos o gap entre homens brancos e mulheres
negras como proporção do salário do homem branco, em cada faixa de
escolaridade.

O gap não diminui com a escolaridade. Ele cresce. Nos níveis mais baixos de
escolaridade, mulheres negras ganham cerca de 31% a 34% a menos que homens
brancos. Entre pessoas com ensino superior completo, essa diferença sobe
para **54%** — e para 51% entre mestres. A desigualdade salarial
interseccional no Rio de Janeiro é, proporcionalmente, maior entre
trabalhadoras negras com diploma universitário do que entre trabalhadoras
negras sem ele.

### 3. A diferença está aumentando, não diminuindo

No município do Rio de Janeiro, o gap salarial real entre homens brancos e
mulheres negras cresceu de R$1.993 em 2014 para R$3.643 em 2024 — um
aumento de R$1.650 em dez anos, mesmo descontando os anos em que a RAIS não
disponibilizou dados completos (2017, 2019 e 2020).

### 4. Um modelo de aprendizado de máquina confirma — e complica — a história

Treinamos um modelo (XGBoost) sobre os 5,78 milhões de vínculos formais do
Rio de Janeiro em 2024, para prever o salário a partir de nove
características: ocupação, tempo de emprego, escolaridade, porte da
empresa, setor, idade, carga horária, sexo e raça. O modelo explica 73% da
variação salarial observada.

Sexo e raça aparecem como as duas características de menor peso direto
nesse modelo — o oitavo e o nono lugar entre dez, respectivamente. À
primeira vista, isso poderia parecer uma contradição com os achados acima.
Não é. O modelo prevê o salário *dado* o cargo, o setor e o porte da
empresa de cada pessoa — e a ocupação, sozinha, responde por 25% da
importância total. Mas a ocupação não é um fator neutro: quem consegue
entrar em quais cargos, setores e empresas é, em si, um dos principais
mecanismos pelos quais o racismo e o machismo operam no mercado de
trabalho. Um modelo condicionado nessas variáveis mede o gap *residual
dentro do mesmo cargo* — não o efeito total de sexo e raça, que é
exatamente o que os achados 1 a 3 estão medindo, sem essa condição. As duas
análises respondem perguntas diferentes; nenhuma invalida a outra, e
nenhuma delas, isoladamente, deve ser lida como "a explicação completa" da
desigualdade salarial.

## Por que isso importa

Políticas de equidade salarial — sejam elas federais, estaduais ou
municipais — costumam ser desenhadas e avaliadas com base em médias
agregadas ou em recortes de um único eixo (só gênero, ou só raça). Se o
efeito real da desigualdade é heterogêneo no território e não-aditivo entre
eixos, como este projeto mostra, essas políticas podem estar mirando no
lugar errado: tratando como uniforme um problema que se concentra, de forma
desproporcional, em municípios específicos.

O **Explorador da Desigualdade Salarial**, painel interativo que acompanha
este reúso, permite consultar esse número para qualquer um dos 92
municípios do Rio de Janeiro, junto com sua série histórica 2010–2024 — uma
ferramenta pensada para jornalistas, gestores públicos e cidadãos
acompanharem, ano a ano, se o problema está piorando ou melhorando onde
vivem.

**Painel:** https://louiseluli.github.io/cgu/
**Dados completos para download:** município por município, série estadual,
e a tabela de importância de variáveis do modelo, todos disponíveis
diretamente no painel.

## Metodologia, em uma frase

Todos os números acima vêm de dados reais da RAIS, agregados e verificados
— incluindo verificação cruzada contra tabelas calculadas de forma
independente (concordância a 13 casas decimais) e testes de sensibilidade
sobre escolhas metodológicas. A auditoria completa de qualidade dos dados,
incluindo dois problemas metodológicos identificados e corrigidos durante o
processo, está documentada em `outputs/tables/eda/eda_briefing.md` no
repositório do projeto, e em versão navegável em:
https://claude.ai/code/artifact/9260c7cd-08de-4063-89bf-70d33e3980f8

## Escopo e próximos passos

Esta análise cobre o Rio de Janeiro. A metodologia — o índice de
invisibilidade, o modelo XGBoost/SHAP, o painel — foi construída para ser
replicável nacionalmente sem alterações estruturais; a expansão para os 27
estados é um passo natural de continuidade, não realizado nesta submissão
por restrição de prazo.

## Fontes de dados

- RAIS (Relação Anual de Informações Sociais), Ministério do Trabalho e
  Emprego: https://dados.gov.br/dataset/relacao-anual-de-informacoes-sociais-rais
- Malha geométrica dos municípios brasileiros, IBGE (usada nos agrupamentos
  territoriais — mesorregião/microrregião):
  https://dados.gov.br/dataset/malha-geometrica-dos-municipios-brasileiros

Ambas catalogadas no Portal Brasileiro de Dados Abertos.
