# Spec — Documento de Validação NTec

## Template fixo, contrato entre as duas skills, e regras de geração

> **O que este documento é:** a especificação do documento de validação que toda validação do núcleo deve produzir, campo a campo, mais o contrato de dados que liga a skill 1 à skill 2.
>
> **Base:** estrutura do Validação Projeto ZEN S.A., com o vocabulário mantido. As duas seções novas estão marcadas como **NOVA**.
>
> **Estado:** esqueleto v0.1 para discussão. Coeficientes marcados 🟡 vêm da Régua e não estão calibrados.
>
> **Nota de versão:** o schema JSON da Seção 9 é a versão de discussão. A versão vigente, com os ajustes feitos depois da revisão adversarial, está em [`dimensionar-projeto-ntec/references/contrato.md`](../dimensionar-projeto-ntec/references/contrato.md). Em caso de divergência, vale o contrato.

---

## 0. Premissas fixas

Tudo abaixo é constante do sistema. Se alguma mudar, muda a versão do template.

| Premissa | Valor | Observação |
|---|---|---|
| Duração da sprint | **15 dias, sempre** | Premissa do núcleo. Sprint de duração variável quebra a conversão PD → sprints |
| Equipe padrão | 1 AS/PM + 2 devs | |
| Dedicação | 3h/dia efetivas (faixa 2–4h) | |
| 1 PD | 1 dia-dev útil a 3h | |
| Velocidade de referência | 14 PD/sprint 🟡 | Ajuste por composição: 1 dev = 7 · veterano ×1,15 · 100% primeiro projeto ×0,75 |
| Escala | XS 1 · S 2 · M 5 · L 8 · XL 13 · XXL 21 | XXL é quebra obrigatória |
| Buffer | base 15%, +5% por fator, teto 40% | |
| Multiplicador | teto 2,0 | Incide só sobre PD de desenvolvimento |
| ITIP alvo | 1200 · piso 900 | 1 sprint = ITIP × 3 consultores × 2 semanas |

**Regra de conversão de cronogramas legados:** sprint de 3 semanas em documento antigo conta como 1,5 sprint. Não se cria sprint de duração diferente.

---

## 1. Cabeçalho

Campos obrigatórios. Campo sem valor recebe `N/A — motivo`, nunca fica vazio.

| Campo | Tipo | Origem |
|---|---|---|
| Projeto | F | CN |
| Cliente (razão social) | F | CN |
| Responsável do cliente (nome + cargo) | F | Transcrição |
| CN responsável | F | — |
| Validador | F | — |
| Data da validação | F | — |
| Prazo sinalizado ao cliente | F | Comercial. **É o número que o cliente ouviu** |
| Investimento fechado | F | Proposta. Valor + parcelamento |
| Modelo de escopo | C | Fechado / Aberto |
| Hospedagem e infraestrutura | F | Inclui handoff ao final, se houver |
| Equipe prevista | F | Composição e senioridade |
| **Versão da Régua** | F | Carimbo |
| **Velocidade usada** | F | Carimbo. PD/sprint aplicado |
| **ITIP de referência** | F | Carimbo |

Os três carimbos existem para que, quando a velocidade for recalibrada, seja possível saber qual documento saiu de qual régua.

---

## 2. Parecer de consultoria

Estrutura do ZEN mantida. O que muda é que cada item passa a declarar seu efeito numérico.

### 2.1 Pontos mal definidos ou ambíguos

Por item: `{descrição, quem resolve, o que trava se não resolver, muda_PD}`

**A distinção que o ZEN não faz:** hoje todos os itens de 1.1 têm o mesmo peso visual. Mas "volume real de usuários de apontamento" e "grau de rigor jurídico da elegibilidade fiscal" custam coisas muito diferentes.

- `muda_PD = true` → a feature correspondente vai para viabilidade **"A avaliar"** → **spike obrigatório de 0,5 sprint**
- `muda_PD = false` → vai direto para a Seção 7 (Pendências), sem custo de cronograma

### 2.2 Funcionalidades mais complexas do que parecem para o nível da equipe

Por item: `{feature_id, por que é mais complexa, complexidade atribuída, confirmado_por}`

Regras:
- Todo item listado aqui é no mínimo **L**
- Todo item aqui exige **quatro olhos** — validador + dev da stack. `confirmado_por` é obrigatório e sai da skill sempre `null`
- Todo item aqui tem de existir como linha na Seção 3

### 2.3 Expectativas do cliente possivelmente fora da realidade

Por item: `{expectativa, realidade, onde está por escrito}`

Regra: toda expectativa listada tem de aparecer em **"Explicitamente fora do escopo"** (Seção 3) ou em **Pendências** com ação e prazo. Expectativa registrada só no parecer não protege ninguém.

### 2.4 Decisões técnicas e de produto a questionar

