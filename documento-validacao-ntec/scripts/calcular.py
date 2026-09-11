#!/usr/bin/env python3
"""
Motor de cálculo da validação — NTec.

Lê um dimensionamento.json (produzido pela skill dimensionar-projeto-ntec) e
emite validacao.json com cronograma, conversões e delta.

Este script existe porque cronograma não pode ser inferência. Se o modelo
alocasse sprints por julgamento, duas execuções com a mesma entrada dariam
cronogramas diferentes — e o objetivo declarado do sistema é que todas as
validações sigam o mesmo modelo e a mesma lógica. Aqui é aritmética.

Teste de aceitação: rodar duas vezes no mesmo arquivo deve produzir saídas
byte a byte idênticas, inclusive se a ordem das features na entrada mudar.
Por isso toda iteração que gera saída percorre listas ordenadas por id, nunca
a ordem do JSON de entrada.

Uso:
    python calcular.py dimensionamento-cliente-2025-08-13.json
    python calcular.py entrada.json --itip 1200 --atipica --saida validacao.json
"""

import argparse
import json
import math
import sys

# ---------------------------------------------------------------- constantes

PD_POR_COMPLEXIDADE = {"XS": 1, "S": 2, "M": 5, "L": 8, "XL": 13, "XXL": 21}
ORDEM_MOSCOW = {"Must": 0, "Should": 1, "Could": 2, "Wont": 3}

SEMANAS_POR_SPRINT = 2
PD_POR_DEV = 7            # metade dos 14 PD/sprint da equipe padrão de 2 devs
TETO_MULTIPLICADOR = 2.0
BUFFER_BASE = 0.15
BUFFER_TETO = 0.40
FATOR_BUFFER = 0.05
LIMITE_SPRINTS_SEMESTRE = 12   # acima disso o projeto cruza a troca semestral
TESTE_FRACAO_DEV = 0.10
TESTE_PISO = 0.5
TESTE_TETO = 2.0

EPS = 1e-9


class ErroDeEntrada(Exception):
    """Problema no dimensionamento.json que impede o cálculo."""


# ------------------------------------------------------------------ entradas

def carregar(caminho):
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ErroDeEntrada(f"arquivo não encontrado: {caminho}")
    except json.JSONDecodeError as e:
        raise ErroDeEntrada(f"JSON inválido em {caminho}: {e}")


def num(valor, padrao=0):
    """Converte para número tratando None. O contrato permite campo nulo em
    quase tudo — lacuna é resposta válida —, então `.get(k, padrao)` não basta:
    a chave existe, o valor é que é None."""
    return padrao if valor is None else valor


def equipe_de(dim):
    return (dim.get("meta") or {}).get("equipe") or {}


def velocidade_ajustada(dim):
    """Aplica o ajuste de composição. A skill 1 registra a velocidade base e a
    composição; o ajuste acontece só aqui, para não ser contado duas vezes.

    A base vem do JSON quando presente — se a régua for recalibrada, o valor
    novo viaja no dimensionamento e este script o respeita."""
    equipe = equipe_de(dim)
    devs = num(equipe.get("devs"), 2)
    base = (dim.get("meta") or {}).get("velocidade_base_pd_sprint")
    v = num(base, PD_POR_DEV * 2) / 2 * devs if base else PD_POR_DEV * devs

    senioridade = equipe.get("senioridade")
    if senioridade == "veterano":
        v *= 1.15
    elif senioridade == "junior":
        v *= 0.75
    return round(v, 2)


def features_dev(dim):
    """Só RF dentro do escopo pontuam. RN e RNF existem no inventário para
    rastreabilidade, com pd 0. Wont é escopo declarado como não entregue —
    se aparecer como 'Dentro', é contradição e vira aviso, não trabalho."""
    return [
        f for f in dim.get("features") or []
        if f.get("tipo") == "RF"
        and f.get("escopo") == "Dentro"
        and f.get("prioridade") != "Wont"
    ]


# ------------------------------------------------------------------ ordenação

def niveis_por_dependencia(features):
    """Nível topológico de cada feature. Ciclo levanta erro: silenciá-lo
    produziria um cronograma impossível com aparência de válido."""
    por_id = {f["id"]: f for f in features}
    nivel = {}

    def calcular(fid, caminho):
        if fid in nivel:
            return nivel[fid]
        if fid in caminho:
            ciclo = " -> ".join(caminho + [fid])
            raise ErroDeEntrada(f"ciclo em depende_de: {ciclo}")
        caminho.append(fid)
        deps = [d for d in num(por_id[fid].get("depende_de"), []) if d in por_id]
        nivel[fid] = 0 if not deps else 1 + max(calcular(d, caminho) for d in deps)
        caminho.pop()
        return nivel[fid]

    for f in sorted(features, key=lambda f: f["id"]):
        calcular(f["id"], [])
    return nivel


