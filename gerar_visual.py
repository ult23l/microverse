"""
gerar_visual.py
Gera um arquivo HTML autocontido (vila_visual.html) que mostra o terreno
do microverso (floresta, campos, rio, montanhas com relevo, clareira da
aldeia) e cada habitante vivo como um pontinho na zona onde trabalha, com
uma ficha completa ao clicar (incluindo pai, mãe, parceiro(a) e filhos).

Rode de novo sempre que quiser atualizar a imagem com o ano mais recente:

    python3 gerar_visual.py

O HTML gerado também tem um botão para carregar um novo
estado_microverso.json na hora, direto no navegador, sem precisar rodar
este script de novo (o terreno é decorativo e fixo; só as pessoas mudam).
"""

import json
import os
import random

CAMINHO_ESTADO = os.path.join(os.path.dirname(__file__), "dados", "estado_microverso.json")
CAMINHO_SAIDA = os.path.join(os.path.dirname(__file__), "vila_visual.html")


# ---------------------------------------------------------------------------
# Geração do terreno decorativo (árvores da floresta e construções da aldeia)
# Isso roda uma vez em Python e vira SVG estático embutido no HTML — não
# depende dos dados da simulação, só da paisagem.
# ---------------------------------------------------------------------------

def gerar_arvores_svg(n=48):
    cores = ["var(--cor-floresta-1)", "var(--cor-floresta-2)", "var(--cor-floresta-3)"]
    partes = []
    for _ in range(n):
        x = random.uniform(20, 295)
        y = random.uniform(55, 425)
        escala = 0.55 + (y - 55) / (425 - 55) * 0.7
        largura = 22 * escala
        altura = 34 * escala
        cor = random.choice(cores)
        partes.append(
            f'<g transform="translate({x:.1f},{y:.1f})">'
            f'<rect x="{-largura*0.08:.1f}" y="{altura*0.15:.1f}" width="{largura*0.16:.1f}" height="{altura*0.35:.1f}" fill="var(--cor-tronco)"/>'
            f'<polygon points="0,{-altura*0.55:.1f} {largura/2:.1f},{altura*0.22:.1f} {-largura/2:.1f},{altura*0.22:.1f}" fill="{cor}"/>'
            f'<polygon points="0,{-altura*0.32:.1f} {largura*0.38:.1f},{altura*0.05:.1f} {-largura*0.38:.1f},{altura*0.05:.1f}" fill="{cor}" opacity="0.9"/>'
            f'</g>'
        )
    return "".join(partes)


def _casa(cx, cy, escala, cor_parede, cor_telhado):
    w, h = 46 * escala, 30 * escala
    rw = w * 0.62
    return (
        f'<g transform="translate({cx:.1f},{cy:.1f})">'
        f'<rect x="{-rw/2:.1f}" y="{-h*0.1:.1f}" width="{rw:.1f}" height="{h*0.55:.1f}" fill="{cor_parede}"/>'
        f'<polygon points="{-w/2:.1f},{-h*0.1:.1f} {w/2:.1f},{-h*0.1:.1f} 0,{-h*0.85:.1f}" fill="{cor_telhado}"/>'
        f'</g>'
    )


def _torre(cx, cy, escala=1.0):
    w, h = 15 * escala, 68 * escala
    return (
        f'<g transform="translate({cx:.1f},{cy:.1f})">'
        f'<rect x="{-w/2:.1f}" y="{-h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="var(--cor-tronco)"/>'
        f'<rect x="{-w*0.9:.1f}" y="{-h-7:.1f}" width="{w*1.8:.1f}" height="9" fill="#3A2E1D"/>'
        f'</g>'
    )