Por item: `{decisão original, recomendação, PD_antes, PD_depois, delta_PD}`

**Esta é a seção de maior valor do parecer e hoje ela não mostra o que economiza.** No ZEN, "motor de regra fiscal genérico → hardcode por programa, generalizar depois" é provavelmente a diferença entre XL (13 PD) e M (5 PD). Oito PD é mais de meia sprint, e isso não aparece em lugar nenhum.

### 2.5 Abordagens alternativas para reduzir risco

Por item: `{abordagem, risco que reduz, efeito no cronograma}`

Regra: se a abordagem altera a ordem de entrega (ex.: modularizar por perfil), ela altera `depende_de` na Seção 3. O cronograma tem de refletir a alternativa escolhida, não a original.

### 2.6 Adequação de stack e bibliotecas

Por tecnologia: `{tecnologia, adequação, ressalva, gera_RF, fator_contexto_relacionado}`

**Regra que o ZEN não tem e precisa ter:** ressalva que exige construir algo por cima vira **RF própria na Seção 3**, não fica só como nota.

No ZEN: *"RBAC granular não vem pronto no BetterAuth — precisa ser construído por cima da lib"*. Isso é trabalho real, provavelmente L ou XL, e não está pontuado em lugar nenhum do documento. É o tipo exato de PD que some e reaparece como hora não paga.

---

## 3. Dimensionamento — **NOVA**

A memória de cálculo. Sem ela, o número do cronograma não é auditável.

### 3.1 Tabela de features

| Coluna | Valores | Regra |
|---|---|---|
| `id` | F-01, F-02… | Estável, referenciado pelo parecer e pelo cronograma |
| `nome` | texto | Uma frase. Se não cabe em uma frase, são duas features |
| `modulo` | texto | Agrupa. Bate com a árvore da Seção 5.3 |
| `tipo` | RF / RN / RNF | **Só RF pontua** |
| `escopo` | Dentro / Fora / A definir | Só "Dentro" entra na soma |
| `complexidade` | XS…XXL | `null` se não há evidência para classificar |
| `pd` | derivado | 1 / 2 / 5 / 8 / 13 / 21 |
| `prioridade` | Must / Should / Could / Wont | Ordem de corte e de alocação |
| `depende_de` | [ids] | Alimenta a ordenação do cronograma |
| `viabilidade` | Viável / Com ressalva / Inviável / A avaliar | "A avaliar" → spike 0,5 sprint |
| `fonte` | timestamp, tela, arquivo | Obrigatório |
| `confirmado_por` | nome ou `null` | Obrigatório preenchido se complexidade ≥ L |

**Destino de RN e RNF** (entram no inventário com `pd: 0`, não pontuam):

| Tipo | Vai para |
|---|---|
| RN — regra de negócio | Regra dentro da RF que ela afeta. 3+ RN não triviais numa RF → sobe um degrau |
| RNF segurança/auth/perfis | Bloco fixo de infra |
| RNF performance/volume | Multiplicador |
| RNF disponibilidade/deploy | Bloco fixo de deploy |
| RNF usabilidade/visual | Distribuído nas RF |
| RNF auditoria/log | Simples: embutido nas RF de escrita. Com encadeamento: vira RF própria em L ou XL |

### 3.2 Fechamento do cálculo

```
PD_dev        = Σ pd das RF com escopo = "Dentro"
multiplicador = 1,00 (web) + Σ fatores marcados        (teto 2,0)
PD_ajustado   = PD_dev × multiplicador
Sprints_dev   = teto(PD_ajustado ÷ velocidade)
Sprints_total = discovery + infra + spikes + Sprints_dev + teste + deploy
Semanas_vend  = Sprints_total × 2 × (1 + buffer)
Preço         = ITIP × consultores × Semanas_vend
```

Fatores de multiplicador marcados devem ser listados, não só somados.

---

## 4. Matriz de riscos

Colunas do ZEN mais uma. A coluna nova é o que liga a matriz ao número.

| Risco | Probabilidade | Impacto | Mitigação | **Efeito no buffer** |
|---|---|---|---|---|

Regras:

- `Efeito no buffer` ∈ {`+5%`, `—`}. Buffer final = 15% + Σ dos +5%, teto 40%
- Risco **Alta/Alto sem mitigação executável** bloqueia a validação
- Mitigação que diz "aplicar buffer" sem o buffer estar na conta final é inválida

**Por que esta coluna existe.** No ZEN a matriz identifica *"Prazo de 4-5 meses insuficiente mesmo para o MVP — Alta/Alto — mitigação: buffer de 20-30%"*, e o cronograma da Seção 4 mostra 21 semanas **sem buffer**. A tabela vira plano de projeto; a ressalva em prosa embaixo dela não vira nada. O documento sabia a resposta certa e apresentou a errada como manchete.