def ordenar(features):
    """Ordenação determinística: nível de dependência, depois MoSCoW, depois PD
    decrescente, e o id como desempate final. O id no fim é o que garante que
    mudar a ordem da entrada não muda a saída."""
    nivel = niveis_por_dependencia(features)
    return sorted(
        features,
        key=lambda f: (
            nivel[f["id"]],
            ORDEM_MOSCOW.get(f.get("prioridade"), 9),
            -f["pd_ajustado"],
            f["id"],
        ),
    )


# ------------------------------------------------------------------ alocação

def alocar_desenvolvimento(ordenadas, capacidade):
    """Empacotamento guloso respeitando dependência em granularidade de sprint.

    Uma feature nunca entra numa sprint anterior ou igual à de uma dependência.
    Feature maior que a capacidade ocupa uma sprint sozinha e a estoura — isso
    fica visível de propósito, porque escondê-lo seria fingir que cabe."""
    sprints = []
    onde = {}

    for f in ordenadas:
        minimo = 0
        for d in num(f.get("depende_de"), []):
            if d in onde:
                minimo = max(minimo, onde[d] + 1)

        i = minimo
        while True:
            while len(sprints) <= i:
                sprints.append({"features": [], "pd": 0.0})
            vazia = sprints[i]["pd"] < EPS
            cabe = sprints[i]["pd"] + f["pd_ajustado"] <= capacidade + EPS
            if vazia or cabe:
                break
            i += 1

        sprints[i]["features"].append(f)
        sprints[i]["pd"] = round(sprints[i]["pd"] + f["pd_ajustado"], 2)
        onde[f["id"]] = i

    return sprints


def alocar_blocos(itens):
    """Empacota blocos fracionários em slots de 1 sprint.

    Discovery de 0,5 e infra de 0,5 dividem uma sprint. Sprint é sempre 15 dias
    — a fração descreve quanto da sprint o bloco consome, não uma sprint mais
    curta."""
    slots, atual, usado = [], [], 0.0

    for nome, quantidade in itens:
        restante = round(max(0.0, float(num(quantidade, 0))), 4)
        while restante > EPS:
            usa = round(min(round(1.0 - usado, 4), restante), 4)
            atual.append({"bloco": nome, "fracao": usa})
            usado = round(usado + usa, 4)
            restante = round(restante - usa, 4)
            if usado >= 1.0 - EPS:
                slots.append(atual)
                atual, usado = [], 0.0

    if atual:
        slots.append(atual)
    return slots


# -------------------------------------------------------------------- buffer

def montar_buffer(dim, fatores_extra):
    base = num((dim.get("buffer") or {}).get("base"), BUFFER_BASE)
    fatores = list(num((dim.get("buffer") or {}).get("fatores"), [])) + fatores_extra
    soma_bruta = round(base + sum(num(f.get("valor"), 0) for f in fatores), 4)
    return {
        "base": base,
        "fatores": fatores,
        "soma_bruta": soma_bruta,
        "total": round(min(soma_bruta, BUFFER_TETO), 4),
        "atingiu_teto": soma_bruta > BUFFER_TETO + EPS,
    }