def gerar_construcoes_svg():
    partes = [
        _casa(490, 385, 1.0, "var(--cor-parede)", "var(--cor-aldeia)"),
        _casa(548, 392, 0.85, "var(--cor-parede)", "var(--cor-aldeia)"),
        _casa(400, 430, 1.0, "var(--cor-parede)", "var(--cor-oficina)"),
        _casa(600, 325, 1.0, "var(--cor-parede)", "var(--cor-cura)"),
        _casa(510, 262, 0.9, "var(--cor-parede)", "var(--cor-espiritual)"),
        _torre(828, 192, 1.0),
    ]
    return "".join(partes)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Microverso — Vila Viva</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@500;700&family=Nunito+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --cor-fundo: #1E1B16;
    --cor-painel: #2A241C;
    --cor-texto: #EDE3D0;
    --cor-texto-fraco: #B8AA92;
    --cor-fogo: #E8722C;
    --cor-homem: #6FA8D8;
    --cor-mulher: #E0899C;

    --cor-montanha-longe: #7D8B94;
    --cor-montanha-perto: #8B8378;
    --cor-neve: #E8E4DC;
    --cor-floresta-1: #3E4F28;
    --cor-floresta-2: #4B5D34;
    --cor-floresta-3: #56693D;
    --cor-tronco: #4A3B26;
    --cor-campo: #A98A4B;
    --cor-campo-linha: #8B6F35;
    --cor-agua: #3E7C7C;
    --cor-agua-clara: #6FB8B8;
    --cor-clareira: #9B7C52;
    --cor-parede: #C9A876;
    --cor-aldeia: #8B6B47;
    --cor-oficina: #6E5A44;
    --cor-vigia: #705838;
    --cor-cura: #5F7A5A;
    --cor-espiritual: #6B5580;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--cor-fundo);
    color: var(--cor-texto);
    font-family: 'Nunito Sans', system-ui, sans-serif;
  }
  h1, h2 { font-family: 'Bitter', Georgia, serif; }

  header {
    padding: 18px 24px 12px;
    border-bottom: 1px solid #3A3226;
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: 10px;
  }
  header h1 { margin: 0; font-size: 1.4rem; font-weight: 700; letter-spacing: 0.3px; }
  header .stats { color: var(--cor-texto-fraco); font-size: 0.92rem; }
  header .stats b { color: var(--cor-texto); }

  .carregar { font-size: 0.82rem; color: var(--cor-texto-fraco); }
  .carregar label {
    cursor: pointer;
    border: 1px solid #4A4030;
    padding: 5px 10px;
    border-radius: 5px;
    display: inline-block;
  }
  .carregar label:hover { border-color: var(--cor-fogo); color: var(--cor-texto); }
  .carregar input { display: none; }

  main {
    display: flex;
    flex-wrap: wrap;
    gap: 18px;
    padding: 18px;
    align-items: flex-start;
  }

  #mapa-container {
    position: relative;
    width: 100%;
    max-width: 900px;
    aspect-ratio: 16 / 10;
    background: #14120E;
    border-radius: 10px;
    overflow: hidden;
    flex: 1 1 560px;
    border: 1px solid #3A3226;
  }
  #mapa-container svg#terreno { position: absolute; inset: 0; width: 100%; height: 100%; }

  .rotulo-zona {
    position: absolute;
    font-size: 0.72rem;
    color: var(--cor-texto);
    background: rgba(20, 18, 14, 0.55);
    padding: 2px 7px;
    border-radius: 4px;
    pointer-events: none;
    white-space: nowrap;
  }

  .fogueira {
    position: absolute;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: radial-gradient(circle, #FFD27A 0%, var(--cor-fogo) 60%, transparent 100%);
    box-shadow: 0 0 14px 6px rgba(232, 114, 44, 0.5);
    animation: tremular 2.2s ease-in-out infinite alternate;
  }
  @keyframes tremular {
    from { transform: scale(0.9); opacity: 0.85; }
    to   { transform: scale(1.15); opacity: 1; }
  }

  .ponto {
    position: absolute;
    border-radius: 50%;
    cursor: pointer;
    border: 1.5px solid rgba(0,0,0,0.35);
    transform: translate(-50%, -50%);
    animation: flutuar 4s ease-in-out infinite;
    transition: box-shadow 0.15s;
  }
  .ponto:hover, .ponto.selecionado {
    box-shadow: 0 0 0 3px rgba(255,255,255,0.55);
    z-index: 5;
  }
  .ponto.lider {
    box-shadow: 0 0 0 3px #FFD27A, 0 0 10px 2px rgba(255, 210, 122, 0.7);
  }

  @keyframes flutuar {
    0%   { margin-left: 0px; margin-top: 0px; }
    25%  { margin-left: 2px; margin-top: -2px; }
    50%  { margin-left: -2px; margin-top: 1px; }
    75%  { margin-left: 1px; margin-top: 2px; }
    100% { margin-left: 0px; margin-top: 0px; }
  }

  #painel {
    flex: 1 1 260px;
    max-width: 340px;
    background: var(--cor-painel);
    border: 1px solid #3A3226;
    border-radius: 10px;
    padding: 16px 18px;
    min-height: 200px;
  }
  #painel h2 { margin: 0 0 4px; font-size: 1.15rem; }
  #painel .sub { color: var(--cor-texto-fraco); font-size: 0.85rem; margin-bottom: 12px; }
  #painel .linha { margin: 7px 0; font-size: 0.88rem; line-height: 1.4; }
  #painel .linha b { color: var(--cor-texto-fraco); font-weight: 600; display: inline-block; min-width: 108px; }
  #painel .vazio { color: var(--cor-texto-fraco); font-size: 0.9rem; }
  #painel .barra-bg { background: #1E1B16; border-radius: 3px; height: 6px; overflow: hidden; margin-top: 3px; }
  #painel .barra-fg { background: var(--cor-fogo); height: 100%; }

  #legenda {
    padding: 0 18px 18px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px 18px;
    font-size: 0.8rem;
    color: var(--cor-texto-fraco);
  }
  #legenda span.dot { display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:5px; vertical-align:middle; }
