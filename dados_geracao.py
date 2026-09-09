"""
dados_geracao.py
Listas e tabelas usadas para gerar aleatoriamente as características das
criaturas do microverso: nomes, clãs, profissões, traços de personalidade,
tipos de humor, gostos e objetivos de vida.

Os nomes são gerados de forma PROCEDURAL (por sílabas), e não de uma lista
fixa, porque a população vai crescer com o tempo e listas fixas se
esgotariam (ou começariam a repetir de forma estranha).
"""

import random

# ---------------------------------------------------------------------------
# Geração procedural de nomes
# ---------------------------------------------------------------------------

_CONSOANTES = list("bdfghjklmnprstvz") + ["th", "kr", "dr", "gr", "br", "fr", "tr", "kl", "gl", "vr"]
_VOGAIS = list("aeiou")

# Clãs/famílias fundadoras. A sociedade nasce dividida nesses ~14 grupos,
# o que já cria uma base para política e conflitos futuros (facções).
CLAS = [
    "Thorak", "Vindra", "Kelmun", "Sarnash", "Odrenn", "Farkul",
    "Brammon", "Ystavar", "Quennor", "Halvring", "Drammek", "Nyssara",
    "Morvek", "Ilthara",
]


def _gerar_silaba():
    return random.choice(_CONSOANTES) + random.choice(_VOGAIS)


def gerar_primeiro_nome(genero):
    n_silabas = random.choice([2, 2, 2, 3])
    nome = "".join(_gerar_silaba() for _ in range(n_silabas))
    if genero == "F":
        if not nome.endswith(("a", "i", "e")):
            nome += random.choice(["a", "ia", "e"])
    else:
        if nome.endswith("a"):
            nome = nome[:-1] + random.choice(["o", "an", "ar", "ok", "us"])
    return nome.capitalize()


def gerar_cla():
    return random.choice(CLAS)


# ---------------------------------------------------------------------------
# Profissões da era inicial (pré-tecnológica) e seus pesos de distribuição
# Isso vai virar uma "árvore" quando a tecnologia evoluir (novas profissões
# se tornam possíveis conforme novas descobertas acontecem).
# ---------------------------------------------------------------------------

PROFISSOES_INICIAIS = {
    "Agricultor(a)": 20,
    "Caçador(a)": 15,
    "Coletor(a)": 15,
    "Pescador(a)": 10,
    "Artesão(ã)": 10,
    "Guerreiro(a)": 10,
    "Cuidador(a) de Crianças": 6,
    "Construtor(a)": 6,
    "Curandeiro(a)": 5,
    "Contador(a) de Histórias": 2,
    "Xamã": 1,
}


def sortear_profissao():
    profissoes = list(PROFISSOES_INICIAIS.keys())
    pesos = list(PROFISSOES_INICIAIS.values())
    return random.choices(profissoes, weights=pesos, k=1)[0]


# ---------------------------------------------------------------------------
# Personalidade, humor, emoções
# ---------------------------------------------------------------------------

TRACOS_PERSONALIDADE = [
    "extroversao", "agressividade", "inteligencia", "ambicao",
    "honestidade", "empatia", "coragem", "criatividade",
]

TIPOS_HUMOR = [
    "sarcástico", "debochado", "irônico", "bobo/brincalhão", "ácido",
    "inocente", "cínico", "espirituoso", "sem graça (mas tenta)",
    "excêntrico", "seco", "caloroso",
]

EMOCOES_BASE = ["felicidade", "tristeza", "raiva", "medo", "estresse"]

# ---------------------------------------------------------------------------
# Gostos e objetivos de vida
# ---------------------------------------------------------------------------

GOSTOS_POSSIVEIS = [
    "frutas silvestres", "carne assada no fogo", "peixe grelhado", "mel selvagem",
    "raízes cozidas", "dançar ao redor da fogueira", "contar histórias",
    "nadar no rio", "esculpir madeira ou pedra", "cantar", "observar as estrelas",
    "cuidar de animais", "competir em jogos de força", "caminhar sozinho(a) pela floresta",
    "o som da chuva", "dias de sol forte", "escalar montanhas", "pintar nas rochas",
    "brincar com crianças", "dormir até tarde", "acordar cedo", "colecionar pedras bonitas",
    "tocar tambores", "contar piadas", "ficar em silêncio observando os outros",
]

OBJETIVOS_POSSIVEIS = [
    "formar uma grande família",
    "tornar-se o líder da tribo",
    "explorar terras desconhecidas",
    "acumular o máximo de recursos possível",
    "ser lembrado(a) por seus feitos",
    "viver em paz e tranquilidade",
    "proteger sua família a qualquer custo",
    "dominar uma nova habilidade ou arte",
    "encontrar um grande amor",
    "vingar-se de alguém que o(a) magoou",
    "ganhar o respeito e reconhecimento dos outros",
    "buscar conhecimento e sabedoria",
    "ter poder sobre os outros",
    "ajudar e cuidar dos mais fracos",
]

CAUSAS_MORTE_JOVEM = [
    "acidente de caça", "doença súbita", "afogamento",
    "conflito com outro membro da tribo", "ataque de animal selvagem",
    "complicações no parto",
]
CAUSAS_MORTE_VELHICE = ["velhice", "doença prolongada", "complicações da idade"]
