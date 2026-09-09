"""
avancar_varios.py
Avança vários anos de uma vez e salva no final. Uso:

    python avancar_varios.py 10

(avança 10 anos; se não passar número, avança 5 por padrão)
"""

import sys
from mundo import Mundo
import gerar_visual

CAMINHO = "dados/estado_microverso.json"
n_anos = int(sys.argv[1]) if len(sys.argv) > 1 else 5

m = Mundo.carregar(CAMINHO)

for _ in range(n_anos):
    eventos = m.avancar_ano()
    interessantes = [e for e in eventos if any(p in e for p in
                     ["namorar", "casaram", "terminaram", "filho", "morreu", "líder"])]
    print(f"--- Ano {m.ano_atual} ({len(eventos)} eventos) ---")
    for e in interessantes:
        print(f"  {e}")

m.salvar(CAMINHO)
gerar_visual.main()
vivos = len([c for c in m.criaturas.values() if c.vivo])
print(f"\n[Estado salvo e mapa atualizado. Ano {m.ano_atual}, população {vivos}]")