</style>
</head>
<body>

<header>
  <div>
    <h1>Microverso — Vila Viva</h1>
    <div class="stats" id="stats-header">carregando...</div>
  </div>
  <div class="carregar">
    <label>Carregar novo estado (.json)
      <input type="file" id="input-arquivo" accept="application/json">
    </label>
  </div>
</header>

<main>
  <div id="mapa-container">
    <svg id="terreno" viewBox="0 0 1000 625" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="0" y="0" width="1000" height="625" fill="#2B2A1F"/>

      <!-- campos -->
      <path d="M15,450 Q120,432 250,450 T430,460 L430,600 L15,600 Z" fill="var(--cor-campo)"/>
      <g stroke="var(--cor-campo-linha)" stroke-width="3" opacity="0.5" fill="none">
        <path d="M30,480 Q200,470 420,485"/>
        <path d="M25,510 Q200,500 425,515"/>
        <path d="M25,540 Q200,532 425,545"/>
        <path d="M25,570 Q200,562 425,575"/>
      </g>

      <!-- floresta (árvores geradas em Python) -->
      <g id="floresta-grupo">__ARVORES_SVG__</g>

      <!-- rio -->
      <path d="M860,235 L790,320 L820,420 L740,500 L680,600" fill="none" stroke="var(--cor-agua)" stroke-width="34" stroke-linecap="round" stroke-linejoin="round" opacity="0.92"/>
      <path d="M860,235 L790,320 L820,420 L740,500 L680,600" fill="none" stroke="var(--cor-agua-clara)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" opacity="0.5"/>

      <!-- clareira da aldeia -->
      <ellipse cx="500" cy="380" rx="165" ry="120" fill="var(--cor-clareira)" opacity="0.9"/>

      <!-- montanhas -->
      <polygon points="680,260 720,160 760,200 800,110 840,190 880,140 920,210 960,160 1000,230 1000,260" fill="var(--cor-montanha-longe)" opacity="0.55"/>
      <polygon points="700,260 740,120 770,180 810,60 850,150 880,90 920,170 960,110 1000,200 1000,260" fill="var(--cor-montanha-perto)"/>
      <polygon points="792,82 810,60 826,86" fill="var(--cor-neve)" opacity="0.85"/>
      <polygon points="944,126 960,110 972,128" fill="var(--cor-neve)" opacity="0.85"/>

      <!-- construções -->
      <g id="construcoes-grupo">__CONSTRUCOES_SVG__</g>
    </svg>

    <div class="rotulo-zona" style="left:3%;top:9%">Floresta</div>
    <div class="rotulo-zona" style="left:3%;top:73%">Campos</div>
    <div class="rotulo-zona" style="left:44%;top:54%">Centro da Aldeia</div>
    <div class="rotulo-zona" style="left:34.5%;top:62%">Oficina</div>
    <div class="rotulo-zona" style="left:71%;top:25%">Posto de Vigia</div>
    <div class="rotulo-zona" style="left:54.5%;top:46%">Cabana da Cura</div>
    <div class="rotulo-zona" style="left:46.5%;top:37.5%">Círculo Espiritual</div>
    <div class="rotulo-zona" style="left:87%;top:4%">Rio</div>
  </div>
  <div id="painel">
    <div class="vazio">Clique em um ponto para ver a ficha da pessoa.</div>
  </div>
</main>

<div id="legenda"></div>