def resolver_buffer(dim, sprints_total, atipica_confirmada):
    """Completa os fatores que a skill 1 deixou pendentes.

    'Projeto acima de 12 sprints' é sobre calendário real, então precisa ser
    avaliado contra as sprints vendidas, não as dimensionadas. Isso parece
    circular — o buffer define as vendidas — mas não é: o fator só soma, então
    se o total já passa de 12 sem ele, passa com ele também. Avaliamos com o
    fator desligado e ligamos se necessário. Uma passada, resultado estável."""
    pendentes = num((dim.get("buffer") or {}).get("fatores_pendentes"), [])
    extras, resolvidos, ainda_pendentes = [], [], []

    provisorio = montar_buffer(dim, [])
    vendidos_sem_fator = math.ceil(sprints_total * (1 + provisorio["total"]) - EPS)

    for p in sorted(pendentes, key=lambda x: x.get("fator") or ""):
        nome = (p.get("fator") or "").lower()
        if "12 sprint" in nome:
            if vendidos_sem_fator > LIMITE_SPRINTS_SEMESTRE:
                item = {"fator": p["fator"], "valor": FATOR_BUFFER,
                        "porque": f"{vendidos_sem_fator} sprints vendidas cruzam a troca semestral"}
                extras.append(item)
                resolvidos.append(item)
            else:
                resolvidos.append({"fator": p["fator"], "valor": 0.0,
                                   "porque": f"{vendidos_sem_fator} sprints vendidas, dentro do limite"})
        elif "atipic" in nome or "atípic" in nome:
            if atipica_confirmada:
                item = {"fator": p["fator"], "valor": FATOR_BUFFER,
                        "porque": "confirmado pelo validador via --atipica"}
                extras.append(item)
                resolvidos.append(item)
            else:
                ainda_pendentes.append(p)
        else:
            ainda_pendentes.append(p)

    buffer = montar_buffer(dim, extras)
    buffer["resolvidos_aqui"] = resolvidos
    buffer["fatores_pendentes"] = ainda_pendentes
    return buffer


# ------------------------------------------------------------------ validação

def validar(dim):
    """Erros que impedem o cálculo levantam; o resto vira aviso ordenado."""
    avisos = []
    todas = dim.get("features") or []

    vistos, duplicados = set(), set()
    for f in todas:
        fid = f.get("id")
        if not fid:
            raise ErroDeEntrada("há feature sem 'id' — o cronograma não pode ser montado")
        if fid in vistos:
            duplicados.add(fid)
        vistos.add(fid)
    if duplicados:
        raise ErroDeEntrada(
            "ids duplicados em features: " + ", ".join(sorted(duplicados))
            + ". Ids precisam ser únicos, senão as dependências apontam para a feature errada."
        )

    contadas = {f["id"] for f in features_dev(dim)}
    for f in sorted(todas, key=lambda f: f["id"]):
        for d in num(f.get("depende_de"), []):
            if d not in vistos:
                avisos.append(f"{f['id']} depende de '{d}', que não existe no inventário.")
            elif f["id"] in contadas and d not in contadas:
                avisos.append(
                    f"{f['id']} depende de '{d}', que está fora da contagem "
                    "(fora do escopo, a definir, Wont ou não-RF) — a dependência foi ignorada no cronograma."
                )

    for f in sorted(todas, key=lambda f: f["id"]):
        if f.get("prioridade") == "Wont" and f.get("escopo") == "Dentro":
            avisos.append(f"{f['id']} está 'Dentro' do escopo com prioridade Wont — contradição; não foi alocada.")

    for f in sorted(features_dev(dim), key=lambda f: f["id"]):
        esperado = PD_POR_COMPLEXIDADE.get(f.get("complexidade"))
        if f.get("pd") is None:
            avisos.append(f"{f['id']} está sem pd — contado como 0. Confirme antes de usar este número.")
        elif esperado is not None and f["pd"] != esperado:
            avisos.append(f"{f['id']}: pd={f['pd']} não bate com complexidade "
                          f"{f['complexidade']} (esperado {esperado}).")
        if f.get("complexidade") == "XXL":
            avisos.append(f"{f['id']} está em XXL — quebra obrigatória antes de fechar.")
        if f.get("complexidade") in ("L", "XL", "XXL") and not f.get("confirmado_por"):
            avisos.append(f"{f['id']} ({f['complexidade']}) ainda não foi confirmada por um dev da stack.")

    if todas:
        a_definir = sum(1 for f in todas if f.get("escopo") == "A definir")
        if a_definir / len(todas) > 0.10:
            avisos.append(f"{a_definir} de {len(todas)} features em 'A definir' "
                          f"({a_definir/len(todas):.0%}) — escopo fechado não se sustenta.")
    return avisos


# ------------------------------------------------------------------- cálculo

