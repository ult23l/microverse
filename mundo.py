"""
mundo.py
A classe Mundo controla toda a sociedade: população, história, ano atual,
tecnologia e recursos. Política, guerras e uma árvore de tecnologia mais
completa entram em versões futuras deste motor.
"""

import json
import random
import dados_geracao as dg
from modelos import Criatura


def calcular_compatibilidade(a, b):
    """Quão bem duas criaturas combinam: personalidades parecidas + gostos
    em comum + um fator de sorte/química (0-100)."""
    diffs = [100 - abs(a.personalidade[t] - b.personalidade[t]) for t in a.personalidade]
    media_personalidade = sum(diffs) / len(diffs)
    gostos_em_comum = len(set(a.gostos) & set(b.gostos))
    bonus_gostos = min(30, gostos_em_comum * 15)
    fator_sorte = random.randint(-10, 10)
    compat = media_personalidade * 0.6 + bonus_gostos + fator_sorte
    return max(0, min(100, compat))


def _pontuacao_lideranca(c):
    p = c.personalidade
    base = p["ambicao"] * 0.4 + p["extroversao"] * 0.3 + p["coragem"] * 0.3
    return base + (c.reputacao - 50) * 0.15  # boa/má fama pesa na hora de virar líder


# O que cada tipo de memória vira quando é repassada como fofoca
MAPA_FOFOCA = {
    "amizade_forte": "fofoca_positiva",
    "casou": "fofoca_positiva",
    "tornou_lider": "fofoca_positiva",
    "nasceu": "fofoca_positiva",
    "rivalidade_forte": "fofoca_negativa",
    "morte_parente": "fofoca_negativa",
    "conflito_fome": "fofoca_negativa",
    "fofoca_positiva": "fofoca_positiva",
    "fofoca_negativa": "fofoca_negativa",
}

DESCRICOES_MEMORIA = {
    "nasceu": "o nascimento de {nome}",
    "casou": "o casamento com {nome}",
    "morte_parente": "a morte de {nome}",
    "amizade_forte": "uma grande amizade com {nome}",
    "rivalidade_forte": "uma rivalidade forte com {nome}",
    "fofoca_positiva": "algo bom sobre {nome}",
    "fofoca_negativa": "algo ruim sobre {nome}",
    "tornou_lider": "a ascensão de {nome} como líder",
    "conflito_fome": "uma briga com {nome} por causa da fome",
}


# Produção de recursos por profissão (por pessoa adulta, por ano)
PRODUCAO_COMIDA = {"Agricultor(a)": 16, "Caçador(a)": 12, "Coletor(a)": 8, "Pescador(a)": 12}
PRODUCAO_MATERIAIS = {"Artesão(ã)": 3, "Construtor(a)": 3}
CONSUMO_COMIDA_ADULTO = 5
CONSUMO_COMIDA_CRIANCA = 3