<script>
const ZONAS = [
  { id: "floresta",   left: 1.5, top: 8,    w: 28.5, h: 60.8, profissoes: ["Caçador(a)", "Coletor(a)"] },
  { id: "campos",     left: 1.5, top: 72,   w: 41.5, h: 24,   profissoes: ["Agricultor(a)"] },
  { id: "aldeia",     left: 44,  top: 52.8, w: 16,   h: 17.6, profissoes: ["Cuidador(a) de Crianças"], comLider: true },
  { id: "oficina",    left: 34,  top: 60.8, w: 12,   h: 16,   profissoes: ["Artesão(ã)", "Construtor(a)"] },
  { id: "vigia",      left: 70,  top: 24,   w: 26,   h: 17.6, profissoes: ["Guerreiro(a)"] },
  { id: "cura",       left: 54,  top: 44.8, w: 12,   h: 14.4, profissoes: ["Curandeiro(a)"] },
  { id: "espiritual", left: 46,  top: 36.8, w: 10,   h: 11.2, profissoes: ["Xamã", "Contador(a) de Histórias"] },
  { id: "rio",        left: 56,  top: 36.8, w: 34,   h: 62.4, profissoes: ["Pescador(a)"] },
];

// Pontos que definem o curso do rio, em % (mesmo traçado do <path> do SVG),
// usados para espalhar os pescadores ao longo da água em vez de numa caixa.
const RIO_PONTOS = [[86, 37.6], [79, 51.2], [82, 67.2], [74, 80], [68, 96]];

function pontoNoRio() {
  const t = Math.random();
  const nSeg = RIO_PONTOS.length - 1;
  const segF = t * nSeg;
  const i = Math.min(Math.floor(segF), nSeg - 1);
  const frac = segF - i;
  const [x1, y1] = RIO_PONTOS[i];
  const [x2, y2] = RIO_PONTOS[i + 1];
  return {
    x: x1 + (x2 - x1) * frac + (Math.random() * 4 - 2),
    y: y1 + (y2 - y1) * frac + (Math.random() * 3 - 1.5),
  };
}

function zonaParaProfissao(prof) {
  for (const z of ZONAS) if (z.profissoes.includes(prof)) return z;
  return ZONAS.find(z => z.id === "aldeia");
}

let DADOS = __DADOS_JSON__;

function idadeDe(pessoa, anoAtual) {
  return anoAtual - pessoa.ano_nascimento;
}

function montarPessoas() {
  const mapa = document.getElementById("mapa-container");
  mapa.querySelectorAll(".ponto").forEach(p => p.remove());
  const anoAtual = DADOS.ano_atual;
  const liderId = DADOS.governo ? DADOS.governo.lider_id : null;
  const vivos = Object.values(DADOS.criaturas).filter(c => c.vivo);

  vivos.forEach(pessoa => {
    const idade = idadeDe(pessoa, anoAtual);
    const zona = (idade < 16 || !pessoa.profissao) ? ZONAS.find(z => z.id === "aldeia") : zonaParaProfissao(pessoa.profissao);

    let left, top;
    if (zona.id === "rio") {
      const p = pontoNoRio();
      left = p.x; top = p.y;
    } else {
      left = zona.left + 8 + Math.random() * Math.max(4, zona.w - 16);
      top = zona.top + 8 + Math.random() * Math.max(4, zona.h - 16);
    }

    const ponto = document.createElement("div");
    ponto.className = "ponto";
    if (pessoa.id === liderId) ponto.classList.add("lider");
    const tamanho = idade < 16 ? 8 : 12;
    ponto.style.width = tamanho + "px";
    ponto.style.height = tamanho + "px";
    ponto.style.left = left + "%";
    ponto.style.top = top + "%";
    ponto.style.background = pessoa.genero === "M" ? "var(--cor-homem)" : "var(--cor-mulher)";
    ponto.style.animationDuration = (3 + Math.random() * 3).toFixed(2) + "s";
    ponto.style.animationDelay = (Math.random() * 3).toFixed(2) + "s";
    ponto.dataset.id = pessoa.id;
    ponto.addEventListener("click", () => selecionar(pessoa.id, ponto));
    mapa.appendChild(ponto);
  });

  // fogueira no centro da aldeia, redesenhada por cima dos pontos antigos
  if (!mapa.querySelector(".fogueira")) {
    const aldeia = ZONAS.find(z => z.id === "aldeia");
    const fogo = document.createElement("div");
    fogo.className = "fogueira";
    fogo.style.left = (aldeia.left + aldeia.w / 2) + "%";
    fogo.style.top = (aldeia.top + aldeia.h / 2 + 3) + "%";
    mapa.appendChild(fogo);
  }
}

function emocaoPredominante(emocoes) {
  return Object.entries(emocoes).sort((a, b) => b[1] - a[1])[0];
}

