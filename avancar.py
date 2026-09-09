"""
avancar.py
Avança 1 ano da simulação e salva o resultado. Rode toda vez que quiser
que o tempo passe:

    python avancar.py

Se quiser avançar vários anos de uma vez, veja avancar_varios.py.
"""

from mundo import Mundo
import gerar_visual

CAMINHO = "dados/estado_microverso.json"

m = Mundo.carregar(CAMINHO)
eventos = m.avancar_ano()

print(f"--- Ano {m.ano_atual} ---")
if eventos:
    for e in eventos:
        print(f"- {e}")
else:
    print("(nenhum evento notável este ano)")

m.salvar(CAMINHO)
gerar_visual.main()
print(f"\n[Estado salvo e mapa atualizado. População atual: {len([c for c in m.criaturas.values() if c.vivo])}]")