Fatores de buffer disponíveis (da Régua):

- [ ] Multiplicador acima de 1,3
- [ ] Duas ou mais integrações, ou qualquer integração sem documentação
- [ ] Feature atípica sem benchmark
- [ ] Terceiro no caminho crítico
- [ ] Equipe majoritariamente trainee, ou troca programada
- [ ] Cliente com múltiplos times de aprovação ou autoridade não identificada
- [ ] Projeto acima de 12 sprints
- [ ] Setor atípico ou regulado

---

## 5. Arquitetura e stack

Seção 3 do ZEN, mantida quase intacta. É a parte que já funciona.

- **5.1 Stack tecnológica** — por camada, com justificativa de uma linha
- **5.2 O que NÃO usar nesse contexto** — item, por quê, e o que usar no lugar. *Mantida como está: é barata de escrever e impede equipe júnior de superengenheirar*
- **5.3 Arquitetura lógica** — árvore de módulos e coleções
- **5.4 Decisões técnicas críticas que impactam prazo** — cada decisão vira `depende_de` na Seção 3

**Regra de integridade:** todo módulo da árvore em 5.3 precisa ter ao menos uma feature na Seção 3. Módulo órfão é escopo não dimensionado.

---

## 6. Cronograma vendido

| Sprint | Período | Objetivo | Features (ids) | PD | Entregáveis | Responsável principal |
|---|---|---|---|---|---|---|

### Regras de alocação — determinísticas, sem inferência

1. Sprint = 15 dias. Sempre.
2. **Sprint 0** = refino, discovery, setup e acessos. Duração pelo nível de detalhamento da demanda: PRD validado 0,5 · padrão 1 · 5+ fluxos críticos 1,5 · demanda solta 2
3. **Infra e auth** vêm antes de qualquer módulo funcional. 1 nível de acesso 0,5 · 2–6 níveis 1 · 6+ ou multitenancy 1,5–2
4. **Spikes** logo após, um por item "A avaliar"
5. **Features de dev:** ordenação topológica por `depende_de`. Dentro do mesmo nível, ordem MoSCoW (Must → Should → Could). Empate resolve por PD decrescente, e o id como desempate final
6. **Empacotamento guloso** até a capacidade da sprint (= velocidade)
7. Feature maior que a capacidade ocupa a sprint sozinha e a estoura — **visível de propósito**
8. **Teste e deploy** nas últimas sprints. Criticidade 3 proíbe combinar QA e UAT
9. **Margem contratada:** as sprints compradas pelo buffer aparecem ao final como linhas próprias, marcadas como margem, sem features alocadas

A regra 9 é uma escolha: o cliente vê a data que está comprando e a equipe vê que margem é margem, não trabalho. A alternativa — diluir o buffer nas sprints — esconde a margem e ela é consumida sem ninguém perceber.

Implementação em [`documento-validacao-ntec/scripts/calcular.py`](../documento-validacao-ntec/scripts/calcular.py); o raciocínio por trás de cada regra está em [`references/algoritmo.md`](../documento-validacao-ntec/references/algoritmo.md).

---

## 7. Delta: vendido versus dimensionado — **NOVA**

A seção que justifica a skill. Hoje ela existe espalhada — no rodapé do cronograma e na última pendência — e por isso não obriga ninguém a nada.

### 7.1 O quadro

| | Vendido | Dimensionado | Delta |
|---|---|---|---|
| Sprints | | | |
| Semanas | | | |
| PD | — | | — |
| Preço | | ITIP alvo × equipe × semanas dimensionadas | |
| ITIP implícito | preço ÷ semanas vendidas ÷ equipe | preço ÷ semanas dimensionadas ÷ equipe | |

A linha de ITIP implícito é a que traduz o atraso em dinheiro. No ZEN: R$ 1.479 no cronograma apresentado, R$ 1.195 no prazo que o próprio documento admite ser real, R$ 1.071 com o buffer cheio. O preço não estava errado — ele só valia no prazo que não vai acontecer.

### 7.2 A escolha de recurso

Se `delta > 0`, **exatamente uma** opção precisa estar marcada e preenchida:

| Opção | O que registrar |
|---|---|
| **Cortar escopo** | ids das features cortadas, PD removido, quem aprovou |
| **Negociar sprints adicionais** | quantas, com quem, status da conversa |
| **Consumir margem** | quanto da margem, quanto sobra, limiar por sprint |
| **Aceitar o risco** | nome de quem aceitou e o que acontece se estourar |

> **Gate:** `delta > 0` sem opção marcada → **a validação não fecha.**
>
> Esta é a trava que protege a equipe de projetos. Sem ela, a saída default é a quinta opção — a equipe absorve e ninguém registra.

---

## 8. Pendências em aberto

