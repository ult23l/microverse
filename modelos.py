"""
modelos.py
Define a classe Criatura: cada um dos habitantes do microverso, com
personalidade, senso de humor, emoções, profissão, gostos, objetivos
de vida e relações familiares.
"""

import random
import dados_geracao as dg


class Criatura:
    def __init__(self, id_, genero, ano_nascimento, ano_atual, cla=None, pais_ids=(None, None)):
        self.id = id_
        self.genero = genero  # "M" ou "F"
        self.nome = dg.gerar_primeiro_nome(genero)
        self.cla = cla or dg.gerar_cla()
        self.ano_nascimento = ano_nascimento
        self.pais_ids = list(pais_ids)

        # Personalidade (0-100 em cada traço)
        self.personalidade = {t: random.randint(5, 95) for t in dg.TRACOS_PERSONALIDADE}

        # Senso de humor (traço fixo de personalidade cômica)
        self.tipo_humor = random.choice(dg.TIPOS_HUMOR)

        # Emoções atuais (0-100 cada, mudam ano a ano)
        self.emocoes = {
            "felicidade": random.randint(45, 90),
            "tristeza": random.randint(0, 30),
            "raiva": random.randint(0, 25),
            "medo": random.randint(0, 35),
            "estresse": random.randint(10, 40),
        }

        # Função/profissão (definida na fundação ou ao chegar à vida adulta)
        self.profissao = None

        # Gostos e objetivos de vida
        self.gostos = random.sample(dg.GOSTOS_POSSIVEIS, k=3)
        self.objetivos = random.sample(dg.OBJETIVOS_POSSIVEIS, k=random.choice([1, 2]))

        # Saúde e status
        self.saude = random.randint(70, 100)
        self.vivo = True
        self.ano_morte = None
        self.causa_morte = None
        self.status_social = "comum"

        # Relações
        self.estado_civil = "solteiro(a)"   # solteiro(a) | namorando | casado(a) | viúvo(a)
        self.parceiro_id = None
        self.anos_juntos = 0                # anos namorando ou casado com o parceiro atual
        self.filhos_ids = []

    def idade(self, ano_atual):
        return ano_atual - self.ano_nascimento

    def nome_completo(self):
        return f"{self.nome} {self.cla}"

    def resumo(self, ano_atual):
        idade = self.idade(ano_atual)
        tags = []
        if self.status_social != "comum":
            tags.append(self.status_social)
        if self.estado_civil != "solteiro(a)":
            tags.append(self.estado_civil)
        status = f" [{', '.join(tags)}]" if tags else ""
        emocao_forte = max(self.emocoes, key=self.emocoes.get)
        return (
            f"{self.nome_completo()}{status} — {self.genero}, {idade} anos, {self.profissao or 'sem função'}\n"
            f"  Humor: {self.tipo_humor} | Saúde: {self.saude} | Emoção predominante: {emocao_forte}\n"
            f"  Gosta de: {', '.join(self.gostos)}\n"
            f"  Quer na vida: {', '.join(self.objetivos)}"
        )

    def to_dict(self):
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)
        obj.__dict__.update(d)
        # --- Migração de estados salvos antes do sistema de namoro/relações ---
        if not hasattr(obj, "estado_civil"):
            if getattr(obj, "status_social", "") == "casado(a)" or getattr(obj, "conjuge_id", None):
                obj.estado_civil = "casado(a)"
                if obj.status_social == "casado(a)":
                    obj.status_social = "comum"
            else:
                obj.estado_civil = "solteiro(a)"
        if not hasattr(obj, "parceiro_id"):
            obj.parceiro_id = getattr(obj, "conjuge_id", None)
        if not hasattr(obj, "anos_juntos"):
            obj.anos_juntos = 3 if obj.estado_civil == "casado(a)" else 0
        if not getattr(obj, "pais_ids", None):
            obj.pais_ids = [None, None]
        if not hasattr(obj, "filhos_ids"):
            obj.filhos_ids = []
        return obj
