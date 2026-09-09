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
    return p["ambicao"] * 0.4 + p["extroversao"] * 0.3 + p["coragem"] * 0.3


class Mundo:
    def __init__(self):
        self.ano_atual = 1
        self.criaturas = {}       # id -> Criatura
        self.historia = {}        # ano -> lista de eventos (strings)
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
                    if 16 <= idade_mae <= 45 and random.random() < 0.18:
                        bebe = Criatura(self._novo_id(), random.choice(["M", "F"]),
                                         self.ano_atual, self.ano_atual,
                                         cla=pai.cla, pais_ids=(pai.id, mae.id))
                        self.criaturas[bebe.id] = bebe
                        mae.filhos_ids.append(bebe.id)
                        pai.filhos_ids.append(bebe.id)
                        eventos.append(f"{mae.nome_completo()} e {pai.nome_completo()} tiveram um(a) filho(a): {bebe.nome_completo()}.")

        # --- Envelhecimento, morte, deriva emocional e eventos aleatórios ---
        for c in vivos:
            idade = c.idade(self.ano_atual)
            chance_morte = 0.004
            if idade > 50:
                chance_morte += (idade - 50) * 0.012
            if c.saude < 50:
                chance_morte += 0.05
            chance_morte = min(chance_morte, 0.9)

            if random.random() < chance_morte:
                c.vivo = False
                c.ano_morte = self.ano_atual
                c.causa_morte = random.choice(dg.CAUSAS_MORTE_VELHICE if idade > 55 else dg.CAUSAS_MORTE_JOVEM)
                if c.parceiro_id and c.parceiro_id in self.criaturas:
                    viuvo = self.criaturas[c.parceiro_id]
                    viuvo.emocoes["tristeza"] = min(100, viuvo.emocoes["tristeza"] + 30)
                    if viuvo.estado_civil in ("namorando", "casado(a)"):
                        viuvo.estado_civil = "viúvo(a)"
                    viuvo.parceiro_id = None
                    viuvo.anos_juntos = 0
                eventos.append(f"{c.nome_completo()} morreu aos {idade} anos ({c.causa_morte}).")
                if c.id == self.governo["lider_id"]:
                    eventos.append("A tribo perdeu seu líder. Uma sucessão será necessária.")
                continue

            # Deriva emocional leve (regressão à média + ruído aleatório)
            for emo in c.emocoes:
                alvo = 60 if emo == "felicidade" else 20
                c.emocoes[emo] += int((alvo - c.emocoes[emo]) * 0.1) + random.randint(-8, 8)
                c.emocoes[emo] = max(0, min(100, c.emocoes[emo]))

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
                        eventos.append(f"{c.nome_completo()} e {par.nome_completo()} se casaram!")

        # --- Sucessão de liderança, se necessário ---
        lider_atual = self.criaturas.get(self.governo["lider_id"])
        if not lider_atual or not lider_atual.vivo:
            candidatos = [c for c in self.criaturas.values() if c.vivo and c.idade(self.ano_atual) >= 18]
            if candidatos:
                novo_lider = max(candidatos, key=_pontuacao_lideranca)
                novo_lider.status_social = "Líder da Tribo"
                self.governo["lider_id"] = novo_lider.id
                eventos.append(f"{novo_lider.nome_completo()} tornou-se o(a) novo(a) líder da tribo.")

        self.historia[self.ano_atual] = eventos
        return eventos

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
        m.tecnologias = estado["tecnologias"]
        m.era_atual = estado["era_atual"]
        m.governo = estado["governo"]
        m.recursos = estado["recursos"]
        m._proximo_id = estado["_proximo_id"]
        return m