| Pendência | Quem resolve | Até quando | O que trava | Muda PD? |
|---|---|---|---|---|

`Muda PD = sim` é o que separa pendência de bloqueio: ela tem spike alocado na Seção 6 e não pode ser resolvida "durante a imersão".

---

## 9. O contrato entre as skills

Artefato intermediário. A skill 1 escreve, a skill 2 lê. É o que permite as duas evoluírem de forma independente.

O schema vigente está em [`dimensionar-projeto-ntec/references/contrato.md`](../dimensionar-projeto-ntec/references/contrato.md), com vocabulário controlado e verificações de integridade. Diferenças em relação à versão de discussão, todas vindas da revisão adversarial:

- `multiplicador_bruto` e `buffer.soma_bruta` passaram a existir ao lado dos valores limitados — guardar só o truncado apagaria o sinal que dispara o gate de escopo aberto
- `buffer.fatores_pendentes` foi criado para os fatores que a skill 1 não consegue avaliar, eliminando uma dependência circular
- `efeito_multiplicador` em `parecer.stack` virou `fator_contexto_relacionado`, uma referência por nome — o campo numérico duplicava 0,25 silenciosamente
- `vendido.houve_venda` foi acrescentado, porque o dimensionamento também acontece antes da proposta
- `velocidade_pd_sprint` virou `velocidade_base_pd_sprint`, e o ajuste por composição passou a ser aplicado só pela skill 2

**Nada de `Sprints_total`, `Semanas_vend` ou `Preço` no JSON:** são derivados, e quem deriva é a skill 2. Guardar resultado calculado no contrato abre espaço para os dois lados discordarem.

---

## 10. Regras de recusa — skill 1

O que separa a skill do mega prompt. A Seção 0 da Régua registra que o prompt gigante *"alucina justamente onde o critério falta"* — estas regras são a defesa.

| Situação | Comportamento obrigatório |
|---|---|
| Fato sem fonte na transcrição, protótipo ou notas | `null` + entrada em `lacunas`. **Nunca inferir valor plausível** |
| Feature mencionada sem detalhe para classificar | `complexidade: null`, `viabilidade: "A avaliar"`, entra em 2.1 |
| Prazo ou preço não ditos explicitamente | `null`. A skill **não estima o que foi vendido** |
| Complexidade ≥ L | `confirmado_por: null` sempre. A skill propõe, humano confirma |
| Contradição entre fontes da mesma época | Registra as duas com suas fontes e abre lacuna. Não escolhe |
| Cliente descreve dor sem descrever solução | Vai para o parecer, **não vira feature** |
| Fator com evidência parcial | Não marca e abre lacuna nomeando o fator |

Regra geral: **lacuna é entregável, não falha.** A lista de `lacunas` é a pauta da próxima call do CN e vale mais que um campo preenchido por adivinhação.

---

## 11. Testes de aceitação

O que precisa passar antes de qualquer uso real. **Nenhum foi executado até aqui** — o ambiente de desenvolvimento não permitiu rodar o script.

**Skill 2 — determinismo**
- Duas execuções com o mesmo JSON produzem cronogramas idênticos, linha a linha
- Trocar a ordem das features no JSON de entrada não muda a alocação
- Mudar a velocidade muda o número de sprints de forma monotônica

**Skill 1 — recusa**
- Transcrição com lacuna deliberada produz `null` + entrada em `lacunas`, e não um valor plausível
- Toda feature ≥ L sai com `confirmado_por: null`
- Nenhuma afirmação de fato sai sem `fonte`

**Integridade do documento**
- Módulo em 5.3 sem feature na Seção 3 é detectado
- Σ `pd` das RF "Dentro" confere com `PD_dev`
- `delta > 0` sem opção de recurso marcada impede o fechamento
- Item em 2.2 sem linha correspondente na Seção 3 é detectado

**Regressão contra o ZEN**
Rodar a skill 1 sobre o material bruto do ZEN e comparar com o documento existente. Não se espera igualdade — espera-se que o parecer cubra os mesmos pontos e que o dimensionamento exponha o que faltava: o RBAC custom sobre o BetterAuth, o PD poupado pelo hardcode das regras fiscais, e o buffer dentro do número em vez de embaixo dele.

---

## 12. O que este spec deliberadamente não resolve

- **Escopo aberto.** O template assume escopo fechado. Escopo aberto precisa de cronograma das primeiras seis sprints por outra lógica
- **A velocidade.** 14 PD/sprint segue sendo chute. O template carimba qual foi usada para que a recalibração seja rastreável, e só
- **Distribuição de PD por macroetapa.** A alocação é gulosa por dependência e prioridade, não otimizada por módulo
- **Se a validação deveria mesmo acontecer depois da venda.** O template torna o delta visível; não muda a ordem comercial que o produz