def calcular(dim, itip=None, atipica_confirmada=False):
    avisos = validar(dim)

    ctx = dim.get("contexto") or {}
    mult_bruto = float(num(ctx.get("multiplicador_bruto"), num(ctx.get("multiplicador"), 1.0)))
    multiplicador = min(mult_bruto, TETO_MULTIPLICADOR)
    if mult_bruto > TETO_MULTIPLICADOR + EPS:
        avisos.append(f"Multiplicador bruto {mult_bruto:.2f} acima do teto de {TETO_MULTIPLICADOR}. "
                      "Projeto não é dimensionável em escopo fechado — decisão do CP.")

    feats = features_dev(dim)
    for f in feats:
        f["pd_bruto"] = num(f.get("pd"), 0)
        f["pd_ajustado"] = round(f["pd_bruto"] * multiplicador, 2)

    pd_dev = sum(f["pd_bruto"] for f in feats)
    pd_ajustado = round(pd_dev * multiplicador, 2)

    velocidade = velocidade_ajustada(dim)
    if velocidade <= 0:
        raise ErroDeEntrada("velocidade calculada é zero ou negativa — confira meta.equipe")

    sprints_dev = alocar_desenvolvimento(ordenar(feats), velocidade)
    n_dev = len(sprints_dev)

    bf = dim.get("blocos_fixos") or {}
    teste = min(max(round(n_dev * TESTE_FRACAO_DEV, 2), TESTE_PISO), TESTE_TETO)
    if bf.get("qa_separado") or (dim.get("produto") or {}).get("criticidade") == 3:
        teste = max(teste, 1.0)
        avisos.append("QA e UAT não podem dividir a mesma sprint neste projeto — bloco de teste em 1 sprint cheia.")

    slots_antes = alocar_blocos([
        ("Refino, discovery, setup e acessos", bf.get("discovery")),
        ("Infra, auth e níveis de acesso", bf.get("infra")),
        ("Spikes", bf.get("spikes")),
    ])
    slots_depois = alocar_blocos([
        ("Testes e QA com o cliente", teste),
        ("Deploy e go-live", bf.get("deploy")),
        ("Publicação em lojas", bf.get("publicacao_lojas")),
    ])

    sprints_total = len(slots_antes) + n_dev + len(slots_depois)

    buffer = resolver_buffer(dim, sprints_total, atipica_confirmada)
    for p in buffer["fatores_pendentes"]:
        avisos.append(f"Fator de buffer não resolvido: {p.get('fator')} — {p.get('porque_pendente')}")
    if buffer["atingiu_teto"]:
        avisos.append(f"Buffer bruto {buffer['soma_bruta']:.0%} acima do teto; aplicado {BUFFER_TETO:.0%}.")

    sprints_vendidos = math.ceil(sprints_total * (1 + buffer["total"]) - EPS)
    margem_sprints = sprints_vendidos - sprints_total
    semanas_vendidas = sprints_vendidos * SEMANAS_POR_SPRINT

    equipe = equipe_de(dim)
    consultores = num(equipe.get("devs"), 2) + num(equipe.get("as"), 1)
    preco = round(itip * consultores * semanas_vendidas, 2) if itip is not None else None

    cronograma = montar_cronograma(slots_antes, sprints_dev, slots_depois,
                                   margem_sprints, velocidade)
    delta = calcular_delta(dim, semanas_vendidas, preco, consultores)

    return {
        "meta": dim.get("meta") or {},
        "entradas": {
            "velocidade_base": (dim.get("meta") or {}).get("velocidade_base_pd_sprint"),
            "velocidade_ajustada": velocidade,
            "multiplicador_bruto": mult_bruto,
            "multiplicador": multiplicador,
            "itip": itip,
            "consultores": consultores,
        },
        "dimensionamento": {
            "pd_dev": pd_dev,
            "pd_ajustado": pd_ajustado,
            "features_contadas": len(feats),
            "sprints_desenvolvimento": n_dev,
            "sprints_blocos_antes": len(slots_antes),
            "sprints_blocos_depois": len(slots_depois),
            "bloco_teste": teste,
            "sprints_total": sprints_total,
        },
        "buffer": buffer,
        "venda": {
            "sprints_vendidos": sprints_vendidos,
            "margem_sprints": margem_sprints,
            "semanas_vendidas": semanas_vendidas,
            "preco": preco,
        },
        "cronograma": cronograma,
        "delta": delta,
        "avisos": avisos,
    }


