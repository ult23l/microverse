# Microverso — Ano 1

Base do motor de simulação da sua sociedade. Ainda simples de propósito —
vamos evoluindo o código aos poucos.

## Arquivos

- `dados_geracao.py` — listas/tabelas usadas para sortear nomes (gerados por
  sílabas, não uma lista fixa, pra nunca "acabarem"), clãs, profissões,
  traços de personalidade, tipos de humor, gostos e objetivos de vida.
- `modelos.py` — a classe `Criatura`, com todos os atributos de cada
  habitante (personalidade, humor, emoções, profissão, gostos, objetivos,
  saúde, relações familiares).
- `mundo.py` — a classe `Mundo`, que é o motor: gera a população fundadora,
  controla o ano atual, a história (log de eventos) e o método
  `avancar_ano()` (nascimentos, mortes, casamentos, deriva emocional,
  sucessão de liderança).
- `main.py` — roda a fundação (Ano 1) e imprime um resumo.
- `dados/estado_microverso.json` — o estado salvo da simulação (toda a
  população, ano atual, história etc).

## Como rodar

```
python3 main.py
```

Isso sempre gera uma fundação **nova** (Ano 1). Para continuar de onde
parou, use no lugar:

```python
from mundo import Mundo
m = Mundo.carregar("dados/estado_microverso.json")
eventos = m.avancar_ano()
print(eventos)
m.salvar("dados/estado_microverso.json")
```

## O que já existe

- 100 fundadores (50 homens/50 mulheres), cada um com: nome + clã, idade,
  personalidade (8 traços), tipo de humor, emoções atuais (5), profissão,
  3 gostos, 1-2 objetivos de vida, saúde, e relações.
- **Sistema de relacionamento em estágios**: solteiro(a) → namorando →
  casado(a) (ou viúvo(a) se o parceiro morrer). A compatibilidade entre
  duas pessoas (`calcular_compatibilidade` em `mundo.py`) combina
  personalidade parecida + gostos em comum + um fator de sorte/química.
  Cada ano, solteiros(as) podem tentar paquerar (mais chance quanto mais
  extrovertido(a)), namoros podem terminar ou virar casamento depois de
  2+ anos juntos, e casais fundadores já nascem pareados por compatibilidade.
- **Reprodução ligada ao casamento**: só casais com estado_civil="casado(a)"
  têm chance de filhos (antes era baseado em um campo solto de cônjuge).
- **Genealogia**: `pais_ids` (pai, mãe) em cada criatura + `mundo.genealogia(id)`
  e `mundo.imprimir_genealogia(id)` para ver pais, avós e descendentes de
  qualquer pessoa.
- Um líder eleito por ambição/extroversão/coragem, com sucessão automática.
- 14 clãs fundadores — já pensando em política/facções futuras.
- **Mapa com biomas**: floresta (árvores geradas proceduralmente), campos
  com sulcos de plantio, rio serpenteando, montanhas com relevo (cordilheira
  dupla + picos nevados) e uma clareira central com casinhas de verdade
  (oficina, cabana da cura, círculo espiritual, aldeia) em vez de manchas
  de cor lisas.

## Testado

Rodei 12 anos seguidos sem erros: paqueras, namoros, casamentos, términos,
nascimentos (só entre casados), mortes, viuvez, sucessão de liderança e a
genealogia de recém-nascidos e descendentes — tudo consistente.

## Visualização (vila_visual.html)

Abra `vila_visual.html` direto no navegador (duplo clique) pra ver a vila:
cada pessoa viva aparece como um pontinho na zona onde trabalha (floresta,
campos, rio, oficina, posto de vigia, cabana da cura, círculo espiritual,
centro da aldeia), balançando devagar. Clique num ponto pra ver a ficha
completa. O líder tem um anel dourado.

Sempre que avançar anos e salvar um novo `estado_microverso.json`, use o
botão "Carregar novo estado (.json)" no topo da página pra atualizar a
vila sem precisar gerar o arquivo de novo. Ou rode `python3 gerar_visual.py`
pra gerar uma nova versão do HTML já com os dados atuais embutidos.

## Economia e sobrevivência (novo)

Cada ano, a tribo produz e consome de verdade:

- **Comida**: produzida por Agricultores, Caçadores, Coletores e Pescadores
  (cada profissão rende uma quantidade diferente). Consumida por todo mundo
  (adultos consomem mais que crianças).
- **Materiais**: produzidos por Artesãos e Construtores, consumidos aos
  poucos pela manutenção/crescimento da aldeia.
- **Clima**: todo ano tem uma chance de ser normal, de fartura (+40% na
  colheita) ou de seca (-40%) — isso já aparece na crônica.
- **Fome de verdade**: se a comida zera, a mortalidade sobe (principalmente
  crianças e idosos), a felicidade cai, o estresse sobe, os nascimentos
  ficam mais raros, e pode rolar briga interna por comida.
- Quando alguém completa 16 anos e ainda não tem profissão, o motor já
  atribui uma automaticamente (antes isso não acontecia e a economia ia
  entrar em colapso conforme a geração fundadora fosse morrendo).
- `mundo.historico_recursos[ano]` guarda comida/materiais/clima/fome de
  cada ano — é o que alimenta o gráfico de recursos.

Balanceei os números pra fome ser um evento real (principalmente em anos
de seca seguidos), não um estado permanente — testei 25 anos e a população
cresceu de forma sustentável (100 → 135) com secas e farturas aparecendo
sem quebrar a sociedade.

## Vida social e memória dos NPCs (novo)

Cada criatura agora tem:

- **Memória** (`memorias`): lista das últimas ~20 coisas marcantes que
  aconteceram com ela ou que ela ouviu falar (nascimentos, mortes de
  parentes, casamentos, amizades/rivalidades fortes, virada de líder,
  fofoca) — cada entrada guarda ano, tipo, sobre quem, e se foi ouvida de
  segunda mão (`boato`).
- **Relações sociais** (`relacoes_sociais`): não é só romance — todo mundo
  tem um nível de confiança (0-100) com quem já cruzou. Confiança alta vira
  "amigo(a)", confiança baixa vira "rival".
- **Reputação** (`reputacao`): o que a comunidade pensa de alguém, sobe e
  desce com a fofoca boa/ruim que se espalha sobre a pessoa, e puxa de
  volta pro neutro aos poucos (fofoca velha perde força). Isso agora **pesa
  na eleição de líder** — ambição sozinha não basta mais, fama ruim atrapalha.
- **Encontros sociais**: todo ano, uma fração da população se encontra
  (com viés pro próprio clã/profissão — colegas de trabalho se veem mais).
  A compatibilidade de personalidade decide se a relação melhora ou piora.
- **Fofoca se espalha e se distorce**: quem participa de um encontro tem
  chance de repassar uma fofoca que sabe sobre um terceiro — e 25% de
  chance de distorcer (positivo virar negativo ou vice-versa) ao repassar.

Testei 20 anos: reputação variando de verdade entre as pessoas (não fica
todo mundo em 50), fofoca se espalhando (180+ memórias marcadas como
"ouviu dizer" numa população de 150), e memórias pessoais tristes/felizes
acumulando (ex: alguém que perdeu 3 filhos guarda isso na memória).

Use `mundo.imprimir_memorias(id)` pra ver as últimas memórias de qualquer
pessoa. Na ficha do mapa (`vila_visual.html`) agora também aparece
reputação, melhor amigo(a), maior rival e as memórias recentes de cada um.
vila sem precisar gerar o arquivo de novo. Ou rode `python3 gerar_visual.py`
pra gerar uma nova versão do HTML já com os dados atuais embutidos.

