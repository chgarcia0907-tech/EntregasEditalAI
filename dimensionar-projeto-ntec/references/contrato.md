# Contrato — `dimensionamento.json`

Artefato intermediário. Esta skill escreve, a skill `documento-validacao-ntec` lê. É o que permite as duas evoluírem em repositórios separados sem quebrar uma à outra.

## Princípio

O contrato guarda **fatos e classificações**, nunca **resultados calculados**. Não há campos para sprints totais, semanas vendidas, preço ou ITIP — quem deriva isso é a skill 2.

A razão é concreta: se o número calculado viajasse no JSON, as duas skills poderiam discordar sobre ele, e não haveria como saber qual está certa.

## Nome e local do arquivo

`dimensionamento-<cliente-slug>-<AAAA-MM-DD>.json`, na pasta de trabalho. Exemplo: `dimensionamento-clinica-vitalis-2025-08-13.json`.

O slug vem do nome do cliente em minúsculas, sem acento, com hífen no lugar de espaço. Nome genérico faria o segundo projeto do dia sobrescrever o primeiro.

Se já existir arquivo para o mesmo cliente em data anterior, é um **redimensionamento**: preencha `meta.substitui` com o nome do arquivo anterior e liste em `meta.mudancas` o que mudou e por quê. Não edite o arquivo antigo — a comparação entre versões é informação.

---

## Schema

```json
{
  "meta": {
    "projeto": "",
    "cliente": "",
    "cn": "",
    "validador": null,
    "data": "AAAA-MM-DD",
    "versao_regua": "0.1",
    "versao_skill": "0.2",
    "velocidade_base_pd_sprint": 14,
    "equipe": { "devs": 2, "as": 1, "senioridade": "junior" },
    "substitui": null,
    "mudancas": []
  },

  "vendido": {
    "houve_venda": false,
    "prazo_sinalizado_semanas": null,
    "investimento_brl": null,
    "parcelamento": null,
    "modelo_escopo": null,
    "fonte": null
  },

  "cliente": {
    "responsavel": { "nome": "", "cargo": "", "fonte": "" },
    "autoridade_de_compra": { "nome": null, "cargo": null, "fonte": null },
    "porte": null,
    "maturidade_tech": null,
    "restricao_stack": null,
    "regras_deploy": null,
    "nivel_detalhamento_demanda": null
  },

  "produto": {
    "o_que_e": { "valor": "", "fonte": "" },
    "problema": { "valor": "", "custo_atual_para_o_cliente": null, "fonte": "" },
    "perfis": [{ "nome": "", "quantidade_estimada": null, "o_que_faz": "", "fonte": "" }],
    "metrica_de_sucesso": { "valor": null, "fonte": null },
    "urgencia": { "data": null, "o_que_acontece_se_atrasar": null, "fonte": null },
    "criticidade": null,
    "fora_do_escopo": [{ "item": "", "porque": "", "fonte": "" }]
  },

  "parecer": {
    "ambiguidades": [
      { "descricao": "", "quem_resolve": "", "trava": "", "muda_pd": false, "feature_id": null }
    ],
    "mais_complexas": [
      { "feature_id": "", "porque": "", "complexidade": "L", "confirmado_por": null }
    ],
    "expectativas": [
      { "expectativa": "", "realidade": "", "registrado_em": "" }
    ],
    "questionar": [
      { "decisao_original": "", "recomendacao": "", "feature_id": null,
        "pd_antes": null, "pd_depois": null, "adotada": false }
    ],
    "alternativas": [
      { "abordagem": "", "risco_reduzido": "", "efeito_cronograma": "", "adotada": false }
    ],
    "stack": [
      { "tecnologia": "", "adequacao": "com_ressalva", "ressalva": "",
        "gera_rf": [], "fator_contexto_relacionado": null }
    ],
    "nao_usar": [
      { "item": "", "porque": "", "usar_no_lugar": "" }
    ]
  },

  "arquitetura": {
    "modulos": [{ "nome": "", "descricao": "" }],
    "decisoes_que_impactam_prazo": [{ "decisao": "", "afeta_features": [] }]
  },

  "features": [
    {
      "id": "F-01",
      "nome": "",
      "modulo": "",
      "tipo": "RF",
      "escopo": "Dentro",
      "complexidade": "M",
      "pd": 5,
      "prioridade": "Must",
      "depende_de": [],
      "viabilidade": "Viavel",
      "regras_de_negocio": [],
      "justificativa": "",
      "fonte": "",
      "confirmado_por": null
    }
  ],

  "contexto": {
    "formatos": ["web"],
    "fatores": [{ "fator": "", "valor": 0.0, "porque": "" }],
    "multiplicador_bruto": 1.0,
    "multiplicador": 1.0,
    "travas": [],
    "obrigacoes": []
  },

  "riscos": [
    { "risco": "", "probabilidade": "Alta", "impacto": "Alto",
      "mitigacao": "", "fator_buffer": null }
  ],

  "buffer": {
    "base": 0.15,
    "fatores": [{ "fator": "", "valor": 0.05, "porque": "" }],
    "fatores_pendentes": [{ "fator": "", "porque_pendente": "" }],
    "soma_bruta": 0.15,
    "total": 0.15
  },

  "blocos_fixos": {
    "discovery": 1.0,
    "infra": 1.0,
    "spikes": 0.0,
    "deploy": 0.5,
    "publicacao_lojas": 0.0,
    "qa_separado": false
  },

  "lacunas": [
    { "campo": "", "porque": "", "pergunta_para_o_cliente": "", "muda_pd": false }
  ]
}
```