class Mundo:
    def __init__(self):
        self.ano_atual = 1
        self.criaturas = {}       # id -> Criatura
        self.historia = {}        # ano -> lista de eventos (strings)
        self.historico_recursos = {}  # ano -> {comida, materiais, producao_comida, clima, fome}
        self.tecnologias = ["Fogo", "Ferramentas de Pedra", "Linguagem Falada", "Agricultura Rudimentar"]
        self.era_atual = "Idade da Pedra"
        self.governo = {"tipo": "Liderança Tribal", "lider_id": None}
        self.recursos = {"comida": 500, "materiais": 200}
        self._proximo_id = 1

    # ------------------------------------------------------------------
    # Geração da população fundadora (Ano 1)
    # ------------------------------------------------------------------
    def gerar_populacao_inicial(self, n_homens=50, n_mulheres=50):
        generos = ["M"] * n_homens + ["F"] * n_mulheres
        random.shuffle(generos)

        fundadores = []
        for genero in generos:
            idade_inicial = random.randint(16, 45)
            ano_nasc = self.ano_atual - idade_inicial
            c = Criatura(self._novo_id(), genero, ano_nasc, self.ano_atual)
            c.profissao = dg.sortear_profissao()
            self.criaturas[c.id] = c
            fundadores.append(c)

        self._formar_casais_iniciais(fundadores)
        self._eleger_lider(fundadores)

        self.historia[self.ano_atual] = [
            f"Fundação do microverso: {n_homens} homens e {n_mulheres} mulheres se estabeleceram, "
            f"organizados em clãs. A era atual é a {self.era_atual}."
        ]
        lider = self.criaturas[self.governo["lider_id"]]
        self.historia[self.ano_atual].append(
            f"{lider.nome_completo()} foi reconhecido(a) como o(a) primeiro(a) líder da tribo."
        )
        self.historico_recursos[self.ano_atual] = {
            "comida": self.recursos["comida"], "materiais": self.recursos["materiais"],
            "producao_comida": 0, "clima": "normal", "fome": False,
        }
        return fundadores

    def _novo_id(self):
        i = self._proximo_id
        self._proximo_id += 1
        return i

    def _formar_casais_iniciais(self, fundadores):
        homens = [c for c in fundadores if c.genero == "M"]
        mulheres_disponiveis = [c for c in fundadores if c.genero == "F"]
        random.shuffle(homens)
        n_casais = int(min(len(homens), len(mulheres_disponiveis)) * 0.6)
        for h in homens[:n_casais]:
            if not mulheres_disponiveis:
                break
            amostra = random.sample(mulheres_disponiveis, k=min(5, len(mulheres_disponiveis)))
            melhor = max(amostra, key=lambda m: calcular_compatibilidade(h, m))
            mulheres_disponiveis.remove(melhor)
            h.parceiro_id = melhor.id
            melhor.parceiro_id = h.id
            h.estado_civil = melhor.estado_civil = "casado(a)"
            h.anos_juntos = melhor.anos_juntos = random.randint(1, 5)
            melhor.cla = h.cla  # convenção da tribo fundadora: a esposa adota o clã do marido

    def _eleger_lider(self, fundadores):
        lider = max(fundadores, key=_pontuacao_lideranca)
        lider.status_social = "Líder da Tribo"
        self.governo["lider_id"] = lider.id

    # ------------------------------------------------------------------
    # Avanço de tempo
    # ------------------------------------------------------------------
    def avancar_ano(self):
        self.ano_atual += 1
        eventos = []
        vivos = [c for c in self.criaturas.values() if c.vivo]

        # --- Quem chegou à vida adulta e ainda não tem função, arruma um ofício ---
        for c in vivos:
            if c.idade(self.ano_atual) >= 16 and not c.profissao:
                c.profissao = dg.sortear_profissao()

        # --- Economia: produção e consumo de comida e materiais ---
        adultos = [c for c in vivos if c.idade(self.ano_atual) >= 16]
        criancas = [c for c in vivos if c.idade(self.ano_atual) < 16]

        fator_clima = random.choices(["normal", "fartura", "seca"], weights=[70, 15, 15])[0]
        mult_clima = {"normal": 1.0, "fartura": 1.4, "seca": 0.6}[fator_clima]

        producao_comida = sum(PRODUCAO_COMIDA.get(c.profissao, 0) for c in adultos) * mult_clima
        producao_materiais = sum(PRODUCAO_MATERIAIS.get(c.profissao, 0) for c in adultos)
        consumo_comida = len(adultos) * CONSUMO_COMIDA_ADULTO + len(criancas) * CONSUMO_COMIDA_CRIANCA
        consumo_materiais = max(1, len(vivos) // 20)

        self.recursos["comida"] = max(0, self.recursos["comida"] + producao_comida - consumo_comida)
        self.recursos["materiais"] = max(0, self.recursos["materiais"] + producao_materiais - consumo_materiais)
        fome = self.recursos["comida"] <= 0

        if fator_clima == "seca":
            eventos.append("Um ano de seca reduziu as colheitas e a caça.")
        elif fator_clima == "fartura":
            eventos.append("Um ano de fartura trouxe colheitas abundantes.")
        if fome:
            eventos.append("A comida acabou este ano — a fome está afetando a tribo.")

        self.historico_recursos[self.ano_atual] = {
            "comida": self.recursos["comida"], "materiais": self.recursos["materiais"],
            "producao_comida": round(producao_comida, 1), "clima": fator_clima, "fome": fome,
        }

        if fome and len(adultos) >= 2 and random.random() < 0.15:
            a, b = random.sample(adultos, 2)
            a.emocoes["raiva"] = min(100, a.emocoes["raiva"] + 25)
            b.emocoes["raiva"] = min(100, b.emocoes["raiva"] + 25)
            a.saude = max(0, a.saude - random.randint(5, 15))
            eventos.append(f"A fome causou uma briga entre {a.nome_completo()} e {b.nome_completo()} por comida.")

        # --- Nascimentos (só entre casais casados) ---
        processados = set()
        for c in vivos:
            if c.estado_civil == "casado(a)" and c.parceiro_id and c.id not in processados:
                par = self.criaturas.get(c.parceiro_id)
                processados.add(c.id)
                if par:
                    processados.add(par.id)
                mae = c if c.genero == "F" else par
                pai = c if c.genero == "M" else par
                if mae and pai and mae.vivo and pai.vivo:
                    idade_mae = mae.idade(self.ano_atual)
                    chance_nascimento = 0.18 * (0.5 if fome else 1.0)
                    if 16 <= idade_mae <= 45 and random.random() < chance_nascimento:
                        bebe = Criatura(self._novo_id(), random.choice(["M", "F"]),
                                         self.ano_atual, self.ano_atual,
                                         cla=pai.cla, pais_ids=(pai.id, mae.id))
                        self.criaturas[bebe.id] = bebe
                        mae.filhos_ids.append(bebe.id)
                        pai.filhos_ids.append(bebe.id)
                        mae.adicionar_memoria(self.ano_atual, "nasceu", bebe.id)
                        pai.adicionar_memoria(self.ano_atual, "nasceu", bebe.id)
                        eventos.append(f"{mae.nome_completo()} e {pai.nome_completo()} tiveram um(a) filho(a): {bebe.nome_completo()}.")

        # --- Envelhecimento, morte, deriva emocional e eventos aleatórios ---
        for c in vivos:
            idade = c.idade(self.ano_atual)
            chance_morte = 0.004
            if idade > 50:
                chance_morte += (idade - 50) * 0.012
            if c.saude < 50:
                chance_morte += 0.05
            if fome:
                chance_morte += 0.05 if idade < 5 or idade > 60 else 0.025
            chance_morte = min(chance_morte, 0.9)

            if random.random() < chance_morte:
                c.vivo = False
                c.ano_morte = self.ano_atual
                if fome and random.random() < 0.5:
                    c.causa_morte = "fome"
                else:
                    c.causa_morte = random.choice(dg.CAUSAS_MORTE_VELHICE if idade > 55 else dg.CAUSAS_MORTE_JOVEM)
                if c.parceiro_id and c.parceiro_id in self.criaturas:
                    viuvo = self.criaturas[c.parceiro_id]
                    viuvo.emocoes["tristeza"] = min(100, viuvo.emocoes["tristeza"] + 30)
                    viuvo.adicionar_memoria(self.ano_atual, "morte_parente", c.id)
                    if viuvo.estado_civil in ("namorando", "casado(a)"):
                        viuvo.estado_civil = "viúvo(a)"
                    viuvo.parceiro_id = None
                    viuvo.anos_juntos = 0
                for fid in c.filhos_ids:
                    filho = self.criaturas.get(fid)
                    if filho and filho.vivo:
                        filho.adicionar_memoria(self.ano_atual, "morte_parente", c.id)
                for pid in (list(c.pais_ids) + [None, None])[:2]:
                    p_vivo = self.criaturas.get(pid)
                    if p_vivo and p_vivo.vivo:
                        p_vivo.adicionar_memoria(self.ano_atual, "morte_parente", c.id)
                eventos.append(f"{c.nome_completo()} morreu aos {idade} anos ({c.causa_morte}).")
                if c.id == self.governo["lider_id"]:
                    eventos.append("A tribo perdeu seu líder. Uma sucessão será necessária.")
                continue

            # Deriva emocional leve (regressão à média + ruído aleatório + efeito da fome)
            for emo in c.emocoes:
                alvo = 60 if emo == "felicidade" else 20
                if fome:
                    alvo += -15 if emo == "felicidade" else 10
                c.emocoes[emo] += int((alvo - c.emocoes[emo]) * 0.1) + random.randint(-8, 8)
                c.emocoes[emo] = max(0, min(100, c.emocoes[emo]))

            # Fofoca velha perde força: a reputação puxa de volta pro neutro aos poucos
            c.reputacao += int((50 - c.reputacao) * 0.05)

        # --- Paqueras, namoros e casamentos ---
        processados_rel = set()
        for c in vivos:
            if not c.vivo or c.id in processados_rel:
                continue
            idade_c = c.idade(self.ano_atual)

            if c.estado_civil in ("solteiro(a)", "viúvo(a)") and idade_c >= 16:
                chance_tentar = 0.03 + c.personalidade["extroversao"] / 1000
                if random.random() < chance_tentar:
                    candidatos = [o for o in vivos if o.genero != c.genero and o.id != c.id
                                  and o.estado_civil in ("solteiro(a)", "viúvo(a)")
                                  and o.idade(self.ano_atual) >= 16]
                    if candidatos:
                        amostra = random.sample(candidatos, k=min(5, len(candidatos)))
                        melhor = max(amostra, key=lambda o: calcular_compatibilidade(c, o))
                        if calcular_compatibilidade(c, melhor) >= 55:
                            c.estado_civil = melhor.estado_civil = "namorando"
                            c.parceiro_id = melhor.id
                            melhor.parceiro_id = c.id
                            c.anos_juntos = melhor.anos_juntos = 0
                            c.emocoes["felicidade"] = min(100, c.emocoes["felicidade"] + 10)
                            melhor.emocoes["felicidade"] = min(100, melhor.emocoes["felicidade"] + 10)
                            eventos.append(f"{c.nome_completo()} e {melhor.nome_completo()} começaram a namorar.")
                            processados_rel.add(c.id)
                            processados_rel.add(melhor.id)

            elif c.estado_civil == "namorando" and c.parceiro_id:
                par = self.criaturas.get(c.parceiro_id)
                if par and par.vivo:
                    processados_rel.add(c.id)
                    processados_rel.add(par.id)
                    c.anos_juntos += 1
                    par.anos_juntos = c.anos_juntos
                    compat = calcular_compatibilidade(c, par)
                    chance_termino = max(0.03, (70 - compat) / 300)
                    if random.random() < chance_termino:
                        c.estado_civil = par.estado_civil = "solteiro(a)"
                        c.parceiro_id = par.parceiro_id = None
                        c.anos_juntos = par.anos_juntos = 0
                        c.emocoes["tristeza"] = min(100, c.emocoes["tristeza"] + 20)
                        par.emocoes["tristeza"] = min(100, par.emocoes["tristeza"] + 20)
                        eventos.append(f"{c.nome_completo()} e {par.nome_completo()} terminaram o namoro.")
                    elif c.anos_juntos >= 2 and random.random() < 0.4:
                        c.estado_civil = par.estado_civil = "casado(a)"
                        c.emocoes["felicidade"] = min(100, c.emocoes["felicidade"] + 15)
                        par.emocoes["felicidade"] = min(100, par.emocoes["felicidade"] + 15)
                        c.adicionar_memoria(self.ano_atual, "casou", par.id)
                        par.adicionar_memoria(self.ano_atual, "casou", c.id)
                        eventos.append(f"{c.nome_completo()} e {par.nome_completo()} se casaram!")

        # --- Vida social: encontros, amizades, rivalidades e fofoca ---
        self._interacoes_sociais(vivos, eventos)

        # --- Sucessão de liderança, se necessário ---
        lider_atual = self.criaturas.get(self.governo["lider_id"])
        if not lider_atual or not lider_atual.vivo:
            candidatos = [c for c in self.criaturas.values() if c.vivo and c.idade(self.ano_atual) >= 18]
            if candidatos:
                novo_lider = max(candidatos, key=_pontuacao_lideranca)
                novo_lider.status_social = "Líder da Tribo"
                self.governo["lider_id"] = novo_lider.id
                for pessoa in vivos:
                    pessoa.adicionar_memoria(self.ano_atual, "tornou_lider", novo_lider.id)
                eventos.append(f"{novo_lider.nome_completo()} tornou-se o(a) novo(a) líder da tribo.")

        self.historia[self.ano_atual] = eventos
        return eventos

    # ------------------------------------------------------------------
    # Vida social: encontros, amizades, rivalidades e fofoca
    # ------------------------------------------------------------------
    def _interacoes_sociais(self, vivos, eventos):
        pessoas = [c for c in vivos if c.idade(self.ano_atual) >= 12]
        if len(pessoas) < 2:
            return
        n_encontros = len(pessoas) // 3
        for _ in range(n_encontros):
            a, b = self._escolher_par_social(pessoas)
            if a and b:
                self._processar_encontro(a, b, eventos)

    def _escolher_par_social(self, pessoas):
        a = random.choice(pessoas)
        mesmo_grupo = [p for p in pessoas if p.id != a.id and (p.cla == a.cla or p.profissao == a.profissao)]
        pool = mesmo_grupo if mesmo_grupo and random.random() < 0.7 else [p for p in pessoas if p.id != a.id]
        if not pool:
            return None, None
        return a, random.choice(pool)

    def _processar_encontro(self, a, b, eventos):
        chave_b, chave_a = str(b.id), str(a.id)
        rel_a = a.relacoes_sociais.setdefault(chave_b, {"tipo": "conhecido", "confianca": 50})
        rel_b = b.relacoes_sociais.setdefault(chave_a, {"tipo": "conhecido", "confianca": 50})

        compat = calcular_compatibilidade(a, b)
        if compat >= 65:
            delta = random.randint(8, 15)
        elif compat <= 35:
            delta = -random.randint(8, 15)
        else:
            delta = random.randint(-4, 4)

        rel_a["confianca"] = max(0, min(100, rel_a["confianca"] + delta))
        rel_b["confianca"] = rel_a["confianca"]

        tipo_antigo = rel_a["tipo"]
        if rel_a["confianca"] >= 75:
            rel_a["tipo"] = rel_b["tipo"] = "amigo(a)"
        elif rel_a["confianca"] <= 25:
            rel_a["tipo"] = rel_b["tipo"] = "rival"
        else:
            rel_a["tipo"] = rel_b["tipo"] = "conhecido"

        if rel_a["tipo"] == "amigo(a)" and tipo_antigo != "amigo(a)" and rel_a["confianca"] >= 85:
            a.adicionar_memoria(self.ano_atual, "amizade_forte", b.id)
            b.adicionar_memoria(self.ano_atual, "amizade_forte", a.id)
            if random.random() < 0.1:
                eventos.append(f"{a.nome_completo()} e {b.nome_completo()} se tornaram grandes amigos.")
        elif rel_a["tipo"] == "rival" and tipo_antigo != "rival" and rel_a["confianca"] <= 15:
            a.adicionar_memoria(self.ano_atual, "rivalidade_forte", b.id)
            b.adicionar_memoria(self.ano_atual, "rivalidade_forte", a.id)
            a.emocoes["raiva"] = min(100, a.emocoes["raiva"] + 10)
            b.emocoes["raiva"] = min(100, b.emocoes["raiva"] + 10)
            if random.random() < 0.1:
                eventos.append(f"{a.nome_completo()} e {b.nome_completo()} se tornaram rivais.")

        self._tentar_fofoca(a, b)
        self._tentar_fofoca(b, a)

    def _tentar_fofoca(self, contador, ouvinte):
        candidatas = [
            m for m in contador.memorias
            if m["tipo"] in MAPA_FOFOCA and m["sobre_id"] not in (None, ouvinte.id, contador.id)
        ]
        if not candidatas or random.random() > 0.25:
            return
        memoria = random.choice(candidatas)
        sobre_id = memoria["sobre_id"]
        sobre = self.criaturas.get(sobre_id)
        if not sobre:
            return

        tipo_repassado = MAPA_FOFOCA[memoria["tipo"]]
        if random.random() < 0.25:  # o boato se distorce ao ser repassado
            tipo_repassado = "fofoca_negativa" if tipo_repassado == "fofoca_positiva" else "fofoca_positiva"

        ouvinte.adicionar_memoria(self.ano_atual, tipo_repassado, sobre_id, boato=True)

        rel = ouvinte.relacoes_sociais.setdefault(str(sobre_id), {"tipo": "conhecido", "confianca": 50})
        ajuste = 5 if tipo_repassado == "fofoca_positiva" else -5
        rel["confianca"] = max(0, min(100, rel["confianca"] + ajuste))

        if tipo_repassado == "fofoca_positiva":
            sobre.reputacao = min(100, sobre.reputacao + 2)
        else:
            sobre.reputacao = max(0, sobre.reputacao - 2)

    def imprimir_memorias(self, id_pessoa):
        pessoa = self.criaturas.get(id_pessoa)
        if not pessoa:
            print("Pessoa não encontrada.")
            return
        print(f"=== Memórias de {pessoa.nome_completo()} (reputação: {pessoa.reputacao}) ===")
        if not pessoa.memorias:
            print("Nenhuma memória marcante ainda.")
            return
        for m in pessoa.memorias[-10:][::-1]:
            outro = self.criaturas.get(m["sobre_id"])
            nome = outro.nome_completo() if outro else "alguém"
            desc = DESCRICOES_MEMORIA.get(m["tipo"], m["tipo"]).format(nome=nome)
            tag = " (ouviu dizer)" if m.get("boato") else ""
            print(f"Ano {m['ano']}: {desc}{tag}")

    # ------------------------------------------------------------------
    # Estatísticas e utilidades
    # ------------------------------------------------------------------
    def resumo(self):
        vivos = [c for c in self.criaturas.values() if c.vivo]
        homens = [c for c in vivos if c.genero == "M"]
        mulheres = [c for c in vivos if c.genero == "F"]
        idade_media = sum(c.idade(self.ano_atual) for c in vivos) / len(vivos) if vivos else 0
        profissoes = {}
        for c in vivos:
            if c.profissao:
                profissoes[c.profissao] = profissoes.get(c.profissao, 0) + 1
        lider_id = self.governo.get("lider_id")
        solteiros = len([c for c in vivos if c.estado_civil in ("solteiro(a)", "viúvo(a)")])
        namorando = len([c for c in vivos if c.estado_civil == "namorando"]) // 2
        casados = len([c for c in vivos if c.estado_civil == "casado(a)"]) // 2
        amizades = sum(1 for c in vivos for r in c.relacoes_sociais.values() if r["tipo"] == "amigo(a)") // 2
        rivalidades = sum(1 for c in vivos for r in c.relacoes_sociais.values() if r["tipo"] == "rival") // 2
        return {
            "ano": self.ano_atual,
            "populacao_viva": len(vivos),
            "homens": len(homens),
            "mulheres": len(mulheres),
            "idade_media": round(idade_media, 1),
            "profissoes": profissoes,
            "solteiros": solteiros,
            "casais_namorando": namorando,
            "casais_casados": casados,
            "amizades": amizades,
            "rivalidades": rivalidades,
            "comida": round(self.recursos["comida"], 1),
            "materiais": round(self.recursos["materiais"], 1),
            "lider": self.criaturas[lider_id].nome_completo() if lider_id in self.criaturas else "Nenhum",
        }

    # ------------------------------------------------------------------
    # Genealogia
    # ------------------------------------------------------------------
    def genealogia(self, id_pessoa, geracoes_acima=2, geracoes_abaixo=2):
        """Monta a árvore genealógica (pais/avós e filhos/netos) de alguém."""
        pessoa = self.criaturas.get(id_pessoa)
        if not pessoa:
            return None

        def ancestrais(pid, n):
            c = self.criaturas.get(pid)
            if not c or n == 0:
                return None
            pai_id, mae_id = (list(c.pais_ids) + [None, None])[:2]
            return {
                "pessoa": c.nome_completo(),
                "pai": ancestrais(pai_id, n - 1) if pai_id else None,
                "mae": ancestrais(mae_id, n - 1) if mae_id else None,
            }

        def descendentes(pid, n):
            c = self.criaturas.get(pid)
            if not c or n == 0:
                return []
            return [
                {"pessoa": self.criaturas[fid].nome_completo(), "filhos": descendentes(fid, n - 1)}
                for fid in c.filhos_ids if fid in self.criaturas
            ]

        pai_id, mae_id = (list(pessoa.pais_ids) + [None, None])[:2]
        return {
            "pessoa": pessoa.nome_completo(),
            "pai": ancestrais(pai_id, geracoes_acima) if pai_id else None,
            "mae": ancestrais(mae_id, geracoes_acima) if mae_id else None,
            "filhos": descendentes(id_pessoa, geracoes_abaixo),
        }

    def imprimir_genealogia(self, id_pessoa):
        arv = self.genealogia(id_pessoa)
        if not arv:
            print("Pessoa não encontrada.")
            return

        def nome_ou(x, desconhecido):
            return x["pessoa"] if x else desconhecido

        print(f"=== Árvore genealógica de {arv['pessoa']} ===")
        print(f"Pai: {nome_ou(arv['pai'], 'desconhecido')}")
        if arv["pai"] and (arv["pai"]["pai"] or arv["pai"]["mae"]):
            print(f"  Avô paterno: {nome_ou(arv['pai']['pai'], 'desconhecido')}")
            print(f"  Avó paterna: {nome_ou(arv['pai']['mae'], 'desconhecida')}")
        print(f"Mãe: {nome_ou(arv['mae'], 'desconhecida')}")
        if arv["mae"] and (arv["mae"]["pai"] or arv["mae"]["mae"]):
            print(f"  Avô materno: {nome_ou(arv['mae']['pai'], 'desconhecido')}")
            print(f"  Avó materna: {nome_ou(arv['mae']['mae'], 'desconhecida')}")

        def imprimir_filhos(filhos, prefixo="  "):
            for f in filhos:
                print(f"{prefixo}- {f['pessoa']}")
                imprimir_filhos(f["filhos"], prefixo + "  ")

        if arv["filhos"]:
            print("Filhos e descendentes:")
            imprimir_filhos(arv["filhos"])
        else:
            print("Sem filhos registrados ainda.")

    def salvar(self, caminho):
        estado = {
            "ano_atual": self.ano_atual,
            "criaturas": {i: c.to_dict() for i, c in self.criaturas.items()},
            "historia": self.historia,
            "historico_recursos": self.historico_recursos,
            "tecnologias": self.tecnologias,
            "era_atual": self.era_atual,
            "governo": self.governo,
            "recursos": self.recursos,
            "_proximo_id": self._proximo_id,
        }
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)

    @classmethod
    def carregar(cls, caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            estado = json.load(f)
        m = cls()
        m.ano_atual = estado["ano_atual"]
        m.criaturas = {int(i): Criatura.from_dict(d) for i, d in estado["criaturas"].items()}
        m.historia = {int(a): eventos for a, eventos in estado["historia"].items()}
        m.historico_recursos = {int(a): r for a, r in estado.get("historico_recursos", {}).items()}
        m.tecnologias = estado["tecnologias"]
        m.era_atual = estado["era_atual"]
        m.governo = estado["governo"]
        m.recursos = estado["recursos"]
        m._proximo_id = estado["_proximo_id"]
        return m