function selecionar(id, elemento) {
  document.querySelectorAll(".ponto.selecionado").forEach(p => p.classList.remove("selecionado"));
  elemento.classList.add("selecionado");

  const pessoa = DADOS.criaturas[id];
  const anoAtual = DADOS.ano_atual;
  const idade = idadeDe(pessoa, anoAtual);
  const [emoNome, emoValor] = emocaoPredominante(pessoa.emocoes);
  const parceiro = pessoa.parceiro_id && DADOS.criaturas[pessoa.parceiro_id] ? DADOS.criaturas[pessoa.parceiro_id] : null;
  const [paiId, maeId] = pessoa.pais_ids || [null, null];
  const pai = paiId && DADOS.criaturas[paiId] ? DADOS.criaturas[paiId] : null;
  const mae = maeId && DADOS.criaturas[maeId] ? DADOS.criaturas[maeId] : null;
  const nomesFilhos = (pessoa.filhos_ids || [])
    .map(fid => DADOS.criaturas[fid] ? (DADOS.criaturas[fid].nome + " " + DADOS.criaturas[fid].cla) : null)
    .filter(Boolean);

  const prefixo = pessoa.status_social && pessoa.status_social !== "comum" ? pessoa.status_social + " · " : "";

  const painel = document.getElementById("painel");
  painel.innerHTML = `
    <h2>${pessoa.nome} ${pessoa.cla}</h2>
    <div class="sub">${prefixo}${pessoa.estado_civil || "solteiro(a)"} · ${pessoa.genero === "M" ? "Homem" : "Mulher"}, ${idade} anos</div>
    <div class="linha"><b>Função</b> ${pessoa.profissao || "nenhuma ainda"}</div>
    <div class="linha"><b>Humor</b> ${pessoa.tipo_humor}</div>
    <div class="linha"><b>Saúde</b> ${pessoa.saude}/100
      <div class="barra-bg"><div class="barra-fg" style="width:${pessoa.saude}%"></div></div>
    </div>
    <div class="linha"><b>Emoção forte</b> ${emoNome} (${emoValor})</div>
    <div class="linha"><b>Gosta de</b> ${pessoa.gostos.join(", ")}</div>
    <div class="linha"><b>Quer na vida</b> ${pessoa.objetivos.join(", ")}</div>
    <div class="linha"><b>Parceiro(a)</b> ${parceiro ? parceiro.nome + " " + parceiro.cla : "ninguém no momento"}</div>
    <div class="linha"><b>Pai</b> ${pai ? pai.nome + " " + pai.cla : "desconhecido"}</div>
    <div class="linha"><b>Mãe</b> ${mae ? mae.nome + " " + mae.cla : "desconhecida"}</div>
    <div class="linha"><b>Filhos</b> ${nomesFilhos.length ? nomesFilhos.join(", ") : "nenhum ainda"}</div>
  `;
}

function atualizarCabecalho() {
  const vivos = Object.values(DADOS.criaturas).filter(c => c.vivo);
  const lider = DADOS.governo && DADOS.criaturas[DADOS.governo.lider_id];
  document.getElementById("stats-header").innerHTML =
    `Ano <b>${DADOS.ano_atual}</b> · População <b>${vivos.length}</b> · Era <b>${DADOS.era_atual}</b>` +
    (lider ? ` · Líder <b>${lider.nome} ${lider.cla}</b>` : "");
}

function montarLegenda() {
  document.getElementById("legenda").innerHTML =
    `<span><span class="dot" style="background:var(--cor-homem)"></span>Homem</span>` +
    `<span><span class="dot" style="background:var(--cor-mulher)"></span>Mulher</span>` +
    `<span><span class="dot" style="background:#999;box-shadow:0 0 0 2px #FFD27A"></span>Líder</span>`;
}

function renderizarTudo() {
  atualizarCabecalho();
  montarLegenda();
  montarPessoas();
  document.getElementById("painel").innerHTML = '<div class="vazio">Clique em um ponto para ver a ficha da pessoa.</div>';
}

document.getElementById("input-arquivo").addEventListener("change", (ev) => {
  const arquivo = ev.target.files[0];
  if (!arquivo) return;
  const leitor = new FileReader();
  leitor.onload = (e) => {
    try {
      DADOS = JSON.parse(e.target.result);
      renderizarTudo();
    } catch (err) {
      alert("Não consegui ler esse arquivo como JSON válido.");
    }
  };
  leitor.readAsText(arquivo);
});

renderizarTudo();
</script>
</body>
</html>
"""


def main():
    with open(CAMINHO_ESTADO, "r", encoding="utf-8") as f:
        dados = json.load(f)
    html = TEMPLATE.replace("__ARVORES_SVG__", gerar_arvores_svg())
    html = html.replace("__CONSTRUCOES_SVG__", gerar_construcoes_svg())
    html = html.replace("__DADOS_JSON__", json.dumps(dados, ensure_ascii=False))
    with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Gerado: {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