### Vocabulário controlado

| Campo | Valores aceitos |
|---|---|
| `tipo` | `RF` · `RN` · `RNF` |
| `escopo` | `Dentro` · `Fora` · `A definir` |
| `complexidade` | `XS` · `S` · `M` · `L` · `XL` · `XXL` · `null` |
| `prioridade` | `Must` · `Should` · `Could` · `Wont` |
| `viabilidade` | `Viavel` · `Com ressalva` · `Inviavel` · `A avaliar` |
| `adequacao` | `adequado` · `com_ressalva` · `inadequado` |
| `probabilidade` / `impacto` | `Alta`/`Alto` · `Media`/`Medio` · `Baixa`/`Baixo` |
| `modelo_escopo` | `fechado` · `aberto` · `null` (sem venda ainda) |
| `senioridade` | `junior` · `misto` · `veterano` · `null` |
| `criticidade` | `1` · `2` · `3` · `null` |
| `porte` | `pequeno` · `medio` · `grande` · `null` |
| `nivel_detalhamento_demanda` | `prd_validado` · `documento_escrito` · `reuniao_anotada` · `conversa_solta` · `null` |
| `maturidade_tech` | `alta` · `media` · `nao_tem` · `null` |
| `formatos` | lista com `web` · `webapp_pwa` · `mobile` |

### Campos que costumam ser esquecidos

| Campo | Como preencher |
|---|---|
| `vendido.houve_venda` | `false` quando o dimensionamento precede a proposta. Nesse caso todo o bloco fica `null`, e isso não é lacuna |
| `cliente.porte` | Pequeno é até ~50 funcionários. Se não houver headcount com fonte, `null` + lacuna — o porte decide o bloco de discovery |
| `produto.criticidade` | 1 conveniência · 2 dor operacional real · 3 para a operação ou tem prazo regulatório. Nível 3 liga `blocos_fixos.qa_separado` |
| `prioridade` | MoSCoW. É a ordem de corte quando o budget não fecha e a ordem de alocação no cronograma. Sem isso a skill 2 não consegue montar sprint |
| `depende_de` | O que precisa existir antes. Alimenta a ordenação topológica do cronograma |
| `arquitetura.modulos` | Vem do agrupamento de `modulo` das features, mais o que o parecer de stack indicar |
| `blocos_fixos` | Cada um tem critério em `coeficientes.md` §6. Não são estimativa: são leitura de outro campo |
| `parecer.*.adotada` | Se a recomendação ou alternativa foi incorporada ao dimensionamento. Recomendação não adotada fica registrada mas não muda PD |
| `riscos[].fator_buffer` | O **nome** do fator de buffer que este risco aciona, ou `null`. Nome, não número — é o que permite conferir que nada foi contado duas vezes |

### Sobre `pd_antes` e `pd_depois`