def montar_cronograma(slots_antes, sprints_dev, slots_depois, margem, velocidade):
    cronograma = []

    def semanas(n):
        return f"{n * SEMANAS_POR_SPRINT + 1}-{(n + 1) * SEMANAS_POR_SPRINT}"

    def bloco(n, slot):
        return {"sprint": n, "semanas": semanas(n), "tipo": "bloco_fixo",
                "objetivo": " + ".join(b["bloco"] for b in slot),
                "blocos": slot, "features": [], "pd": 0.0}

    n = 0
    for slot in slots_antes:
        cronograma.append(bloco(n, slot)); n += 1
    for s in sprints_dev:
        cronograma.append({
            "sprint": n, "semanas": semanas(n), "tipo": "desenvolvimento",
            "objetivo": modulos_da_sprint(s["features"]), "blocos": [],
            "features": [{"id": f["id"], "nome": f.get("nome", f["id"]),
                          "pd_bruto": f["pd_bruto"], "pd_ajustado": f["pd_ajustado"]}
                         for f in s["features"]],
            "pd": s["pd"],
            "ociosidade": round(max(0.0, velocidade - s["pd"]), 2),
        })
        n += 1
    for slot in slots_depois:
        cronograma.append(bloco(n, slot)); n += 1
    for _ in range(margem):
        cronograma.append({"sprint": n, "semanas": semanas(n), "tipo": "margem",
                           "objetivo": "Margem contratada — não alocar trabalho",
                           "blocos": [], "features": [], "pd": 0.0})
        n += 1
    return cronograma


def modulos_da_sprint(features):
    vistos = []
    for f in features:
        m = f.get("modulo") or "Sem módulo"
        if m not in vistos:
            vistos.append(m)
    return " + ".join(vistos) if vistos else "Desenvolvimento"


def calcular_delta(dim, semanas_dim, preco, consultores):
    """Quando a validação acontece depois da venda, esta é a seção que importa:
    a distância entre o que foi prometido e o que foi medido."""
    vendido = dim.get("vendido") or {}
    if not vendido.get("houve_venda"):
        return {"houve_venda": False,
                "observacao": "Dimensionamento anterior à proposta — não há delta a apurar."}

    semanas_vend = vendido.get("prazo_sinalizado_semanas")
    investimento = vendido.get("investimento_brl")

    d = {
        "houve_venda": True,
        "semanas_sinalizadas": semanas_vend,
        "semanas_dimensionadas": semanas_dim,
        "delta_semanas": (semanas_dim - semanas_vend) if semanas_vend else None,
        "investimento": investimento,
        "preco_dimensionado": preco,
        "itip_implicito_no_vendido": None,
        "itip_implicito_no_dimensionado": None,
        "recurso_obrigatorio": None,
    }

    if investimento and semanas_vend and consultores:
        d["itip_implicito_no_vendido"] = round(investimento / semanas_vend / consultores, 2)
    if investimento and semanas_dim and consultores:
        d["itip_implicito_no_dimensionado"] = round(investimento / semanas_dim / consultores, 2)

    if d["delta_semanas"] and d["delta_semanas"] > 0:
        d["recurso_obrigatorio"] = (
            "Delta positivo. Escolha e registre uma saída: cortar escopo pela ordem "
            "de prioridade, negociar sprints adicionais, consumir margem, ou aceitar "
            "o risco com nome de quem aceitou. Sem isso a validação não fecha."
        )
    return d


# ---------------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description="Motor de cálculo da validação NTec")
    p.add_argument("entrada", help="caminho do dimensionamento.json")
    p.add_argument("--itip", type=float, default=None,
                   help="ITIP por consultor-semana (alvo 1200, piso 900)")
    p.add_argument("--atipica", action="store_true",
                   help="confirma feature atípica sem benchmark (+5%% de buffer)")
    p.add_argument("--saida", default="validacao.json")
    args = p.parse_args()

    try:
        resultado = calcular(carregar(args.entrada),
                             itip=args.itip, atipica_confirmada=args.atipica)
    except ErroDeEntrada as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1

    with open(args.saida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2, sort_keys=True)

    d, v = resultado["dimensionamento"], resultado["venda"]
    print(f"PD {d['pd_dev']} -> ajustado {d['pd_ajustado']} "
          f"(x{resultado['entradas']['multiplicador']}, "
          f"velocidade {resultado['entradas']['velocidade_ajustada']} PD/sprint)")
    print(f"Sprints: {d['sprints_total']} dimensionadas, "
          f"{v['sprints_vendidos']} vendidas ({v['margem_sprints']} de margem)")
    print(f"Semanas vendidas: {v['semanas_vendidas']}"
          + (f" | Preco R$ {v['preco']:,.2f}" if v["preco"] is not None else ""))
    if resultado["avisos"]:
        print(f"\n{len(resultado['avisos'])} aviso(s):")
        for a in resultado["avisos"]:
            print(f"  - {a}")
    print(f"\nSaida: {args.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
