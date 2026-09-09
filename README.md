# microverse
literaly a microverse

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

## Próximos passos possíveis (me diga a ordem que prefere)

- Sistema político real: tipos de governo, eleições, golpes, ditadores.
- Guerras entre clãs/facções (recursos, território, exércitos).
- Árvore de tecnologia (Idade da Pedra → Bronze → Ferro → ...) que
  desbloqueia novas profissões e muda a economia.
- Economia de recursos (comida, materiais) afetando fome/mortalidade.
- Eventos aleatórios maiores (pragas, secas, descobertas, cismas religiosos).
- Árvore genealógica visual (gráfica, não só texto) na página HTML.
- Um jeito mais fácil de visualizar a história (linha do tempo em HTML).