São pontuação de uma alternativa que não foi implementada — não há fonte possível para elas. Preencha apenas quando as duas pontas forem classificáveis pela escala com a mesma confiança que qualquer outra feature, e registre o raciocínio em `recomendacao`. Quando não for o caso, deixe `null`: a recomendação continua valendo, só não vem com número.

### Sobre `parecer.stack[].fator_contexto_relacionado`

É uma **referência cruzada**, não um acréscimo. Se uma ressalva de stack justifica um fator do multiplicador, aponte o nome do fator aqui para rastreabilidade. O valor numérico mora em `contexto.fatores` e em lugar nenhum mais — duplicá-lo somaria 0,25 duas vezes sem que nenhuma verificação pegasse.

---

## Verificações antes de emitir

Rode todas. Cada uma corresponde a um jeito conhecido de o dimensionamento sair internamente inconsistente. Comece validando que o arquivo é JSON parseável — leitura atenta não substitui um parser.

### Integridade de referências

- Todo `feature_id` citado no parecer existe em `features`
- Todo id em `gera_rf`, `depende_de` e `afeta_features` existe em `features`
- Não há ciclo em `depende_de`
- Todo módulo em `arquitetura.modulos` tem ao menos uma feature. Módulo órfão é escopo que ninguém pontuou
- Todo `modulo` usado em `features` existe em `arquitetura.modulos`

### Coerência de classificação

- Toda feature em `mais_complexas` tem `complexidade` ∈ {L, XL, XXL}
- Toda feature com `complexidade` ∈ {L, XL, XXL} tem `confirmado_por: null`
- Toda feature em `XXL` tem entrada correspondente em `ambiguidades` com `muda_pd: true`
- Features com `tipo` ≠ `RF` têm `pd: 0` e `complexidade: null`
- Features com `tipo` = `RF` e `escopo` = `Dentro` têm `pd` batendo com `complexidade`: XS 1 · S 2 · M 5 · L 8 · XL 13 · XXL 21
- Features em `A definir` são no máximo 10% das linhas; acima disso, sinalize

### Coerência do parecer

- Toda ambiguidade com `muda_pd: true` tem `feature_id` apontando para feature em `viabilidade: "A avaliar"`
- `blocos_fixos.spikes` bate com a fórmula de `coeficientes.md` §6
- Toda expectativa em `parecer.expectativas` aparece em `produto.fora_do_escopo` ou em `lacunas`
- Toda ressalva de stack cujo texto indica construção adicional tem `gera_rf` não vazio
- Toda alternativa com `adotada: true` está refletida em `depende_de` ou em `features`

### Coerência numérica

- `contexto.multiplicador_bruto` = base do formato + soma dos `fatores`
- `contexto.multiplicador` = mínimo entre o bruto e 2,0
- `buffer.soma_bruta` = `base` + soma dos `fatores`
- `buffer.total` = mínimo entre a soma bruta e 0,40
- Todo fator em `buffer.fatores` tem exatamente um risco com `fator_buffer` apontando para ele, e vice-versa
- Nenhum fator aparece simultaneamente em `fatores` e em `fatores_pendentes`
- Nenhum valor numérico do multiplicador aparece duplicado em `parecer.stack`

### Rastreabilidade

- Toda afirmação de fato tem `fonte` no formato definido na fase 2 do SKILL.md — origem e localizador, não só "transcrição"
- Todo campo `null` que não seja opcional tem entrada correspondente em `lacunas`
- `buffer.fatores_pendentes` contém pelo menos "projeto acima de 12 sprints", que esta skill nunca consegue avaliar

---

## Resumo legível

Além do JSON, sempre entregue um resumo que o CN consiga ler sem abrir arquivo, **nesta ordem**:

1. **Lacunas** — como perguntas prontas para a próxima call, as que mudam PD primeiro
2. **Features que precisam de confirmação** — as ≥ L, nomeadas, com o porquê
3. **Travas estouradas**, se houver
4. **PD total** e distribuição por complexidade
5. **Multiplicador** com os fatores marcados listados
6. **Buffer** com fatores marcados e pendentes
7. **Decisões de maior valor no parecer** — o que foi recomendado e o que muda
8. **Fora do escopo**

A ordem é essa de propósito. Lacunas e confirmações pendentes são acionáveis hoje; os números só valem depois que alguém confirmar. Um resumo que abre com o número convida a tratá-lo como pronto.
